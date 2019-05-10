import csv
import matplotlib.pyplot as plt
import numpy as np
import math
import argparse

def main():
    # Always show thrust as positive
    # XXX Make note, this should be find but then cant capture negative trhstu
    thrust = np.abs(thrust)
    rThrust = np.abs(rThrust)

    p.plot(time[1:], (np.absolute(leftT)/thrust)[1:])
    p.show()

    print ("Time len=", len(rTime))
    print ("Thrust len=", len(rThrust))

    rcommand[rcommand == 0.0] = 1000
    fig, ax1 = p.subplots()
    ax1.plot(rTime, rThrust)
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel('Thrust (N)')
    color = 'r'
    label = "PWM Motor Signal (µs)"
    ax_command = ax1.twinx()
    ax_command.plot(rTime, rcommand, color=color)
    ax_command.set_ylabel(label, color=color)
    ax_command.tick_params(axis='y', labelcolor=color)

    if args.show_plot:
        fig.show()



    # Plot construction
    fig = p.figure()

    ax_thrust = fig.add_subplot(221)
    ax_rpm = fig.add_subplot(222)
    ax_left_torque = fig.add_subplot(223)
    ax_right_torque = fig.add_subplot(224)


    fig.tight_layout(pad=1, w_pad=1.5, h_pad=1.0)

    ax_thrust.scatter(time, thrust, s=1)
    ax_thrust.set_xlabel('Time (s)')
    ax_thrust.set_ylabel('Thrust (N)')



    ax_rpm.scatter(time, rpm, s=1)
    ax_rpm.set_xlabel('Time (s)')
    ax_rpm.set_ylabel('Rotations Per Minute (RPM)')

    ax_left_torque.scatter(time, leftT, s=1)
    ax_left_torque.set_xlabel('Time (s)')
    ax_left_torque.set_ylabel('Torque (N-m)')

    ax_right_torque.scatter(time, rightT, s=1)
    ax_right_torque.set_xlabel('Time (s)')
    ax_right_torque.set_ylabel('Torque (N-m)')

    # Add command to everything
    color = 'r'
    label = "PWM Motor Signal (µs)"
    ax_command = ax_thrust.twinx()
    ax_command.plot(time, command, color=color)
    ax_command.set_ylabel(label, color=color)
    ax_command.tick_params(axis='y', labelcolor=color)

    ax_command = ax_rpm.twinx()
    ax_command.plot(time, command, color=color)
    ax_command.set_ylabel(label, color=color)
    ax_command.tick_params(axis='y', labelcolor=color)

    ax_command = ax_left_torque.twinx()
    ax_command.plot(time, command, color=color)
    ax_command.set_ylabel(label, color=color)
    ax_command.tick_params(axis='y', labelcolor=color)

    ax_command = ax_right_torque.twinx()
    ax_command.plot(time, command, color=color)
    ax_command.set_ylabel(label, color=color)
    ax_command.tick_params(axis='y', labelcolor=color)

    ###############################################################################

    # Max Thrust
    absoluteThrust = np.absolute(thrust)
    indexList = np.where(absoluteThrust == np.amax(absoluteThrust))

    max_thrust_index = int(np.median(indexList))
    max_thrust = thrust[max_thrust_index]

    #print('Maximum Thrust: ', max_thrust)
    #ax_thrust.scatter(time[maxThrust], thrust[maxThrust], s=2, c='red')
    #ax_thrust.annotate(thrust[maxThrust], (time[maxThrust], thrust[maxThrust]), textcoords='offset pixels', xytext=(5, 5))

    ###############################################################################

    # Max Left Torque
    absoluteLeftT = np.absolute(leftT)
    indexList = np.where(absoluteLeftT == np.amax(absoluteLeftT))

    maxLeftT_index = int(np.median(indexList))
    max_left_torque = leftT[maxLeftT_index]

    #ax_left_torque.scatter(time[maxLeftT], leftT[maxLeftT], s=2, c='red')
    #ax_left_torque.annotate(leftT[maxLeftT], (time[maxLeftT], leftT[maxLeftT]), textcoords='offset pixels', xytext=(5, 5))

    ###############################################################################

    # Max Right Torque
    absoluteRightT = np.absolute(rightT)
    indexList = np.where(absoluteRightT == np.amax(absoluteRightT))

    maxRightT_index = int(np.median(indexList))
    max_right_torque = rightT[maxRightT_index]

    #ax_right_torque.scatter(time[maxRightT], rightT[maxRightT], s=2, c='red')
    #ax_right_torque.annotate(rightT[maxRightT], (time[maxRightT], rightT[maxRightT]), textcoords='offset pixels', xytext=(5, 5))

    maxAverageTorque = (abs(max_left_torque) + abs(max_right_torque)) / 2

    print('Maximum Average Torque: ', maxAverageTorque)

    ###############################################################################

    # Max RPM
    maxCommand = np.where(command == np.amax(command))

    #indexList = np.where(rpm == np.amax(rpm))

    maxRPM_index = int(maxCommand[0])#int(np.median(indexList))

    max_rpm = rpm[maxRPM_index]
    print('Maximum RPM: ', max_rpm)
    #ax_rpm.scatter(time[maxRPM], rpm[maxRPM], s=2, c='red')
    #ax_rpm.annotate(rpm[maxRPM], (time[maxRPM], rpm[maxRPM]), textcoords='offset pixels', xytext=(15, 30))

    ###############################################################################

    # The following is to calculate the timeConstantUp and timeConstantDown parameters.

    """
    minIndex = np.where(rThrust == np.amin(rThrust))
    maxIndex = np.where(rThrust == np.amax(rThrust))

    print(minIndex)

    # The min index we want on the rising side is the one before the first maximum.
    # The first min index to be greater than the max is the minimum on the falling side.
    minRisingIndex = 0
    minFallingIndex = 0
    for z in minIndex:
            if (z < maxIndex[0][0]):
                    minRisingIndex = z
            else:
                    minFallingIndex = z
                    break

    """
    epsilon = 0.01
    minRisingIndex = 0
    for z in range(len(rThrust)):
            if (rThrust[z + 1] - rThrust[z] >= epsilon):
                    minRisingIndex = z
                    break

    maxRisingIndex = 0
    for z in range(len(rThrust) - minRisingIndex):
            if (rThrust[z + 1 + minRisingIndex] - rThrust[z + minRisingIndex] <= epsilon):
                    maxRisingIndex = z + minRisingIndex
                    break

    maxFallingIndex = 0
    for z in range(len(rThrust) - maxRisingIndex):
            if (rThrust[z + maxRisingIndex] - rThrust[z + 1 + maxRisingIndex] >= epsilon):
                    maxFallingIndex = z + maxRisingIndex
                    break

    minFallingIndex = 0
    for z in range(len(rThrust) - maxFallingIndex):
            if (rThrust[z + maxFallingIndex] - rThrust[z + 1 + maxFallingIndex] <= epsilon):
                    minFallingIndex = z + maxFallingIndex
                    break

    timeConstantUp = rTime[maxRisingIndex] - rTime[minRisingIndex] 
    timeConstantDown = rTime[minFallingIndex] - rTime[maxFallingIndex]

    timeConstants = 'timeConstantUp: {} | timeConstantDown: {}'.format(timeConstantUp, timeConstantDown)

    ###############################################################################

    # Calculate motor constants

    rev_per_second = max_rpm / 60.0
    n = rev_per_second
    D = args.prop_diameter/1000.0
    rho = 1.23

    Q = max(abs(max_left_torque), abs(max_right_torque))

    #P = (Q * 2 * math.pi * n)
    Ct0 = max_thrust/ (rho * np.power(n, 2) * np.power(D, 4))
    Cq0 =  Q/(rho * np.power(n, 2) * np.power(D, 5))

    #motor_constant_ = max_thrust / (4 * np.power(math.pi, 2) * np.power(rev_per_second, 2))
    #moment_constant_ = np.power(D, 2) * max_thrust /Q

    my_moment_constant = (Cq0 * D)/Ct0

    # TODO Calculate Ct0 and Cq0 for all values of n
    #
    myMotorC = (Ct0 * rho * np.power(D, 4)) /np.power(2 * math.pi, 2)
    print ("D=", D)
    print ("Average Torque=", Q)
    print ("Max thrust=", max_thrust)
    print ("n=", n)
    print ("Ct0=", Ct0)
    print ("Cq0=", Cq0)
    print ("My moment constant ", my_moment_constant)
    print ("My motor constant ", myMotorC)

    rotor_velocity = rev_per_second * 2 * math.pi

    """
    print ("Motor Parameters")
    print ("-----------------")
    print("timeConstantUp: {}".format(timeConstantUp))
    print("timeConstantDown: {}".format(timeConstantDown))
    print("motorConstant: {}".format(motor_constant_))
    print("momentConstant: {}".format(moment_constant_))
    print("maxRotVelocity: {}".format(rotor_velocity))
    """

    #p.figtext(0.5, 0.01, consts, va='bottom', ha='center')

    if args.show_plot:
        p.show()


class MetricGenerator:
    def __init__(self, prop_diameter, ramp_time, ramp_command, ramp_thrust, ramp_left_torque, ramp_right_torque, ramp_rpm, step_time, step_command, step_thrust):
        self.D = prop_diameter
        self.ramp_time = ramp_time
        self.ramp_command = ramp_command
        self.ramp_thrust = ramp_thrust
        self.ramp_left_torque = ramp_left_torque
        self.ramp_right_torque = ramp_right_torque
        self.ramp_rpm = ramp_rpm
        self.ramp_torque = (ramp_left_torque + ramp_right_torque)/2.0

        self.step_time = step_time
        self.step_command = step_command
        self.step_thrust = step_thrust

        self.rho = 1.23

    def plot_step(self):

        fig, ax1 = plt.subplots()
        ax1.plot(self.step_time, self.step_thrust, '*-')
        ax1.set_xlabel("Time (s)")
        ax1.set_ylabel('Thrust (N)')
        color = 'r'
        label = "Motor Signal (%)"
        ax_command = ax1.twinx()
        ax_command.plot(self.step_time, self.step_command, color=color)
        ax_command.set_ylabel(label, color=color)
        ax_command.tick_params(axis='y', labelcolor=color)
        plt.show()

    def plot_c_t_static(self):
        n = self.ramp_rpm / 60.0
        T = self.ramp_thrust

        Ct0 = T / (self.rho * np.power(n, 2) * np.power(self.D, 4))

        start = 100
        print ("Average=", np.average(Ct0[start:]))
        fig, ax1 = plt.subplots()
        ax1.plot(self.ramp_rpm[start:], Ct0[start:], '*')
        ax1.set_xlabel("RPM")
        ax1.set_ylabel('Ct0')

    def plot_c_q_static(self):
        n = self.ramp_rpm / 60.0
        Q = self.ramp_torque 

        Cq0 =  Q/(self.rho * np.power(n, 2) * np.power(self.D, 5))
        #plt.plot(self.ramp_time, Cq0)

        max_torque_index = int(np.where(self.ramp_torque == np.amax(self.ramp_torque))[0][0])
        print ("Max=", max_torque_index)
        
        start = 100
        print ("Average=", np.average(Cq0[start:]))
        fig, ax1 = plt.subplots()
        ax1.plot(self.ramp_rpm[start:], Cq0[start:], '*')
        ax1.set_xlabel("RPM")
        ax1.set_ylabel('Cq0')
        """
        color = 'r'
        label = "PWM Motor Signal (µs)"
        ax2 = ax1.twinx()
        ax2.plot(rTime, rcommand, color=color)
        ax2.set_ylabel(label, color=color)
        ax2.tick_params(axis='y', labelcolor=color)
        """
        plt.show()

    def plot_moment_constant(self):
        Q = self.ramp_torque 
        T = self.ramp_thrust

        start = 100
        moment_constants = Q/T

        #print ("Average=", np.average(moment_constants[start:]))
        print ("Average=", np.average(moment_constants))

        fig, ax1 = plt.subplots()
        ax1.plot(self.ramp_rpm[start:], moment_constants[start:], '*')
        ax1.set_xlabel("RPM")
        ax1.set_ylabel('moment constant')
        plt.show()

    def plot_force(self):
        fig, ax1 = plt.subplots()
        ax1.plot(self.ramp_time, self.ramp_thrust)
        ax1.set_xlabel("Time (s)")
        ax1.set_ylabel('Thrust (N)')
        color = 'r'
        label = "Motor Signal (%)"
        ax_command = ax1.twinx()
        ax_command.plot(self.ramp_time, self.ramp_command, color=color)
        ax_command.set_ylabel(label, color=color)
        ax_command.tick_params(axis='y', labelcolor=color)

        plt.show()

    def plot_torque(self):
        fig, ax1 = plt.subplots()
        ax1.plot(self.ramp_time, self.ramp_torque)
        ax1.set_xlabel("Time (s)")
        ax1.set_ylabel('Torque (N-m)')
        color = 'r'
        label = "Motor Signal (%)"
        ax_command = ax1.twinx()
        ax_command.plot(self.ramp_time, self.ramp_command, color=color)
        ax_command.set_ylabel(label, color=color)
        ax_command.tick_params(axis='y', labelcolor=color)
        plt.show()
    
    def plot_rpm(self):
        fig, ax1 = plt.subplots()
        ax1.plot(self.ramp_time, self.ramp_rpm)
        ax1.set_xlabel("Time (s)")
        ax1.set_ylabel('Motor Angular Velocity (RPM)')
        color = 'r'
        label = "Motor Signal (%)"
        ax_command = ax1.twinx()
        ax_command.plot(self.ramp_time, self.ramp_command, color=color)
        ax_command.set_ylabel(label, color=color)
        ax_command.tick_params(axis='y', labelcolor=color)
        plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Analyze motor data that was previously recorded.")
    parser.add_argument('--show-plot', action="store_true")
    parser.add_argument('--ramp-filepath', help="", default="data.csv")
    parser.add_argument('--step-filepath', help="", default="data.csv")
    parser.add_argument('--prop-diameter', type=float, help="Diameter for propeller in millimeters")
    args = parser.parse_args()

    #args.show_plot = True
    time, command, thrust, leftT, rightT, rpm = np.loadtxt(args.ramp_filepath, delimiter=',', unpack=True)
    step_time, step_command, step_thrust, _, _, step_rpm = np.loadtxt(args.step_filepath, delimiter=',', unpack=True)

    command[command == 0.0] = 1000
    command /= 1000.0
    command -= 1

    step_command[step_command == 0.0] = 1000
    step_command /= 1000.0
    step_command -= 1

    thrust = np.absolute(thrust)
    left_torque = np.absolute(leftT)
    right_torque = np.absolute(rightT)
    mg = MetricGenerator(args.prop_diameter/1000.0, 
                         time, 
                         command, 
                         np.absolute(thrust), 
                         left_torque, 
                         right_torque, 
                         rpm,
                         step_time,
                         step_command,
                         np.absolute(step_rpm))

    #mg.plot_c_q_static()
    #mg.plot_c_t_static()
    #mg.plot_moment_constant()
    mg.plot_force()
    #mg.plot_torque()
    #mg.plot_rpm()
    mg.plot_step()


