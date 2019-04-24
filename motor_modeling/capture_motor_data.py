from msp_interface import MSP
from msp_protocol import *
import argparse
import threading
from arduino_interface import ArduinoInterface 
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
    global running
    try:
        
        board.connect()
        board.running = True
        go.set() # Activate the event flag to start data collection on time
        time.sleep(1)

        if (mode != 'step'):
            board.ramp(motor, 1000, 2000, duration/2)
            #time.sleep(1)
            board.ramp(motor, 2000, 1000, duration/2)
        else:
            board.set(motor, 2000)
            time.sleep(0.5)
            board.set(motor, 1000)
            #board.ramp(motor, 2000, 1000, duration)

        time.sleep(5)
        board.running = False
        running = False
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
    arduino = ArduinoInterface(port)
    arduino.read() # Primes the system
    
    go.wait() # Wait until the Tinyhawk wakes up

    start_time = time.time()
    #while (time.time() - start_time <= duration + 3) and running:
    while running:
        read_line = arduino.read()

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
    
    with open(args.filepath, "w", newline='') as f:
        writer = csv.writer(f)
        for z in sensor_data:
            if (z != None):
                writer.writerow(z)

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Capture motor data")
    parser.add_argument('--port-send', help="The port connected to the aircraft FC.", default="/dev/ttyACM0")
    parser.add_argument('--port-receive', help="The port connected to the Arduino", default="/dev/ttyACM0")
    parser.add_argument('--motor', help="The motor ID, starts at 0", type=int)
    parser.add_argument('--duration', help="The total duration to perform the experiment. NOTE there is a minimum delay of 0.01 seconds between motor commands which must be taken into accourt when computing duration.", default=10, type=float)
    parser.add_argument('--filepath', help="The absolute path to the file to log the data", default="data.csv")
    parser.add_argument('--mode', help="One of 'step' or 'ramp'. Ramp will ramp the given motor from zero to full throttle for duration/2 and then full throttle to zero for duration/2. Step will immediately apply motor input to full throttle (2000) and then ramp drown to zero for duration/2", default="")

    args = parser.parse_args()
    main(args)
    