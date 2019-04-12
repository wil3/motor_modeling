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

        self.thrust = 0
        self.leftTorque = 0
        self.rightTorque = 0
        self.rpm = 0

    #
    # Methods
    #
    def read(self):

        try:
            serialLine = self.ser.readline()
            decodedLine = serialLine.decode("utf-8").split()
            #print("decodedLine ", decodedLine)

            if len(decodedLine) == 5:

                self.thrust = (float(decodedLine[0]) + 41.7) / 89300

                self.leftTorque = (float(decodedLine[1]) + 6340) / -2560000

                self.rightTorque = (float(decodedLine[2]) + 3580) / 2860000

                self.rpm = float(decodedLine[4])

            return [self.thrust, self.leftTorque, self.rightTorque, self.rpm]

        except Exception as e:
            print(e)

"""

if __name__ == "__main__":

    rig = test_rig('COM1')
    rig.read() # prime the system

    if (sys.argv[1] == 'torque'): # Calibrate Torque
        print("----- Calibrating Torque -----")

        leverLength = 0.1305 # 130.5 mm
        weight = 0
        samples = [0] * 100

        # ----- Right Load Cell Calibration ------ #

#        print("Activating Right Load Cell")
#        for z in range(5):
#            weight += float(input("Input the mass (g) you are currently ADDING. Press [Enter] when ready."))
#
#            print("Collecting data...", end='')
#            s = 0
#            rig.ser.reset_input_buffer()
#            while s < rig.NUM_SAMPLES:
#                samples[s] = float(rig.read()[2])
#                s += 1
#                print("Sample #", s)
#
#
#            with open("right.csv", "a") as f:
#                writer = csv.writer(f)
#                writer.writerow([leverLength * (9.8 * weight / 1000), sum(samples)/len(samples)]) # Should be <Torque, load cell reading>
#
#            print("Done.")
#
#        for z in range(5):
#            weight -= float(input("Input the mass (g) you are currently REMOVING. Press [Enter] when ready."))
#
#            print("Collecting data", end='')
#            s = 0
#            rig.ser.reset_input_buffer()
#            while s < rig.NUM_SAMPLES:
#                samples[s] = float(rig.read()[2])
#                s += 1
#                print("Sample #", s)
#
#
#            with open("right.csv", "a") as f:
#                writer = csv.writer(f)
#                writer.writerow([leverLength * (9.8 * weight / 1000), sum(samples)/len(samples)]) # Should be <Torque, load cell reading>
#
#            print("Done.")

        # ----- Left Load Cell Calibration ------ #

        print("Activating Left Load Cell")
        for z in range(5):
            weight += float(input("Input the mass you are currently ADDING. Press [Enter] when ready."))

            print("Collecting data...", end='')
            s = 0
            rig.ser.reset_input_buffer()
            while s < rig.NUM_SAMPLES:
                samples[s] = float(rig.read()[1])
                s += 1
                print("Sample #", s)


            with open("left.csv", "a") as f:
                writer = csv.writer(f)
                writer.writerow([leverLength * (9.8 * weight / 1000), sum(samples)/len(samples)])

            print("Done.")

        for z in range(5):
            weight -= float(input("Input the mass you are currently REMOVING. Press [Enter] when ready."))

            print("Collecting data", end='')
            s = 0
            rig.ser.reset_input_buffer()
            while s < rig.NUM_SAMPLES:
                samples[s] = float(rig.read()[1])
                s += 1
                print("Sample #", s)


            with open("left.csv", "a") as f:
                writer = csv.writer(f)
                writer.writerow([leverLength * (9.8 * weight / 1000), sum(samples)/len(samples)])

            print("Done.")

    elif (sys.argv[1] == 'thrust'):

        weight = 0
        samples = [0] * 100

        print("Activating Thrust Load Cell")
        for z in range(5):
            weight += float(input("Input the mass you are currently ADDING. Press [Enter] when ready."))

            print("Collecting data...", end='')
            s = 0
            rig.ser.reset_input_buffer()
            while s < rig.NUM_SAMPLES:
                samples[s] = float(rig.read()[0])
                s += 1
                print("Sample #", s)


            with open("thrust.csv", "a") as f:
                writer = csv.writer(f)
                writer.writerow([9.8 * weight / 1000, sum(samples)/len(samples)]) # <Force, load cell reading>

            print("Done.")

        for z in range(5):
            weight -= float(input("Input the mass you are currently REMOVING. Press [Enter] when ready."))

            print("Collecting data", end='')
            s = 0
            rig.ser.reset_input_buffer()
            while s < rig.NUM_SAMPLES:
                samples[s] = float(rig.read()[0])
                s += 1
                print("Sample #", s)


            with open("thrust.csv", "a") as f:
                writer = csv.writer(f)
                writer.writerow([9.8 * weight / 1000, sum(samples)/len(samples)])  # <Force, load cell reading>

            print("Done.")

"""
        