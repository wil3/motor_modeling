import serial, time, struct
from msp_protocol import *
from messages import MSPStatusMessage
import signal
import sys
import time
import argparse

class MSP:
    VOLTAGE_METER_ID_NONE = 0
    VOLTAGE_METER_ID_BATTERY_1 = 10       # 10-19 for battery meters
    VOLTAGE_METER_ID_BATTERY_2 = 11
    VOLTAGE_METER_ID_BATTERY_10 = 19
    VOLTAGE_METER_ID_5V_1 = 20         # 20-29 for 5V meters
    VOLTAGE_METER_ID_5V_2 = 21
    VOLTAGE_METER_ID_5V_10 = 29
    VOLTAGE_METER_ID_9V_1 = 30         # 30-39 for 9V meters
    VOLTAGE_METER_ID_9V_2 = 31
    VOLTAGE_METER_ID_9V_10 = 39
    VOLTAGE_METER_ID_12V_1 = 40        # 40-49 for 12V meters
    VOLTAGE_METER_ID_12V_2 = 41
    VOLTAGE_METER_ID_12V_10 = 49
    VOLTAGE_METER_ID_ESC_COMBINED_1 = 50 # 50-59 for ESC combined (it's doubtful an FC would ever expose 51-59 however)
    VOLTAGE_METER_ID_ESC_COMBINED_10 = 59
    VOLTAGE_METER_ID_ESC_MOTOR_1 = 60  # 60-79 for ESC motors (20 motors)
    VOLTAGE_METER_ID_ESC_MOTOR_2 = 61
    VOLTAGE_METER_ID_ESC_MOTOR_3 = 62
    VOLTAGE_METER_ID_ESC_MOTOR_4 = 63
    VOLTAGE_METER_ID_ESC_MOTOR_5 = 64
    VOLTAGE_METER_ID_ESC_MOTOR_6 = 65
    VOLTAGE_METER_ID_ESC_MOTOR_7 = 66
    VOLTAGE_METER_ID_ESC_MOTOR_8 = 67
    VOLTAGE_METER_ID_ESC_MOTOR_9 = 68
    VOLTAGE_METER_ID_ESC_MOTOR_10 = 69
    VOLTAGE_METER_ID_ESC_MOTOR_11 = 70
    VOLTAGE_METER_ID_ESC_MOTOR_12 = 71
    VOLTAGE_METER_ID_ESC_MOTOR_20 = 79
    VOLTAGE_METER_ID_CELL_1 = 80       # 80-119 for cell meters (40 cells)
    VOLTAGE_METER_ID_CELL_2 = 81
    VOLTAGE_METER_ID_CELL_40 = 119

    CURRENT_METER_ID_NONE = 0
    CURRENT_METER_ID_BATTERY_1 = 10       # 10-19 for battery meters
    CURRENT_METER_ID_BATTERY_2 = 11
    CURRENT_METER_ID_BATTERY_10 = 19
    CURRENT_METER_ID_5V_1 = 20         # 20-29 for 5V meters
    CURRENT_METER_ID_5V_2 = 21
    CURRENT_METER_ID_5V_10 = 29
    CURRENT_METER_ID_9V_1 = 30         # 30-39 for 9V meters
    CURRENT_METER_ID_9V_2 = 31
    CURRENT_METER_ID_9V_10 = 39
    CURRENT_METER_ID_12V_1 = 40        # 40-49 for 12V meters
    CURRENT_METER_ID_12V_2 = 41
    CURRENT_METER_ID_12V_10 = 49
    CURRENT_METER_ID_ESC_COMBINED_1 = 50 # 50-59 for ESC combined (it's doubtful an FC would ever expose 51-59 however)
    CURRENT_METER_ID_ESC_COMBINED_10 = 59
    CURRENT_METER_ID_ESC_MOTOR_1 = 60  # 60-79 for ESC motors (20 motors)
    CURRENT_METER_ID_ESC_MOTOR_2 = 61
    CURRENT_METER_ID_ESC_MOTOR_3 = 62
    CURRENT_METER_ID_ESC_MOTOR_4 = 63
    CURRENT_METER_ID_ESC_MOTOR_5 = 64
    CURRENT_METER_ID_ESC_MOTOR_6 = 65
    CURRENT_METER_ID_ESC_MOTOR_7 = 66
    CURRENT_METER_ID_ESC_MOTOR_8 = 67
    CURRENT_METER_ID_ESC_MOTOR_9 = 68
    CURRENT_METER_ID_ESC_MOTOR_10 = 69
    CURRENT_METER_ID_ESC_MOTOR_11 = 70
    CURRENT_METER_ID_ESC_MOTOR_12 = 71
    CURRENT_METER_ID_ESC_MOTOR_20 = 79
    CURRENT_METER_ID_VIRTUAL_1 = 80       # 80-89 for virtual meters
    CURRENT_METER_ID_VIRTUAL_2 = 81
    CURRENT_METER_ID_MSP_1 = 90       # 90-99 for MSP meters
    CURRENT_METER_ID_MSP_2 = 91


    MOTOR_MIN = 1000
    MOTOR_MAX = 2000
    ARM_VALUE = 1990
    RATE_MODE = 1990
    STATE_DISARMED = 0
    STATE_ARMED = 1
    STATE_ARM_READY = 2

    def __init__(self, dstAddress, baudrate = 115200):
        self.ser = serial.Serial()
        self.ser.port = dstAddress
        self.ser.baudrate = baudrate
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.parity = serial.PARITY_NONE
        self.ser.stopbits = serial.STOPBITS_ONE
        self.ser.timeout = 0
        self.ser.xonxoff = False
        self.ser.rtscts = False
        self.ser.dsrdtr = False
        self.ser.writeTimeout = 2

        self.flight_state = self.STATE_DISARMED

        signal.signal(signal.SIGINT, self.abort)

    def connect(self):
        """Time to wait until the board becomes operational"""
        wakeup = 2
        try:
            self.ser.open()
            print("Waking up board on "+self.ser.port+"...")
            for i in range(1,wakeup):
                    time.sleep(1)
        except Exception as error:
            print("\n\nError opening "+self.ser.port+" port.\n"+str(error)+"\n\n")

    def close(self):
        self.ser.close()
        sys.exit()

    def write(self, message):
        return self.ser.write(message)

    def sendCMD(self, data_length, code, data):
        checksum = 0
        total_data = [b'$', b'M', b'<', data_length, code] + data
        for i in struct.pack('<2B%dH' % len(data), *total_data[3:len(total_data)]):
            checksum = checksum ^ i
        total_data.append(checksum)
        message = struct.pack('<3c2B%dHB' % len(data), *total_data)
        self.ser.write(message)
        self.ser.flush()


    def is_checksum_valid(self, data, checksum):
        computed = 0
        for i in data :
            computed = computed ^ i
        return computed == checksum

    def read(self):
        # <preamble>,<direction>,<size>,<command>,,<crc>
        state = 0
        # Get the header: preamble and direction 
        while True:
            header = self.ser.read()
            if state == 0 and header == b'$':
                state = 1
            elif state == 1 and header == b'M':
                state = 2 
            elif state == 2 and header == b'>':
                break
            else:
                pass

        b = self.ser.read()
        if len(b) == 1:
            datalength = struct.unpack('<B', b)[0]
            #print ("Len=", datalength)
        else:
            return None

        # The command id
        b = self.ser.read()
        if len(b) == 1:
            code = struct.unpack('<B', b)
            #print ("Code = ", code)
        else:
            return None

        payload = self.ser.read(datalength)
        if len(payload) != datalength:
            #print ("Actual Len=", len(payload))
            return None

        b = self.ser.read()
        if len(b) == 1:
            crc = struct.unpack('<B', b)
            #print ("Crc=", crc)
        else:
            return None

        self.ser.flushInput()
        self.ser.flushOutput()

        return payload

    def get_voltage(self):
        print ("Start read voltage")
        try:
            self.sendCMD(0, MSP_VOLTAGE_METERS, [])
            payload = self.read()
            if not payload:
                return None
            #print ("Payload=", len(payload))
            decoded = struct.unpack('<' + 'b'*len(payload), payload)
            #assert len(decoded) % 2 == 0
            voltage_meters = [] 
            for i in range(int(len(decoded)/2)):
                voltage_meter = {}
                voltage_meter["id"] = decoded[i *2]
                voltage_meter["value"] = decoded[i *2 + 1]
                voltage_meters.append(voltage_meter)
            print ("t=", time.time(), " Voltage=", voltage_meters)
            print ("End read voltage")
            return voltage_meters
        except Exception as e:
            print ("Exception reading voltage ", e)
            pass

    def get_current(self):
        print ("Start read current")
        try:
            self.sendCMD(0, MSP_CURRENT_METERS, [])
            payload = self.read()
            if not payload:
                return None
            decoded = struct.unpack('<' + 'b'*len(payload), payload)
            #print ("Decoded=", decoded)
            #assert len(decoded) % 5 == 0
            current_meters = [] 
            for i in range(int(len(payload)/5)):
                current_meter = {}
                _id, mAhr, mA  = struct.unpack('<' + 'BHH', payload[i*5:i*5 + 5])
                current_meter["id"] = _id
                current_meter["mAhr"] = mAhr
                current_meter["mA"] = mA
                current_meters.append(current_meter)
            print ("t=", time.time()," Current=", current_meters)
        except:
            pass
        print ("End read current")

    def get_status(self):
        self.sendCMD(0, MSP_STATUS, [])
        payload = self.read()
        if not payload:
            return None
        unpacked = struct.unpack("<3HIB2HB", payload[:16])
        msg = MSPStatusMessage()#direction=message.direction, size=message.size, data=message.data)

        msg.dt = unpacked[0]
        msg.ic2_error_count = unpacked[1]
        msg.sensors = unpacked[2]
        msg.flight_mode_flags = unpacked[3]
        msg.pid_profile_index = unpacked[4]
        msg.system_load = unpacked[5]
        msg.gyro_cycle_time = unpacked[6]
        msg.size_conditional_flight_mode_flags = unpacked[7]

        # Second stage, conditional
        unpacked2 = None
        if msg.size_conditional_flight_mode_flags > 0:
            unpacked2 = struct.unpack("<{}BBI".format(msg.size_conditional_flight_mode_flags), payload[16:])
            msg.conditional_flight_mode_flags = unpacked2[:msg.size_conditional_flight_mode_flags]
            msg.num_disarming_flags = unpacked2[msg.size_conditional_flight_mode_flags ]
            msg.arming_disabled_flags = unpacked2[msg.size_conditional_flight_mode_flags + 1]
        else:
            unpacked2 = struct.unpack("<BI", payload[16:])

            msg.num_disarming_flags = unpacked2[0]
            msg.arming_disabled_flags = unpacked2[1]

        self.status_callback(msg)

    def status_callback(self, status):
        #print("CALLBACK ", status.flight_mode_flags, "disable flags = ", status.arming_disabled_flags, " disable flag names ", status.get_arming_disabled_flags_by_name(), " enabled ", status.get_enabled_boxes())
        if self.flight_state == self.STATE_DISARMED and status.arming_disabled_flags == 0:
            self.flight_state = self.STATE_ARM_READY
            self.message = MSPSetRawRCMessage(aux1=self.ARM_VALUE, aux2=self.RATE_MODE)
            print("Arming...")
        elif self.flight_state == self.STATE_ARM_READY and "BOXARM" in status.get_enabled_boxes():
            self.flight_state = self.STATE_ARMED
            #self.message = MSPSetRawRCMessage(r=1600, aux1=self.ARM_VALUE, aux2=self.RATE_MODE)
        elif self.flight_state == self.STATE_ARMED:
            self.message = MSPSetRawRCMessage(aux1=self.ARM_VALUE, aux2=self.RATE_MODE, max_r_rate=400, max_p_rate=400, max_y_rate=400)
            self.message.set_r_rate(200)
            print("Armed, sending command ", self.message)

    def get_enabled_boxes(self):
        names = []
        bits = list(reversed("{0:b}".format(self.flight_mode_flags)))
        #logger.debug("Modes={} to bits= {}", self.flight_mode_flags, bits)
        for i in range(len(bits)):
            if bits[i] == "1":
                names.append(self.BOX_NAMES[i])
        return names

    def abort(self, signal, frame):
        print ("Aborting!")
        cmd = [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000]
        self.sendCMD(16, MSP_SET_MOTOR, cmd)
        self.close()


    def ramp(self, motor_id, start, end, duration):
        """
        Args: 
            motor_id: 0-7 indicated by the betaflight mixer
            start: value 1000 to 2000
            end: value 1000 to 2000
            duration: time in seconds
        """

        # We can only work in full integer steps so we are limited
        # to a max of 1000 steps during a time period
        motor_range = abs(end - start)
        delta_motor_value = 1 if end - start > 0 else -1
        delay = duration/motor_range
        cmd = [self.MOTOR_MIN]*8
        step = 1
        motor_value = start
        while  step <= motor_range:
            cmd[motor_id] = motor_value
            board.sendCMD(16, MSP_SET_MOTOR, cmd)
            time.sleep(delay)
            motor_value += delta_motor_value
            step += 1

def get_voltage_by_id(voltages, _id):
    for v in voltages:
        if v["id"] == _id:
            return v["value"]/10.0
    return None

def get_current_by_id(currents, _id):
    for c in currents:
        if c["id"] == _id:
            return c["mAh"]
    return None



def test1():
    board = None
    try:
        board = MSP("/dev/ttyACM0")
        signal.signal(signal.SIGINT, board.abort)
        board.connect()

        while True:
            #board.getData(MultiWii.RAW_IMU)
            #print board.rawIMU

            #board.get_status()
            board.get_current()
            board.get_voltage()

            cmd = [1000, 1000, 1070, 1000, 1000, 1000, 1000, 1000]
            board.sendCMD(16, MSP_SET_MOTOR, cmd)

            time.sleep(0.01)
            #board.getData(MultiWii.ANALOG)
            #print ("START Get voltage")
            #voltages = board.get_voltage()
            #if voltages:
            #    vbat = get_battery_voltage_by_id(voltages, MSP.VOLTAGE_METER_ID_BATTERY_1)

            #currents = board.get_current()
            #if currents:
            #    i = get_current_by_id(MSP.CURRENT_METER_ID_BATTERY_1)
    except Exception as e:
        print ("Exception ", e)
        if board:
            # Stop spinning
            cmd = [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000]
            board.sendCMD(16, MSP_SET_MOTOR, cmd)
            board.close()

if __name__ == "__main__":

    board = None
    try:
        board = MSP("/dev/ttyACM0")
        board.connect()

        board.ramp(0)
    except Exception as e:
        print ("Exception ", e)
        if board:
            # Stop spinning
            cmd = [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000]
            board.sendCMD(16, MSP_SET_MOTOR, cmd)
            board.close()

