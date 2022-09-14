"""demo script using edit-mode of ipmmap

"""

import time
import random
import uuid
import datetime

from ipmmap import DataStructMmapEditor

def Main():

    DataStructMmapEditor.setUserStructs(["demo_struct"])

    # edit mmap file
    while True:

        with DataStructMmapEditor("DemoMmapStructure") as editor:

            data_int = random.randint(0, 100)
            data_string = str(uuid.uuid1())
            x = random.random() * 100
            y = random.random() * 100
            
            # edit 
            editor.writeData("data_int", data_int)
            editor.writeData("data_string", bytes(data_string, 'utf-8'))

            # edit mmap buffer directly
            buf = editor.referMappedBuffer()
            buf.data_xy.x = x
            buf.data_xy.y = y

            # you need release reference of buffer
            buf = None          

            editor.updateLastUpdate()

            print("----------------------------------")
            print("[lastupdate] {}".format(datetime.datetime.fromtimestamp(editor.getLastUpdate())))
            print("[data_int] {}".format(data_int))
            print("[data_string] {}".format(data_string))
            print("[data_xy] x: {}, y: {}".format(x, y))
            print("updated.")

        time.sleep(1)


if __name__ == "__main__":
    Main()