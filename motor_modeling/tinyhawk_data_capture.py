from record_data import MSP
from msp_protocol import *
import argparse
import threading
from test_rig import test_rig
import time
import csv

# Store all sensor data here.
# Format:
# <Timestamp> <Thrust> <Left Torque> <Right Torque> <RPM>
sensor_data = []
go = threading.Event()
 
def send_motor(port, duration):
    board = None
    try:
        board = MSP(port)
        board.connect()

        go.set() # Activate the event flag to start data collection on time

        board.ramp(1, 1000, 2000, duration/2)
        time.sleep(1)
        board.ramp(1, 2000, 1000, duration/2)
    except Exception as e:
        print ("Exception ", e)
        if board:
            # Stop spinning
            cmd = [MSP.MOTOR_MIN]*8
            board.sendCMD(16, MSP_SET_MOTOR, cmd)
            board.close()

def get_data(port, duration):

    test = test_rig(port)
    test.read() # Primes the system
    
   # go.wait() # Wait until the Tinyhawk wakes up

    start_time = time.time()
    while (time.time() - start_time <= duration + 3):
        read_line = test.read()

        if (read_line != None): 
            read_line.insert(0, time.time() - start_time)

        sensor_data.append(read_line)
        print("Sensors: ", read_line)
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Capture motor data")
    parser.add_argument('--port-send', help="", default="/dev/ttyACM0")
    parser.add_argument('--port-receive', help="", default="/dev/ttyACM0")
    parser.add_argument('--duration', help="", default=1, type=float)
    parser.add_argument('--filename', help="", default="data.csv")
    parser.add_argument('--mode', help="", default="")

    args = parser.parse_args()

    get_data_thread = threading.Thread(target=get_data, args = (args.port_receive, args.duration))
    get_data_thread.start()

    if (args.mode != "rapid"):
        send_motor_thread = threading.Thread(target=send_motor, args = (args.port_send, args.duration))
        send_motor_thread.start()
        send_motor_thread.join()

    get_data_thread.join()

    #have each thread save into memory a global array all data collecting add a timetamp merge in that way
    
    with open(args.filename, "a", newline='') as f:
        writer = csv.writer(f)
        for z in sensor_data:
            if (z != None):
                writer.writerow(z)
