"""demo script using edit-mode of ipmmap

"""

import sys
import time
import pathlib
import signal
import argparse
import struct
import ctypes

from ipmmap import DataStructMmapManager, DataStructMmapEditor

def Main():

    managerList: list[DataStructMmapManager] = []

    # close memory mapping
    def handler(signum, frame):
        for manager in managerList:
            manager.closeMemory()
        sys.exit(1)

    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

    mmapInfo = [
        {"mmap_file_path": ".\\.mmap", "structure_type": "DemoMmapStructure"}
    ]

    # add struct module path
    DataStructMmapEditor.setUserStructs(["demo_struct"])

    # create mmap file
    for info in mmapInfo:
        mPath = pathlib.Path(info["mmap_file_path"])
        strctTypeName = info["structure_type"]
        # with DataStructMmapEditor(strctType, mmapDir=mPath, create=True) as m:
        #     pass
        manager = DataStructMmapManager(strctTypeName, mmapDir=mPath, create=True, force=True)
        managerList.append(manager)

    # open managed mmap file
    for manager in managerList:
        manager.openMemory()

    # edit mmap via ipmmap object
    while True:
        for info in mmapInfo:
            mPath = pathlib.Path(info["mmap_file_path"])
            strctTypeName = info["structure_type"]

            with DataStructMmapEditor(strctTypeName, mmapDir=mPath) as m:
                # 最終更新チェック
                print(m.getLastUpdate())
                # 最終更新アップデート
                m.updateLastUpdate()

        print("----------------------")

        time.sleep(1)

if __name__ == "__main__":
    Main()