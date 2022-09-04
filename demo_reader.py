"""demo script using read-only-mode of ipmmap

"""

import time
import datetime

from ipmmap import DataStructMmapReader

def Main():

    DataStructMmapReader.setUserStructs(["demo_struct"])

    # read mmap file
    while True:

        with DataStructMmapReader("DemoMmapStructure") as reader:
            lastUpdateTime = datetime.datetime.fromtimestamp(reader.getLastUpdate())

            data_int = reader.readData('data_int')
            data_string = reader.readData('data_string')
            pts = reader.readData('data_xy')

            print("----------------------------------")
            print("[lastupdate] {}".format(lastUpdateTime))
            print("[data_int] {}".format(data_int))
            print("[data_string] {}".format(data_string))
            print("[data_xy] x: {}, y: {}".format(pts.x, pts.y))

        time.sleep(1)

    

if __name__ == "__main__":
    Main()