"""demo script using read-only-mode of ipmmap

"""

import time
import pathlib

from ipmmap import DataStructMmapReader

def Main():
    mmapInfo = [
        #{"mmap_file_path": ".\\.mmap", "structure_type": "DetectDataMmapStructure"},
        {"mmap_file_path": ".\\.mmap", "structure_type": "DemoMmapStructure"}
    ]

    DataStructMmapReader.setUserStructs(["demo_struct"])

    # reading mmap file
    while True:
        for info in mmapInfo:
            mPath = pathlib.Path(info["mmap_file_path"])
            strctTypeName = info["structure_type"]

            with DataStructMmapReader(strctTypeName, mmapDir=mPath) as m:
                pts = m.readData('data_xy')
                print(pts.x, pts.y)

        print("----------------------")

        time.sleep(1)

    

if __name__ == "__main__":
    Main()