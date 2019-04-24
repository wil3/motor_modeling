from record_data import MSP
from msp_protocol import *
import time
import numpy as np

if __name__ == "__main__":

    board = None
    try:

        board = MSP("/dev/ttyACM0")
        board.connect()
        data = []
        for i in range(5000):
            status = board.get_status2()
            print (status.system_load)
            time.sleep(0.01)
            data.append(status.system_load)

        arr = np.array(data)
        print("Average=", np.mean(arr))
        print("Min=", np.amin(arr))
        print("Max=", np.amax(arr))

    except Exception as e:
        print ("Exception ", e)
        if board:
            # Stop spinning
            cmd = [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000]
            board.sendCMD(16, MSP_SET_MOTOR, cmd)
            board.close()

