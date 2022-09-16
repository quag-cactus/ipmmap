"""demo script using read-only-mode of ipmmap

"""

import time
import datetime

from ipmmap import DataStructMmapReader

def Main():

    DataStructMmapReader.setUserStructs(["demo_struct"])

    # read mmap file
    lastestUpdateTime = 0
    while True:
        
        with DataStructMmapReader("DemoMmapStructure") as reader:

            updateTime = reader.getLastUpdate()

            if updateTime > lastestUpdateTime:

                lastUpdateTime = datetime.datetime.fromtimestamp(updateTime)

                data_int = reader.readData('data_int')
                data_string = reader.readData('data_string')
                pts_x = reader.readData('data_xy.x')
                pts_y = reader.readData('data_xy.y')

                print("------SHARED MEM UPDATED!------")
                print("[last update] {}".format(lastUpdateTime))
                print("[data_int] {}".format(data_int))
                print("[data_string] {}".format(data_string))
                print("[data_xy] x: {}, y: {}".format(pts_x, pts_y))

                lastestUpdateTime = updateTime

        time.sleep(0.1)

    

if __name__ == "__main__":
    Main()