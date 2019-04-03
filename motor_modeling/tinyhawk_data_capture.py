from record_data import MSP
from msp_protocol import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Capture motor data")
    parser.add_argument('--port', help="", default="/dev/ttyACM0")

    args = parser.parse_args()
    board = None
    try:
        board = MSP(args.port)
        board.connect()

        board.ramp(0, 1000, 2000, 1)
    except Exception as e:
        print ("Exception ", e)
        if board:
            # Stop spinning
            cmd = [MSP.MOTOR_MIN]*8
            board.sendCMD(16, MSP_SET_MOTOR, cmd)
            board.close()

