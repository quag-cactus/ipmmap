"""demo script using edit-mode of ipmmap

"""

import sys
import time
import pathlib
import argparse
import struct
import ctypes

from ipmmap import DataStructMmapEditor

def Main():
    mmapInfo = [
        {"mmap_file_path": ".\\mmap", "structure_type": "DetectDataMmapStructure"}
    ]

    # create mmap file
    for info in mmapInfo:
        mPath = pathlib.Path(info["mmap_file_path"])
        strctType = info["structure_type"]
        with DataStructMmapEditor(strctType, mmapDir=mPath, create=True) as m:
            pass

    # edit mmap via ipmmap object
    while True:
        for info in mmapInfo:
            mPath = pathlib.Path(info["mmap_file_path"])
            strctType = info["structure_type"]
            # Manager以外で呼び出すこと（managerをabstractにした方がいい？）
            with DataStructMmapEditor(strctType, mmapDir=mPath) as m:
                # 最終更新チェック
                print(m.getLastUpdate())
                # 最終更新アップデート
                m.updateLastUpdate()
        time.sleep(1)

if __name__ == "__main__":
    Main()