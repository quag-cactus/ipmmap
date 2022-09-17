## Description

IPMMAP(Inter-Process Mmap) is a python library of inter-process communication with exclusivity for multiprocesses that are independent of each other. This library is based on the [mmap object](https://docs.python.org/3/library/mmap.html) provided by The Python Standard Library.

This library provides:
* Shared memory access classes provided per permission (manager, editor, reader)
* Reader-Writer LOCK (using [fasteners](https://github.com/harlowja/fasteners))
* class-based and inheritable shared data structures using [ctypes.structure](https://docs.python.org/ja/3/library/ctypes.html)

## Dependencies
* python >= 3.8.x
* fasteners >= 0.17.x

## Overview

1. clone and pip install
    ```sh
    git clone https://github.com/quag-cactus/ipmmap.git
    ```
    ```
    pip install fasteners
    ```
    
    If you want to execute it anyway, you can [run demo scripts](#executing-demo-scripts).

1. Code `ctypes.Structure` for Ipmmap that extends `base_struct.BaseMmapStructure` to define your shared memory structure.
    ```py
    # demo_struct.py

    import ctypes

    from ipmmap.struct import base_struct as bs

    # point-2d structure
    class Point2D(ctypes.Structure):
        _fields_ = (
            ('x', ctypes.c_double), 
            ('y', ctypes.c_double),
        )

    class DemoMmapStructure(bs.BaseMmapStructure):
        _fields_ = (
            ('header', bs.MmapStructureHeader),
            ('data_int', ctypes.c_int32),
            ('data_string', ctypes.c_char * 256),
            ('data_xy', Point2D),
        )

    ```


1. Register the modules that is defined IpmmapStructure, when you use IPMMAP classes
    ```py

    from ipmmap import DataStructMmapEditor

    # regist All Structures extends BaseMmapStructure in demo_struct.py
    DataStructMmapEditor.setUserStructs(["demo_struct"])

    ```

1. Create IPMMAP files
    - By instantiating DataStructMmapManager, a IPMMAP file -- the physical entity of the memory mapping space -- can be created.
    - `DataStructMmapManager` is the only class that can create a new mmap file.
    - `DataStructEditor` and `DataStructReader` can only be used in IPMMAP Structure where a IPMMAP file already exists.

    ```py

    from ipmmap import DataStructMmapManager

    DataStructMmapEditor.setUserStructs(['demo_struct'])

    manager = DataStructMmapManager('DemoMmapStructure', mmapDir='./', create=True, force=True)

    ```

1. Edit a shared memory space of IPMMAP: 
    - `writeData()` of The `DataStructMmapEditor` can edit the shared memory space.
    - The with statement can be used to edit a value exclusively with write lock, in appropriate resource managing.
    - No other process can refer to the shared memory space of IPMMAP while with satement is running.

    ```py

    from ipmmap import DataStructMmapEditor

    DataStructMmapEditor.setUserStructs(["demo_struct"])
    with DataStructMmapEditor("DemoMmapStructure") as editor:

        editor.writeData('data_int', 1)
        editor.writeData('data_string', bytes('hello world!', 'utf-8'))
        # supported attribute of nested Structure 
        edirot.writeData('data_xy.x', 99)

    ```

1. Read a shared memory space of IPMMAP
    - `readData()` of The `DataStructMmapReader` can edit the shared memory space.

    ```py

    from ipmmap import DataStructMmapReader

    DataStructMmapReader.setUserStructs(["demo_struct"])
    with DataStructMmapReader("DemoMmapStructure") as reader:
        print(reader.readData('data_int'))
        print(reader.readData('data_string'))
        print(reader.readData('data_xy.x'))

    ```

## Executing Demo scripts

let's check multiple processes can share the value.

1. Execute demo_editor.py
    * `demo_editor.py` map to the address space the entity file (.mmap) that defined at `DemoMmapStructure` in `demo_struct.py`.
    * It accesses the shared address space with **editor privileges** and rewrites the values randomly repeatedly in a loop.
    ```
    python demo_editor.py
    ```

2. Open new terminal, and execute demo_reader.py
   * It accesses the shared address space with **reader privileges** and read the value.
   ```
   python demo_reader.py
   ```

## List of IPMMAP Classes 

Accessing To shared-memory address space in IPMMAP library, separate 3 classes By Authority.

| class                 | authority                                             | lock type (using with statement)                         | 
| --------------------- | ----------------------------------------------------- | -------------------------------------------------------- | 
| DataStructMmapManager | create mmap file, read and write mapped memory space. | WriterLock<br>(write_lock(): fasteners.InterProcessLock) | 
| DataStructMmapEditor  | read and write mapped memory space.                   | WriterLock<br>(write_lock(): fasteners.InterProcessLock) | 
| DataStructMmapReader  | read mapped memory space.                             | ReaderLock<br>(read_lock(): fasteners.InterProcessLock)  | 


