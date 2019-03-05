import serial, time, struct
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
        pass

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
        self.sendCMD(0, 128, [])
        payload = self.read()
        if not payload:
            return None
        decoded = struct.unpack('<' + 'b'*len(payload), payload)
        #print ("Decoded=", decoded)
        assert len(decoded) % 2 == 0
        voltage_meters = [] 
        for i in range(int(len(decoded)/2)):
            voltage_meter = {}
            voltage_meter["id"] = decoded[i *2]
            voltage_meter["value"] = decoded[i *2 + 1]
            voltage_meters.append(voltage_meter)
        #print (voltage_meters)
        return voltage_meters

    def get_current(self):
        self.sendCMD(0, 129, [])
        payload = self.read()
        if not payload:
            return None
        decoded = struct.unpack('<' + 'b'*len(payload), payload)
        #print ("Decoded=", decoded)
        assert len(decoded) % 5 == 0
        current_meters = [] 
        for i in range(int(len(payload)/5)):
            current_meter = {}
            _id, mAhr, mA  = struct.unpack('<' + 'BHH', payload[i*5:i*5 + 5])
            current_meter["id"] = _id
            current_meter["mAhr"] = mAhr
            current_meter["mA"] = mA
            current_meters.append(current_meter)
        #print (current_meters)




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

if __name__ == "__main__":

    board = MSP("/dev/ttyACM0")
    board.connect()

    while True:
        #board.getData(MultiWii.RAW_IMU)
        #print board.rawIMU

        cmd = [1080, 1000, 1000, 1000, 1000, 1000, 1000, 1000]
        board.sendCMD(16, 214, cmd)
        #time.sleep(0.01)
        #board.getData(MultiWii.ANALOG)
        #print ("START Get voltage")
        #voltages = board.get_voltage()
        #if voltages:
        #    vbat = get_battery_voltage_by_id(voltages, MSP.VOLTAGE_METER_ID_BATTERY_1)

        #currents = board.get_current()
        #if currents:
        #    i = get_current_by_id(MSP.CURRENT_METER_ID_BATTERY_1)


