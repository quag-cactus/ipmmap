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

                # Reading shared memory easily
                data_int = reader.readData('data_int')
                data_string = reader.readData('data_string')
                pts_x = reader.readData('data_xy.x')
                pts_y = reader.readData('data_xy.y')

                # Reading shared memory manualy, you can read deep nested attributes
                buf = reader.readMappedBuffer()
                multi_0_x = buf.multi_pts.multi_points[0].x
                multi_0_y = buf.multi_pts.multi_points[0].y

                print("------SHARED MEM UPDATED!------")
                print("[last update] {}".format(lastUpdateTime))
                print("[data_int] {}".format(data_int))
                print("[data_string] {}".format(data_string))
                print("[data_xy] x: {}, y: {}".format(pts_x, pts_y))
                print("[multiPoints(index: [0])] x: {}, y: {}".format(multi_0_x, multi_0_y))

                lastestUpdateTime = updateTime

        time.sleep(0.1)

    

if __name__ == "__main__":
    Main()