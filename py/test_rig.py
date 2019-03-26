import serial
import csv
import sys

class test_rig:

    #
    # Global Class Variables
    #
    CAL_THRUST_CONST = 1
    CAL_LEFT_CONST = 1
    CAL_RIGHT_CONST = 1

    NUM_SAMPLES = 100 # Change this to change the number of samples to take when calibrating

    thrust = 0
    leftTorque = 0
    rightTorque = 0


    #
    # Constructor
    #
    def __init__(self, dstAddress):
        self.ser = serial.Serial(dstAddress)
        self.ser.flushInput()

    #
    # Methods
    #
    def read(self):

        try:
            serialLine = self.ser.readline()
            decodedLine = serialLine.decode("utf-8").split()

            if len(decodedLine) == 3:
                self.thrust = decodedLine[0]
                self.leftTorque = decodedLine[1]
                self.rightTorque = decodedLine[2]

            return [rig.thrust, rig.leftTorque, rig.rightTorque]

        except Exception as e:
            print(e)


if __name__ == "__main__":

    rig = test_rig('COM1')
    rig.read() # prime the system

    if (sys.argv[1] == '-t'): # Calibrate Torque
        print("----- Calibrating Torque -----")

        leverLength = 0.1305 # 130.5 mm
        weight = 0
        samples = [0] * 100

        print("Activating Right Load Cell")
        for z in range(4):
            print("Set weight to", weight, "g. Press [Enter] when ready.", sep=" ")
            input()

            print("Collecting data...", end='')
            s = 0
            rig.ser.reset_input_buffer()
            while s < rig.NUM_SAMPLES:
                samples[s] = float(rig.read()[2])
                s += 1
                print("Sample #", s)


            with open("increase.csv", "a") as f:
                writer = csv.writer(f)
                writer.writerow([sum(samples)/len(samples)])

            print("Done.")
            weight = weight + 200

        for z in range(5):
            print("Set weight to", weight, "g. Press [Enter] when ready.", sep=" ")
            input()

            print("Collecting data", end='')
            s = 0
            rig.ser.reset_input_buffer()
            while s < rig.NUM_SAMPLES:
                samples[s] = float(rig.read()[2])
                s += 1
                print("Sample #", s)


            with open("decrease.csv", "a") as f:
                writer = csv.writer(f)
                writer.writerow([sum(samples)/len(samples)])

            print("Done.")
            weight = weight - 200



        
        