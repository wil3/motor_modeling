from record_data import MSP
from msp_protocol import *
import argparse
import threading
from test_rig import test_rig
import time
import csv
import signal


# Store all sensor data here.
# Format:
# <Timestamp> <Thrust> <Left Torque> <Right Torque> <RPM>
sensor_data = []
go = threading.Event()

board = None
running = False

def abort(signal, frame):
    print ("ABBOOORRRRTTTTT!!!!!!!!!")
    global board
    global running
    board.running = False
    running = False

def send_motor(board, motor, port, duration, mode):
    #board = None
    try:
        
        board.connect()
        board.running = True
        go.set() # Activate the event flag to start data collection on time

        if (mode != 'step'):
            board.ramp(motor, 1000, 1100, duration/2)
            #time.sleep(1)
            board.ramp(motor, 1100, 1000, duration/2)
        else:
            board.set(motor, 1000)
            time.sleep(duration / 2)
            board.set(motor, 1000)
            time.sleep(duration / 2)

    except Exception as e:
        print ("Exception ", e)
        if board:
            # Stop spinning
            cmd = [MSP.MOTOR_MIN]*8
            board.sendCMD(16, MSP_SET_MOTOR, cmd)
            board.close()

def get_data(board, port, duration):

    global running
    running = True
    test = test_rig(port)
    test.read() # Primes the system
    
    go.wait() # Wait until the Tinyhawk wakes up

    start_time = time.time()
    while (time.time() - start_time <= duration + 3) and running:
        read_line = test.read()

        if (read_line != None): 
            read_line.insert(0, time.time() - start_time)
        read_line.insert(1, board.current_ramp_motor_value)
        sensor_data.append(read_line)
        print("Sensors: ", read_line)
    
def main(args):
    signal.signal(signal.SIGINT, abort)

    global board
    board = MSP(args.port_send)

    get_data_thread = threading.Thread(target=get_data, args = (board, args.port_receive, args.duration))
    get_data_thread.start()

    send_motor_thread = threading.Thread(target=send_motor, args = (board, args.motor, args.port_send, args.duration, args.mode))
    send_motor_thread.start()
    send_motor_thread.join()

    get_data_thread.join()

    #have each thread save into memory a global array all data collecting add a timetamp merge in that way
    
    with open(args.filename, "a", newline='') as f:
        writer = csv.writer(f)
        for z in sensor_data:
            if (z != None):
                writer.writerow(z)

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Capture motor data")
    parser.add_argument('--port-send', help="", default="/dev/ttyACM0")
    parser.add_argument('--port-receive', help="", default="/dev/ttyACM0")
    parser.add_argument('--motor', help="motor ID starts at 0", type=int)
    parser.add_argument('--duration', help="", default=1, type=float)
    parser.add_argument('--filename', help="", default="data.csv")
    parser.add_argument('--mode', help="", default="")

    args = parser.parse_args()
    main(args)
    