from record_data import MSP
from msp_protocol import *

if __name__ == "__main__":

    board = None
    try:
        board = MSP("/dev/ttyACM0")
        board.connect()

        board.ramp(0, 1000, 2000, 1)
    except Exception as e:
        print ("Exception ", e)
        if board:
            # Stop spinning
            cmd = [MSP.MOTOR_MIN]*8
            board.sendCMD(16, MSP_SET_MOTOR, cmd)
            board.close()

