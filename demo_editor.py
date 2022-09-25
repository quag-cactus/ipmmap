"""demo script using edit-mode of ipmmap

"""

import sys
import time
import signal
import random
import uuid
import datetime

from ipmmap import DataStructMmapManager, DataStructMmapEditor

def Main():

    # SIGNAL HANDLER for closing memory mapping when the process interrupted.
    def handler(signum, frame):
        print("process intrrupted: {}".format(signum))
        manager.closeMemory()
        print("mmap released")
        sys.exit(1)

    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

    # 1. resgist your IPMMAP Structure module-path.
    DataStructMmapEditor.setUserStructs(["demo_struct"])

    # 2. call manager class for your IPMMAP Structure. 
    manager = DataStructMmapManager("DemoMmapStructure", create=True, force=True)

    # 3. map the ipmmap file to memory.
    manager.openMemory()
    print("memory mapped: ", manager.mmapFilePath)

    # 4. edit mmap file.
    while True:

        t = time.perf_counter()
        with DataStructMmapEditor("DemoMmapStructure") as editor:

            data_int = random.randint(0, 100)
            data_string = str(uuid.uuid1())
            x = random.random() * 100
            y = random.random() * 100
            
            # edit value of your IPMMAP Stracture 
            editor.writeData("data_int", data_int)
            editor.writeData("data_string", bytes(data_string, 'utf-8'))
            editor.writeData("data_xy.x", x)
            editor.writeData("data_xy.y", y)

            # update last-update time
            editor.updateLastUpdate()

            print("------INSERT TO SHARED MEM------")
            print("[last update] {}".format(datetime.datetime.fromtimestamp(editor.getLastUpdate())))
            print("[data_int] {}".format(data_int))
            print("[data_string] {}".format(data_string))
            print("[data_xy] x: {}, y: {}".format(x, y))

        print("performance: {:.4f} ms".format((time.perf_counter() -t) * 1000))
        time.sleep(1)

if __name__ == "__main__":
    Main()