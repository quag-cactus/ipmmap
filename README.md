## Description

IPMMAP(Inter-Process Mmap) is a python library of inter-process communication with exclusivity for multiprocesses that are independent of each other. This library is based on the [mmap object](https://docs.python.org/3/library/mmap.html) provided by The Python Standard Library.

This library provides:
* Shared memory access classes provided per permission (manager, editor, reader)
* Read-Write exclusivity (using [fasteners](https://github.com/harlowja/fasteners))
* class-based and inheritable shared data structures using [ctypes.structure](https://docs.python.org/ja/3/library/ctypes.html)

## dependencies
* python >= 3.8.x
* fasteners >= 0.17.x

## Usage(demo scripts)

let's check multiple processes can share the value.

1. execute demo_manager.py
    * `demo_manager.py` map to the address space the entity file (.mmap) that defined at `DemoMmapStructure` in `demo_struct.py`.
    * It accesses the shared address space with **editor privileges** and rewrites the values randomly repeatedly in a loop.
    ```
    python demo_manager.py
    ```

2. open new terminal, and execute demo_reader.py
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


