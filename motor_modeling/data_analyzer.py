import csv
import matplotlib.pyplot as p
import numpy as np
import math
import argparse

parser = argparse.ArgumentParser("Analyze motor data")
parser.add_argument('--filename', help="", default="data.csv")
args = parser.parse_args()

maximums = [] # Thrust LeftT RightT RPM

time, thrust, leftT, rightT, rpm = np.loadtxt(args.filename, delimiter=',', unpack=True)

# Plot construction
figgy = p.figure()
thrustPlot = figgy.add_subplot(221)
rpmPlot = figgy.add_subplot(222)
leftTPlot = figgy.add_subplot(223)
rightTPlot = figgy.add_subplot(224)

thrustPlot.scatter(time, thrust, s=1)
thrustPlot.set_xlabel('Time (s)')
thrustPlot.set_ylabel('Thrust (N)')

rpmPlot.scatter(time, rpm, s=1)
rpmPlot.set_xlabel('Time (s)')
rpmPlot.set_ylabel('Rotations Per Minute (RPM)')

leftTPlot.scatter(time, leftT, s=1)
leftTPlot.set_xlabel('Time (s)')
leftTPlot.set_ylabel('Torque (N-m)')

rightTPlot.scatter(time, rightT, s=1)
rightTPlot.set_xlabel('Time (s)')
rightTPlot.set_ylabel('Torque (N-m)')

###############################################################################

# Max Thrust
print('Computing max thrust...')
indexList = np.where(thrust == np.amax(thrust))
print(indexList)

maxThrust = int(np.median(indexList))
maximums.append(thrust[maxThrust])

print(maxThrust)
thrustPlot.scatter(time[maxThrust], thrust[maxThrust], s=2, c='red')
thrustPlot.annotate(thrust[maxThrust], (time[maxThrust], thrust[maxThrust]), textcoords='offset pixels', xytext=(5, 5))

###############################################################################

# Max Left Torque
print('Computing max left torque...')
absoluteLeftT = np.absolute(leftT)
indexList = np.where(absoluteLeftT == np.amax(absoluteLeftT))
print(indexList)

maxLeftT = int(np.median(indexList))
maximums.append(leftT[maxLeftT])

print(maxLeftT)
leftTPlot.scatter(time[maxLeftT], leftT[maxLeftT], s=2, c='red')
leftTPlot.annotate(leftT[maxLeftT], (time[maxLeftT], leftT[maxLeftT]), textcoords='offset pixels', xytext=(5, 5))

###############################################################################

# Max Right Torque
print('Computing max right torque...')
absoluteRightT = np.absolute(rightT)
indexList = np.where(absoluteRightT == np.amax(absoluteRightT))
print(indexList)

maxRightT = int(np.median(indexList))
maximums.append(rightT[maxRightT])

print(maxRightT)
rightTPlot.scatter(time[maxRightT], rightT[maxRightT], s=2, c='red')
rightTPlot.annotate(rightT[maxRightT], (time[maxRightT], rightT[maxRightT]), textcoords='offset pixels', xytext=(5, 5))

###############################################################################

# Max RPM
print('Computing max RPM...')
indexList = np.where(rpm == np.amax(rpm))
print(indexList)

maxRPM = int(np.median(indexList))
maximums.append(rpm[maxRPM])

print(maxThrust)
rpmPlot.scatter(time[maxRPM], rpm[maxRPM], s=2, c='red')
rpmPlot.annotate(rpm[maxRPM], (time[maxRPM], rpm[maxRPM]), textcoords='offset pixels', xytext=(5, 5))


# Calculate motor constants
dummyDiameter = 40 / 1000 # setup an argparser thing to get the diameter from the command line.

motor_constant_ = maximums[0] / (4 * math.pi * maximums[3] ** 2)
moment_constant_ = dummyDiameter * maximums[0] / maximums[2]

consts = 'motor_constant_: {} | moment_constant_: {}'.format(motor_constant_, moment_constant_)
print('Constants:')
print(consts)  

p.figtext(0.5, 0.01, consts, va='bottom', ha='center')

p.show()
