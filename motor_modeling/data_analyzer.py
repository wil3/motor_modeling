import csv
import matplotlib.pyplot as plt
import numpy as np
import math
import argparse
import os
import pandas as pd
import scipy.fftpack
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d
from scipy.signal import savgol_filter


class MetricGenerator:
    def __init__(self, prop_diameter, ramp_file, step_file):
        self.D = prop_diameter
        self.ramp_file = ramp_file
        self.step_file = step_file

        # Values to create any of the metrics
        self.ramp_time = []
        self.ramp_command = [] 
        self.ramp_thrust = [] 
        self.ramp_left_torque = [] 
        self.ramp_right_torque = []
        self.ramp_rpm = []

        self.step_time = []
        self.step_command = []
        self.step_thrust = []

        self.rho = 1.23

        self.process()

    def process(self):
        if os.path.isfile(self.ramp_file):
            self.parse_ramp(self.ramp_file)
        else:
            pass

    def parse_ramp(self, filepath, start_time=1, end_time=41):
        t, command, thrust, left_torque, right_torque, rpm = np.loadtxt(filepath, delimiter=',', unpack=True)

        """
        start_time_index = 0
        end_time_index = -1
        for i in range(len(t)):
            if t[i] > start_time:
                start_time_index = i
                break
        for i in range(len(t)):
            if t[i] > end_time: 
                end_time_index = i
                break



        t = t[start_time_index:end_time_index] - t[start_time_index]
        """
        command[command == 0.0] = 1000
        command /= 1000.0
        command -= 1
        #self.ramp_command = command

        thrust = np.absolute(thrust)
        left_torque = np.absolute(left_torque)
        right_torque = np.absolute(right_torque)
        torque = (left_torque + right_torque)/2.0
        #ramp_time, ramp_command, ramp_thrust, ramp_left_torque, ramp_right_torque, ramp_rpm, step_time, step_command, step_thrust
        start_time_index = 0
        end_time_index = -1
        return (t, 
                command[start_time_index:end_time_index], 
                thrust[start_time_index:end_time_index], 
                torque[start_time_index:end_time_index], 
                rpm[start_time_index:end_time_index])

    def parse_step(self, filepath):
        step_time, step_command, step_thrust, _, _, step_rpm = np.loadtxt(filepath, delimiter=',', unpack=True)


        step_command[step_command == 0.0] = 1000
        step_command /= 1000.0
        step_command -= 1
        step_rpm = np.absolute(step_rpm)

    def compute_sdf_values(self):

        t, command, thrusts, torques, rpms = self._trim_ramp_metrics()

        rev_per_second = max_rpm / 60.0
        rotor_velocity = rev_per_second * 2 * math.pi

        print("timeConstantUp: {}".format(time_constant_up))
        print("timeConstantDown: {}".format(time_constant_down))
        print("motorConstant: {}".format(motor_constant))

        Q =  np.average(torques, axis=0) 
        T = np.average(thrusts, axis=0)
        moment_constants = Q/T

        #print ("Average=", np.average(moment_constants[start:]))
        print ("Average=", np.average(moment_constants))
        print("momentConstant: {}".format(moment_constant))


        ave_rpm = np.average(rpms, axis=0)
        max_rotor_velocity = np.amax(ave_rpm)
        print("maxRotVelocity: {}".format(max_rotor_velocity))

    def _sliding_window(self, xs, ys, stop_time=3, size=0.01, step_size = 0.001):
        """
        return values from an average sliding window for data that has different
        time series

        Args:
            xs: An array of times
            ys: An array of data that hapen at xs[i]
            stop_time: seconds in which we could do the window up too
            size: Of the sliding window in seconds
            step_size: to count

        Return: times, average values, low values, high values
        """
        start_time = 0
        end_time = size
        rpms = []
        ts = []
        
        lows = []
        highs = []
        while end_time < stop_time:
            rpms_in_window = []
            for i in range(len(xs)):
                index_low = np.nonzero(xs[i] >= start_time)
                index_high = np.nonzero(xs[i] < end_time)
                index = np.intersect1d(index_low, index_high)
                rpms_in_window += ys[i][index].tolist()

            #print ("Start ", start_time, " End ", end_time, " ", rpms_in_window)
            if len(rpms_in_window) == 0:
                start_time += step_size
                end_time = start_time + size
                continue
            ave = np.average(rpms_in_window)
            lows.append(np.amin(rpms_in_window))
            highs.append(np.amax(rpms_in_window))
            rpms.append(ave)
            ts.append(start_time)
            #start_time += size
            start_time += step_size
            end_time = start_time + size

        return ts, rpms, lows, highs

    def plot_step(self):
        fig, ax = plt.subplots()
        ax.set_xlabel("Time (s)")
        ax.set_ylabel('Motor Velocity (RPM)')

        t = command = thrust = torque = rpm = None
        ts = []
        commands = []
        if os.path.isfile(self.ramp_file):
            (t, command, thrust, _, _) = self.parse_ramp(self.ramp_file)
            ax.plot(t, thrust)
        else:
            ts, commands, rpms,names = self._trim_step_metrics()
            #ave_rpm = np.average(rpms, axis=0)

            peak_velocity = np.amax(rpms)
            print ("Peak velocity is ", peak_velocity)
            time_constant_velocity = peak_velocity * 0.632
            print ("Tau Velocity =", time_constant_velocity)
            #ax.plot([0])
            #for i in range(len(ts)):
            #    ax.plot(ts[i], rpms[i], label=names[i], marker='.')


            #XXX The window determines the step size
            x, y, low, high = self._sliding_window(ts, rpms, size=0.015)

            middle_x = (np.abs(np.array(x) - 1.5)).argmin()
            idx = (np.abs(y[:middle_x] - time_constant_velocity)).argmin()
            tau_up = x[idx] - 1.0
            tau_up_x = x[idx]
            print ("Tau up=", tau_up)

            color = 'grey'
            linestyle = 'dotted'
            ax.plot([0, tau_up_x], [time_constant_velocity, time_constant_velocity], ls=linestyle, color=color)
            ax.plot([tau_up_x, tau_up_x], [0,time_constant_velocity ], ls=linestyle, color=color)

            time_constant_velocity_down = peak_velocity * (1-0.632)
            print ("Speed down=", time_constant_velocity_down)
            print ("Middle x=", middle_x)
            idx = (np.abs(y[middle_x:] - time_constant_velocity_down)).argmin()
            tau_down = x[middle_x + idx] - 2.0
            print ("Tau down=", tau_down)
            tau_down_x = tau_down + 2

            ax.plot([0, tau_down_x], [time_constant_velocity_down, time_constant_velocity_down], ls=linestyle, color=color)
            ax.plot([tau_down_x, tau_down_x], [0,time_constant_velocity_down ], ls=linestyle, color=color)


            ax.set_xlim(0, 3)

            ax.plot(x,y,'--', color="k")

            #ax.plot(t, ave_rpm, '--')
            ax.fill_between(x, low, high, alpha=.3, color="blue")

        # time when target is when command is 0.632

        fig, ax1 = plt.subplots()
        ax1.plot(self.step_time, self.step_thrust, '*-')
        ax1.set_xlabel("Time (s)")
        ax1.set_ylabel('RPM')
        color = 'r'
        label = "Motor Signal (%)"
        ax_command = ax.twinx()
        #ax_command.plot(t, command, color=color)
        ax_command.set_ylabel(label, color=color)
        ax_command.tick_params(axis='y', labelcolor=color)
        t = [0, 1, 1, 2, 2, 3]
        c = [0, 0, 1, 1, 0, 0]
        ax_command.plot(t, c, color=color)

        plt.show()


    def c_t_static(self, n, T):
        return T / (self.rho * np.power(n, 2) * np.power(self.D, 4))

    def plot_c_t_static(self):
        """ Plot the C_t0, the thurst coefficient for static conditions


        """
        t, command, thrusts, torques, rpms = self._trim_ramp_metrics()

        T = np.average(thrusts, axis=0)
        ave_rpm = np.average(rpms, axis=0)
        n = ave_rpm / 60.0

        min_rpm = 5000

        max_throttle_index = np.argmax(ave_rpm)

        min_rpm_index = 0
        for i in range(len(ave_rpm)):
            if ave_rpm[i] > min_rpm:
                min_rpm_index = i
                break

        ramp_up_thrust = T[min_rpm_index:max_throttle_index]
        ramp_up_rpm = ave_rpm[min_rpm_index:max_throttle_index]
        ramp_up_n = n[min_rpm_index:max_throttle_index]

        min_rpm_index = 0
        for i in range(len(ave_rpm)-1, -1, -1):
            if ave_rpm[i] > min_rpm:
                min_rpm_index = i
                break

        ramp_down_thrust = np.flip(T[max_throttle_index:min_rpm_index])
        ramp_down_rpm = np.flip(ave_rpm[max_throttle_index:min_rpm_index])
        ramp_down_n = np.flip(n[max_throttle_index:min_rpm_index])
        
        with np.errstate(divide='ignore', invalid='ignore'):
            Ct0_ramp_up = self.c_t_static(ramp_up_n, ramp_up_thrust) 
            Ct0_ramp_up[Ct0_ramp_up == np.inf] = 0

            Ct0_ramp_down = self.c_t_static(ramp_down_n, ramp_down_thrust) 
            Ct0_ramp_down[Ct0_ramp_down == np.inf] = 0

            min_l = np.minimum(len(Ct0_ramp_up), len(Ct0_ramp_down))
            ave_Ct0 = np.average([Ct0_ramp_up[:min_l], Ct0_ramp_down[:min_l]])
            print ("Average Ct0=", ave_Ct0)

            """
            print("UP RPM=",ramp_up_rpm)
            print ("UP T=", ramp_up_thrust)
            print (Ct0_ramp_up)
            print ("DOWN")

            #print (ramp_down_n)
            print ("DOWN RPM", ramp_down_rpm)
            print ("DOWN T=", ramp_down_thrust)
            print (Ct0_ramp_down)
            """

            fig, ax = plt.subplots()
            ax.plot(ramp_up_rpm, Ct0_ramp_up, color='tab:orange', marker='.')
            ax.plot(ramp_down_rpm, Ct0_ramp_down, '.', color='tab:blue', )
            ax.axhline(ave_Ct0, color='r')
            #ax.plot(ave_rpm[max_throttle_index:], Ct0[max_throttle_index:], color='tab:blue', marker='.')


            ax.set_xlabel("RPM")
            ax.set_ylabel('$C_{t0}$')
        plt.show()

    def c_q_static(self, n, Q):
        return  Q/(self.rho * np.power(n, 2) * np.power(self.D, 5))


    def plot_c_q_static(self):
        fig, ax = plt.subplots()

        t, command, thrusts, torques, rpms, names = self._trim_ramp_metrics()
        t_torque, Q, low, high = self._sliding_window(t, torques, stop_time=45, size=0.2)
        t_rpm, ave_rpm, low, high = self._sliding_window(t, rpms, stop_time=45, size=0.2)

        #Q = np.average(torques, axis=0)
        #ave_rpm = np.average(rpms, axis=0)
        ave_rpm = np.array(ave_rpm)
        n = ave_rpm / 60.0

        min_rpm = 5000

        #max_throttle_index = np.argmax(ave_rpm)
        max_throttle_index = np.argmax(Q)

        # Chop off the head
        min_rpm_index = (np.abs(ave_rpm[:len(ave_rpm)//2] - min_rpm)).argmin()
        ramp_up_torque = Q[min_rpm_index:max_throttle_index]
        ramp_up_rpm = ave_rpm[min_rpm_index:max_throttle_index]
        ramp_up_n = n[min_rpm_index:max_throttle_index]

        ax.plot(t_torque[min_rpm_index:max_throttle_index], ramp_up_torque, label="up")
        # Chop off the tail end
        """
        min_rpm_index = 0
        for i in range(len(ave_rpm)-1, -1, -1):
            if ave_rpm[i] > min_rpm:
                min_rpm_index = i
                break
        """

        min_rpm_index =len(ave_rpm)//2 + (np.abs(ave_rpm[len(ave_rpm)//2:] - min_rpm)).argmin()
        ramp_down_torque = np.flip(Q[max_throttle_index:min_rpm_index])
        ramp_down_rpm = np.flip(ave_rpm[max_throttle_index:min_rpm_index])
        ramp_down_n = np.flip(n[max_throttle_index:min_rpm_index])


        ax.plot(t_torque[max_throttle_index:min_rpm_index], ramp_down_torque, label="down")
        
        """
        with np.errstate(divide='ignore', invalid='ignore'):
            Ct0_ramp_up = self.c_q_static(ramp_up_n, ramp_up_torque) 
            Ct0_ramp_up[Ct0_ramp_up == np.inf] = 0

            Ct0_ramp_down = self.c_t_static(ramp_down_n, ramp_down_torque) 
            Ct0_ramp_down[Ct0_ramp_down == np.inf] = 0

            min_l = np.minimum(len(Ct0_ramp_up), len(Ct0_ramp_down))
            ave_Ct0 = np.average([Ct0_ramp_up[:min_l], Ct0_ramp_down[:min_l]])
            print ("Average CQ0=", ave_Ct0)
            ax.plot(ramp_up_rpm, Ct0_ramp_up, '.', color='tab:orange', label="Accelleration")
            ax.plot(ramp_down_rpm, Ct0_ramp_down, '.', color='tab:blue', label="Deceleration")
            ax.axhline(ave_Ct0, color='r')
            #ax.plot(ave_rpm[max_throttle_index:], Ct0[max_throttle_index:], color='tab:blue', marker='.')


            ax.set_xlabel("RPM")
            ax.set_ylabel('$C_{q0}$')
            
        """
        ax.legend(loc='upper left')
        plt.show()

    def split_ramp(self, fn=np.average, min_rpm=5000):
        t, command, thrusts, torques, rpms = self._trim_ramp_metrics()

        Q = fn(torques, axis=0)
        T = fn(thrusts, axis=0)
        ave_rpm = np.average(rpms, axis=0)
        n = ave_rpm / 60.0


        max_throttle_index = np.argmax(ave_rpm)

        min_rpm_index = 0
        for i in range(len(ave_rpm)):
            if ave_rpm[i] > min_rpm:
                min_rpm_index = i
                break

        ramp_up_Q = Q[min_rpm_index:max_throttle_index]
        ramp_up_T = T[min_rpm_index:max_throttle_index]
        ramp_up_RPM = ave_rpm[min_rpm_index:max_throttle_index]

        min_rpm_index = 0
        for i in range(len(ave_rpm)-1, -1, -1):
            if ave_rpm[i] > min_rpm:
                min_rpm_index = i
                break

        ramp_down_Q = np.flip(Q[max_throttle_index:min_rpm_index])
        ramp_down_T = np.flip(T[max_throttle_index:min_rpm_index])
        ramp_down_RPM = np.flip(ave_rpm[max_throttle_index:min_rpm_index])

        return(ramp_up_Q, ramp_up_T, ramp_up_RPM), (ramp_down_Q, ramp_down_T, ramp_down_RPM) 

    def plot_moment_constant(self):
        fig, ax = plt.subplots()

        (ramp_up_Q, ramp_up_T, ramp_up_RPM), (ramp_down_Q, ramp_down_T, ramp_down_RPM)  = self.split_ramp(min_rpm=0)
        moment_constants_up = ramp_up_Q/ramp_up_T
        moment_constants_down = ramp_down_Q/ramp_down_T
        min_l = np.minimum(len(moment_constants_up), len(moment_constants_down))
        moment_constant = np.average([moment_constants_up[:min_l], moment_constants_down[:min_l]])
        print ("Average Moment Constant=", moment_constant)

        ax.plot(ramp_up_RPM, moment_constants_up, '.', color="tab:orange")
        ax.plot(ramp_down_RPM, moment_constants_down, '.', color="tab:blue")

        (ramp_up_Q, ramp_up_T, ramp_up_RPM), (ramp_down_Q, ramp_down_T, ramp_down_RPM)  = self.split_ramp(fn=np.amin, min_rpm=0)
        moment_constants_up = ramp_up_Q/ramp_up_T
        moment_constants_down = ramp_down_Q/ramp_down_T
        min_l = np.minimum(len(moment_constants_up), len(moment_constants_down))
        moment_constant = np.average([moment_constants_up[:min_l], moment_constants_down[:min_l]])
        print ("Average Moment Constant=", moment_constant)

        ax.plot(ramp_up_RPM, moment_constants_up, '*', color="tab:orange")
        ax.plot(ramp_down_RPM, moment_constants_down, '*', color="tab:blue")

        (ramp_up_Q, ramp_up_T, ramp_up_RPM), (ramp_down_Q, ramp_down_T, ramp_down_RPM)  = self.split_ramp(fn=np.amax, min_rpm=0)
        moment_constants_up = ramp_up_Q/ramp_up_T
        moment_constants_down = ramp_down_Q/ramp_down_T
        min_l = np.minimum(len(moment_constants_up), len(moment_constants_down))
        moment_constant = np.average([moment_constants_up[:min_l], moment_constants_down[:min_l]])
        print ("Average Moment Constant=", moment_constant)

        ax.plot(ramp_up_RPM, moment_constants_up, 'o', color="tab:orange")
        ax.plot(ramp_down_RPM, moment_constants_down, 'o', color="tab:blue")



        ax.set_xlabel("RPM")
        ax.set_ylabel('moment constant')
        plt.show()


    def _trim_ramp_metrics(self):
        """
        Return:
            t 2D array
            command 1D array
            thrust List of np arrays
            torque List of np arrays
            rpm List of np arrays
        """
        raw_thrusts = []
        raw_torques = []
        raw_rpms = []
        min_length = 1e6
        ts = []
        filenames= []
        for name in os.listdir(self.ramp_file):
            filepath = os.path.join(self.ramp_file, name)
            print ("Processing ", filepath)
            if os.path.isfile(filepath):
                (t, command, thrust, torque, rpm) = self.parse_ramp(filepath)
                min_length = min(min_length, len(thrust))
                raw_thrusts.append(thrust)
                raw_torques.append(torque)
                raw_rpms.append(rpm)
                ts.append(t)
                filenames.append(name)


        # They may not have all finished exactly the same time
        trimmed_thrusts = []
        trimmed_torques = []
        trimmed_rpms = []
        trimmed_ts = []
        for i in range(len(raw_thrusts)):
            trimmed_thrusts.append(raw_thrusts[i][:min_length])
            trimmed_torques.append(raw_torques[i][:min_length])
            trimmed_rpms.append(raw_rpms[i][:min_length])
            trimmed_ts.append(ts[i][:min_length])

        t = t[:min_length]
        return trimmed_ts, command[:min_length], trimmed_thrusts, trimmed_torques, trimmed_rpms, filenames


    def _trim_step_metrics(self):
        raw_rpms = []
        raw_ts = []
        min_length = 1e6
        filenames= []
        raw_commands = []
        for name in os.listdir(self.step_file):
            filepath = os.path.join(self.step_file, name)
            print ("Processing ", filepath)
            if os.path.isfile(filepath):
                (t, command, _, _, rpm) = self.parse_ramp(filepath, start_time=0, end_time=1e6)
                min_length = min(min_length, len(rpm))
                raw_rpms.append(rpm)
                raw_ts.append(t)
                raw_commands.append(command)
                filenames.append(name)

        # They may not have all finished exactly the same time
        trimmed_rpms = []
        trimmed_ts = []
        trimmed_commands = []
        for i in range(len(raw_rpms)):
            trimmed_rpms.append(raw_rpms[i][:min_length])
            trimmed_ts.append(raw_ts[i][:min_length])
            trimmed_commands.append(raw_commands[i][:min_length])

        t = t[:min_length]
        return trimmed_ts, trimmed_commands, trimmed_rpms, filenames

    def plot_force(self):
        fig, ax = plt.subplots()
        ax.set_xlabel("Time (s)")
        ax.set_ylabel('Thrust (N)')

        t = command = thrust = torque = rpm = None
        t, command, thrusts, _, _, names = self._trim_ramp_metrics()
        #for i in range(len(t)):
        #    ax.plot(t[i], thrusts[i], label=names[i])
        #ax.legend(loc='upper left')

        t, ave_thrust, low, high = self._sliding_window(t, thrusts, stop_time=45, size=0.1)
        average_max_thrust = np.amax(ave_thrust)
        print ("Average max thrust=", average_max_thrust)
        #ave_thrust = np.average(thrusts, axis=0)
        ax.plot(t, ave_thrust, '--', color="k")
        ax.fill_between(t, low, high, alpha=.3, color="blue")
        color = 'r'
        label = "Motor Signal (%)"
        ax_command = ax.twinx()
        ax_command.plot([0, 1, 20, 40, 45], [0, 0, 1, 0, 0], color=color)

        ax_command.set_ylabel(label, color=color)
        ax_command.tick_params(axis='y', labelcolor=color)

        plt.show()

    def plot_ramp(self, ylabel, measure_index):
        """
        t = 0
        command = 1
        thrusts = 2
        torques = 3
        rpms = 4
        names = 5
        """
        fig, ax = plt.subplots()
        ax.set_xlabel("Time (s)")
        ax.set_ylabel(ylabel)

        t = command = thrust = torque = rpm = None
        metrics = self._trim_ramp_metrics()
        t = metrics[0] 
        #for i in range(len(t)):
        #    ax.plot(t[i], thrusts[i], label=names[i])
        #ax.legend(loc='upper left')

        t, ave, low, high = self._sliding_window(t, metrics[measure_index], stop_time=45, size=0.1)
        max_average = np.amax(ave)
        print ("Average =", max_average, " ", ylabel)
        #ave_thrust = np.average(thrusts, axis=0)
        ax.plot(t, ave, '--', color="k")
        ax.fill_between(t, low, high, alpha=.3, color="blue")

        color = 'r'
        label = "Motor Signal (%)"
        ax_command = ax.twinx()
        ax_command.plot([0, 1, 20, 40, 45], [0, 0, 1, 0, 0], color=color)

        ax_command.set_ylabel(label, color=color)
        ax_command.tick_params(axis='y', labelcolor=color)

        plt.show()

    def plot_torque(self):
        self.plot_ramp('Torque (N-m)', 3)

    def plot_force_rpm(self):
        fig, ax = plt.subplots()
        ax.set_xlabel("Time (s)")
        ax.set_ylabel('Thrust (N)')

        t = command = thrust = torque = rpm = None
        if os.path.isfile(self.ramp_file):
            (t, command, thrust, _, _) = self.parse_ramp(self.ramp_file)
            ax.plot(t, thrust)
        else:
            t, command, thrusts, _, rpms = self._trim_ramp_metrics()
            ave_thrust = np.average(thrusts, axis=0)
            rpm = np.average(rpms, axis=0)
            ax.plot(t, ave_thrust, '--')
            ax.fill_between(t, np.amin(thrusts, axis=0), np.amax(thrusts, axis=0), alpha=.3)
        color = 'r'
        label = "Motor Angular Velocity (RPM)"
        ax_command = ax.twinx()
        ax_command.plot(t, rpm, color=color)
        ax_command.set_ylabel(label, color=color)
        ax_command.tick_params(axis='y', labelcolor=color)

        plt.show()

    def plot_torque2(self):
        fig, ax = plt.subplots()
        ax.set_xlabel("Time (s)")
        ax.set_ylabel('Torque (N-m)')

        t = command = thrust = torque = rpm = None
        if os.path.isfile(self.ramp_file):
            (t, command, _, torque, _) = self.parse_ramp(self.ramp_file)
            ax.plot(t, torque)
        else:
            raw_torques = []
            min_length = 1e6
            for name in os.listdir(self.ramp_file):
                filepath = os.path.join(self.ramp_file, name)
                print ("Processing ", filepath)
                if os.path.isfile(filepath):
                    (t, command, _, torque, _) = self.parse_ramp(filepath)
                    min_length = min(min_length, len(torque))
                    raw_torques.append(torque)

            trimmed_torques = []
            for raw_torque in raw_torques:
                trimmed_torques.append(raw_torque[:min_length])

            t = t[:min_length]
            ave_torque = np.average(trimmed_torques, axis=0)
            ax.plot(t, ave_torque, '--')
            ax.fill_between(t, np.amin(trimmed_torques, axis=0), np.amax(trimmed_torques, axis=0), alpha=.3)

        color = 'r'
        label = "Motor Signal (%)"
        ax_command = ax.twinx()
        ax_command.plot(t, command, color=color)
        ax_command.set_ylabel(label, color=color)
        ax_command.tick_params(axis='y', labelcolor=color)

        plt.show()

    def plot_rpm(self):
        self.plot_ramp('Motor Angular Velocity (RPM)', 4)

    def plot_rpm2(self):
        fig, ax = plt.subplots()
        ax.set_xlabel("Time (s)")
        ax.set_ylabel('Motor Angular Velocity (RPM)')

        t = command = thrust = torque = rpm = None
        if os.path.isfile(self.ramp_file):
            (t, command, _, _ , rpm) = self.parse_ramp(self.ramp_file)
            ax.plot(t, rpm)
        else:
            raw_rpms = []
            min_length = 1e6
            for name in os.listdir(self.ramp_file):
                filepath = os.path.join(self.ramp_file, name)
                print ("Processing ", filepath)
                if os.path.isfile(filepath):
                    (t, command, _, _, rpm) = self.parse_ramp(filepath)
                    min_length = min(min_length, len(rpm))
                    raw_rpms.append(rpm)

            trimmed_rpms = []
            for raw_rpm in raw_rpms:
                trimmed_rpms.append(raw_rpm[:min_length])

            t = t[:min_length]
            ave_rpm = np.average(trimmed_rpms, axis=0)
            ax.plot(t, ave_rpm, '--')
            ax.fill_between(t, np.amin(trimmed_rpms, axis=0), np.amax(trimmed_rpms, axis=0), alpha=.3)

        color = 'r'
        label = "Motor Signal (%)"
        ax_command = ax.twinx()
        ax_command.plot(t, command, color=color)
        ax_command.set_ylabel(label, color=color)
        ax_command.tick_params(axis='y', labelcolor=color)

        plt.show()

    def parse_scopes(self):
        fs = [
        "/home/wil/workspace/gymfc-nf1/digitaltwin/data/oscilliscope/step_25.csv",
        "/home/wil/workspace/gymfc-nf1/digitaltwin/data/oscilliscope/step_50.csv",
        "/home/wil/workspace/gymfc-nf1/digitaltwin/data/oscilliscope/step_75.csv",
        "/home/wil/workspace/gymfc-nf1/digitaltwin/data/oscilliscope/step_100.csv"
        ]
        labels = [
            "25%-Actual",
            "50%-Actual",
            "75%-Actual",
            "100%-Actual",
        ]
        filename = [
            "25", 
            "50", 
            "75", 
            "100"
        ]
        # From scope
        fig, ax = plt.subplots()
        max_rpms = []
        for i in range(len(fs)):
            f_ = "/home/wil/workspace/gymfc-nf1/digitaltwin/data/oscilliscope/processed/rpm_{}.csv".format(filename[i])
            if os.path.isfile(f_):
                print ("Loading data")
                data = np.loadtxt(f_, delimiter=",", skiprows=1)
                ts = data[:,0]#[:1000]
                rpms = data[:,1]#[:1000]
            else:
                data = np.loadtxt(fs[i], delimiter=",", skiprows=1)
                ts = data[:,0]#[:1000]
                vs = data[:,1]#[:1000]

                (ts, rpms) = self.parse_scope(ts, vs)
                
                if i == 1 or i == 2: #messed up recording these
                    end_offset = 2
                    # these were taken for 2 seconds
                    id_t_1 = (np.abs(ts - 1)).argmin()
                    id_t_2 = (np.abs(ts - end_offset)).argmin()
                    ts = np.concatenate([ts[:id_t_1], ts[id_t_2:] - 1])
                    rpms = np.concatenate([rpms[:id_t_1], rpms[id_t_2:]])
                    #ax.plot(ts1, rpms1, label=labels[i])
                    save_data = np.array(list(zip(ts, rpms)))
                else:
                    save_data = np.array(list(zip(ts, rpms)))
                #self.parse_scope(ts, vs, labels[i])
                #else:

                np.savetxt(f_, save_data, header="time,rpms", delimiter=",")

            ax.plot(ts, rpms, label=labels[i])
            print ("{} Max RPM={}".format(labels[i], np.max(rpms)))
            max_rpms.append(np.max(rpms))


            #
            # FITTING
            # 
            x = ts[:len(ts)//2]
            y = rpms[:len(ts)//2]

            xx = np.linspace(x.min(),x.max(), 10000)

            itp = interp1d(x,y, kind='linear')
            window_size, poly_order = 101, 3
            yy_sg = savgol_filter(itp(xx), window_size, poly_order)


            # or fit to a global function
            #def func(x, A, B, x0, sigma):
            #    return A + B*np.tanh((x-x0)/sigma)

            def func(t, tau, v):
                return v * (1 - np.exp(-t/tau))

            fit, _ = curve_fit(func, x, y)
            print ("Params=", fit)
            yy_fit = func(xx, *fit)

            #yy_fit = func(xx, 0.09, 25041)

            #ax.plot(xx, yy_fit, 'b--')

            #ax.plot(x, y, 'r.', label= 'Unsmoothed curve')
            ##ax.plot(xx, 2 * yy_fit, 'b--', label=r"$f(x) = A + B \tanh\left(\frac{x-x_0}{\sigma}\right)$")
            #ax.plot(xx, yy_sg, 'k', label= "Smoothed curve")
            
            #ax.plot(ts, y2, '--', color="r")
            #
            # END FITTING

            ts_half = ts[:len(ts)//2]
            z = np.polyfit(ts_half, rpms[:len(ts)//2], 10)
            p = np.poly1d(z)
            #ax.plot(ts_half, p(ts_half), '--', color="r")



        plt.gca().set_prop_cycle(None)


        #
        #
        # Plot for t vs rpm
        # 

        x_u = np.array([0, .25, .5, .75, 1])
        y_rpm = np.array([0] + max_rpms) * 0.10472

        #xx = np.linspace(x_u.min(), x_u.max(), 10000)
        coef = np.polyfit(x_u, y_rpm, 2)
        p = np.poly1d(coef)


        # From sim
        fs = [
        "/home/wil/workspace/gymfc-nf1/digitaltwin/data/sim/step_25.csv",
        "/home/wil/workspace/gymfc-nf1/digitaltwin/data/sim/step_50.csv",
        "/home/wil/workspace/gymfc-nf1/digitaltwin/data/sim/step_75.csv",
        "/home/wil/workspace/gymfc-nf1/digitaltwin/data/sim/step_100.csv"
        ]
        labels = [
            "25%-Sim",
            "50%-Sim",
            "75%-Sim",
            "100%-Sim",
        ]
        for i in range(len(fs)):
            data = np.loadtxt(fs[i], delimiter=",", skiprows=1)
            ts = data[:,0]#[:1000]
            vs = data[:,1]#[:1000]
            plt.plot(ts, vs, label=labels[i], linestyle='--')


        ax.set_ylabel("RPM")
        ax.set_xlabel("t")

        plt.gca().set_prop_cycle(None)

        cmd_1 = [1, 1, 0, 0]
        cmd_75 = [0.75, 0.75, 0, 0]
        cmd_5 = [0.5, 0.5, 0, 0]
        cmd_25 = [0.25, 0.25, 0, 0]
        cmds = [cmd_1, cmd_75, cmd_5, cmd_25]
        t_cmd = [0, 1, 1, 2]
        label = "Control Signal"
        ax_command = ax.twinx()
        p = np.poly1d(coef)
        for cmd in cmds:
            ax_command.plot(t_cmd, p(cmd)/p(1), color="k", alpha=0.5)


        ax_command.set_xlim(0)
        ax_command.set_ylabel(label)
        ax_command.tick_params(axis='y')

        ax.legend()


        self.plot_motor_velocity_vs_control(max_rpms)
        plt.show()

    def plot_motor_velocity_vs_control(self, max_rpms):
        x_u = np.array([0, .25, .5, .75, 1])

        # XXX THIS IS ACTUALLY RADIANS
        y_rpm = np.array([0] + max_rpms) * 0.10472
        xx = np.linspace(x_u.min(),x_u.max(), 10000)


        #xx = np.linspace(x_u.min(), x_u.max(), 10000)
        coef = np.polyfit(x_u, y_rpm, 2)
        p = np.poly1d(coef)
        print (p)
        fig, ax = plt.subplots()
        ax.set_ylabel("Rotor Velocity (rad/s)")
        ax.set_xlabel("Control signal (u)")
        ax.plot(x_u, y_rpm, "o", label="Measured")
        ax.plot([0, 1], [0, y_rpm[-1]], linestyle="--", color='r', label="Linear reference")
        ax.plot(xx, p(xx), label="Fitted: ${:.2f}x^2 + {:.2f}x + {:.2f}$".format(*coef))
        ax.legend()


    def parse_scope(self, ts, vs):
        threshold_low = 1.2
        threshold_high = 1.5
        START = 0
        RISE_1 = 1
        RISE_2 = 2
        FALL_1 = 3
        FALL_2 = 4

        b = 3

        rising_edge = False
        count = 0
        counts = []
        count_times = []
        last_time = 0
        smallest_period = 1e6
        smallest_period_at_t = 0
        first = True
        decend_t = 0
        decend_start = False
        stage = FALL_2
        peak_times = []
        for i in range(len(vs)):
            v = vs[i]
            t = ts[i]
            #if t < 0:
            #    continue
            #print (t)
            # Rising edge
            interval = t - last_time
            if v > threshold_low and stage == FALL_2: # Falling edge
                stage = RISE_1
                count += 1
                counts.append(count)
                count_times.append(t)
                peak_times.append(t)
                if first:
                    last_time = t
                    first = False
                else:
                    #smallest_period = min (interval, smallest_period)
                    if interval < smallest_period:
                        smallest_period = interval
                        smallest_period_at_t = t
                        
                    last_time = t
                    #plt.axvline(t, color="r")
            elif v > threshold_high and stage == RISE_1:
                stage = RISE_2
            elif v < threshold_high and stage == RISE_2:
                stage = FALL_1
            elif v < threshold_low and stage == FALL_1:
                stage = FALL_2
                #plt.axvline(t, color="b")
            #else:
            #    stage = FALL_2

        peak_times = np.array(peak_times)
        print ("L=", len(peak_times))
        s = len(peak_times) // 3
        #times_per_rotation = np.reshape(peak_times[:s * 3], (s, 3))
        full_rotation_times = peak_times[0::3]
        rpms = (1/np.diff(full_rotation_times)) * 60
        print ("L rot=", len(full_rotation_times), " L rpm=", len(rpms))
        

        print ("T small=", smallest_period_at_t)
        print ("T=", smallest_period)
        f = 1/smallest_period
        rpm = (f * 60) / b

        t = full_rotation_times[:-1]

        id_rpm_10000 = (np.abs(rpms[:len(rpms) // 2] - 10000)).argmin()
        id_rpm_15000 = (np.abs(rpms[:len(rpms) // 2]  - 15000)).argmin()
        
        m = (rpms[id_rpm_15000] - rpms[id_rpm_10000])/(t[id_rpm_15000]-t[id_rpm_10000])
        print ("Slope ", m, " rpms per t")

        print ("RPM=", rpm) 
        print ("Max RPM=", np.max(rpms))
        #plt.plot(ts,vs, color="k")
        #plt.plot(count_times, counts)
        return (t, rpms)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Analyze motor data that was previously recorded.")
    parser.add_argument('--show-plot', action="store_true")
    parser.add_argument('--ramp-filepath', help="Either a specific file or if a directory will take the mean and CI", default="data.csv")
    parser.add_argument('--step-filepath', help="Either a specific file or if a directory will take the mean and CI", default="data.csv")
    parser.add_argument('--prop-diameter', type=float, help="Diameter for propeller in millimeters")
    args = parser.parse_args()

    #args.show_plot = True


    mg = MetricGenerator(args.prop_diameter/1000.0, args.ramp_filepath, args.step_filepath)

    mg.parse_scopes()
    #mg.plot_c_q_static()
    #mg.plot_c_t_static()
    #mg.plot_moment_constant()
    #mg.plot_force()
    #mg.plot_torque()
    #mg.plot_rpm()
    #mg.plot_step()
    #mg.plot_force_rpm()


