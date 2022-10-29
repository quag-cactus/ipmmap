"""MmapManager for ctypes.Structure
"""

import time
import pathlib
import importlib
import mmap
import ctypes
from typing import Any

from .mmap_manager import AbstractMmapManger, DEFAULT_MMAP_FILE_DIR, DEFAULT_FASTENERS_FILE_DIR
from .struct import base_struct
from .exception import ipmmap_error as Err 

HEADER_UNIQUE_BYTES = 0x1128

class BaseStructMmapManager(AbstractMmapManger):
    """Base class for StructMmapReader, Editor and Manager"""

    @staticmethod
    def setUserStructs(moduleNameList):
        for name in moduleNameList:
            importlib.import_module(name)

    def __init__(self, structName: str, tag: str="", mmapDir: pathlib.Path=None, fastenerDir: pathlib.Path=None):
        super().__init__(mmapDir, fastenerDir)
        self.structType = self._searchStructType(structName)
        fileName = "{}_{}".format(self.structType.__name__, tag)
        self.mmapFilePath = (self._getUseFDir(DEFAULT_MMAP_FILE_DIR, mmapDir) / fileName).with_suffix('.mmap').resolve()
        self.fastenerFilePath = (self._getUseFDir(DEFAULT_FASTENERS_FILE_DIR, fastenerDir) / fileName).with_suffix('.lockfile').resolve()


    def _searchStructType(self, structName: str):
        for st in base_struct.BaseMmapStructure.__subclasses__():
            if structName == st.__name__:
                return st

        raise Err.StructNotFoundIpMmapError(structName)


    def getLastUpdate(self) -> float:
        """Returns last-update time of IPMMAP's shared memory as the UNIX epoch time (float).

        This time can edit only DataStructMmapEditor.updateLastUpdate().
        The default value of last-update time is 0.

        Returns:
            float: UNIX epoch time
        """
        if not self.mm is None:
            self.mm.seek(0)
            mmData = self.structType.from_buffer_copy(self.mm)
            return mmData.header.time_stamp
        else:
            return -1

class DataStructMmapReader(BaseStructMmapManager):
    """IPMMAP handler class with a reader privilege."""

    def __init__(self, structName: str, tag: str="", mmapDir: pathlib.Path=None, fastenerDir: pathlib.Path=None):
        """Initializer of DataStructMmapReader.

        Args:
            structName (str): String of a IPMMAP Structure's name that you want to map.
            tag (str, optional): String of a tag name for multiple memory mapping by same IPMMAP Structures. Defaults to "".
            mmapDir (pathlib.Path, optional): Directory path of the mmap file located. Defaults to None(current directory).
            fastenerDir (pathlib.Path, optional): Directory path of the fasteners locking file located. Defaults to None(current directory).
        """

        super().__init__(structName, tag, mmapDir, fastenerDir)
        self.editable = False

        # mmapオブジェクトを取得

    def readData(self, key: str) -> any:
        """Returns a value of designated a key-string any IPMMAP Structure's fields. 

        Args:
            key (str): string of the IPMMAP Structure's field name

        Returns:
            any: value
        """
        self.mm.seek(0)
        mmData = self.structType.from_buffer_copy(self.mm)

        val = mmData
        for k in key.split('.'):
            val = getattr(val, k)

        return val

    def readMappedBuffer(self):
        """Return a IPMMAP's Structure object that is copied from shared memory fields.

        Returns:
            ctypes.Structure: copied IPMMAP's Structure object
        """

        mmData = None
        if not self.mm is None:
            self.mm.seek(0)
            mmData = self.structType.from_buffer_copy(self.mm)
        return mmData


class DataStructMmapEditor(DataStructMmapReader):
    """IPMMAP handler class with a editor privilege."""

    def __init__(self, structName: str, tag: str="", mmapDir: pathlib.Path=None, fastenerDir: pathlib.Path=None):
        """Initializer of DataStructMmapEditor.

        Args:
            structName (str): String of a IPMMAP Structure's name that you want to map.
            tag (str, optional): String of a tag name for multiple memory mapping by same IPMMAP Structures. Defaults to "".
            mmapDir (pathlib.Path, optional): Directory path of the mmap file located. Defaults to None(current directory).
            fastenerDir (pathlib.Path, optional): Directory path of the fasteners locking file located. Defaults to None(current directory).
        """

        super().__init__(structName, tag, mmapDir, fastenerDir)
        self.editable = True


    def updateLastUpdate(self) -> None:
        """Update last update time of the IPMMAP's shared memory.
        """
        if not self.mm is None:
            self.mm.seek(0)
            mmData = self.structType.from_buffer(self.mm)
            mmData.header.time_stamp = time.time()

        return

    def writeData(self, key: str, value: Any) -> None:
        """Set a value of designated a key-string any IPMMAP Structure's fields

        Args:
            key (str): String of a IPMMAP Structure's field name
            value (Any): Value to write for IPMMAP's shared memory space
        """
        if not self.mm is None:
            self.mm.seek(0)
            mmData = self.structType.from_buffer(self.mm)

            keyList = key.split('.')

            # set recursive
            attr = mmData
            for k in keyList[:-1]:
                attr = getattr(attr, k)
                
            setattr(attr, keyList[-1], value)

        return

    def referMappedBuffer(self):
        """Return a IPMMAP's Structure object that is refered shared memory fields.
        You can edit shared memory field directory, by editing the returned object.
        *caution!* You must remove referrence for shared memory field, before you exit from with statement.

        Returns:
            ctypes.Structure: IPMMAP's Structure object
        """
        if not self.mm is None:
            self.mm.seek(0)
            return self.structType.from_buffer(self.mm)
        else:
            return None   

    def clearMappedBuffer(self) -> None:
        """Fill IPMMAP's shared memory space with zero.

        This method also fills last-update time with zero.
        """

        if not self.mm is None:
            self.mm.seek(0)
            mmData = self.structType.from_buffer(self.mm)
            ctypes.memset(ctypes.byref(mmData), 0, ctypes.sizeof(mmData))

        return

class DataStructMmapManager(DataStructMmapEditor):
    """IPMMAP handler class with a manager privilege."""

    def __init__(self, structName: str, tag: str="", mmapDir: pathlib.Path=None, fastenerDir: pathlib.Path=None, 
                 create: bool=False, force: bool=False):
        """_Initializer of DataStructMmapEditor.

        Args:
            structName (str): String of a IPMMAP Structure's name that you want to map.
            tag (str, optional): String of a tag name for multiple memory mapping by same IPMMAP Structures. Defaults to "".
            mmapDir (pathlib.Path, optional): Directory path of the mmap file located. Defaults to None(current directory).
            fastenerDir (pathlib.Path, optional): Directory path of the fasteners locking file located. Defaults to None(current directory).
            create (bool, optional): If this is true, a mmap file is created when creating instance. Defaults to False.
            force (bool, optional): If this is true, a mmap file is overwrited when create the mmap file. Defaults to False.
        """

        super().__init__(structName, tag, mmapDir, fastenerDir)
        self.editable = True

        # create new mmap
        if create:
            # if "force" mode, old mmapfile is overwritten 
            if force or (not self.mmapFilePath.exists()):
                self._createNewMmapFile(self._generateStruct())
                # print("file generated: ", self.mmapFilePath)
            else:
                pass
                # print("file already exist")

    def _generateStruct(self):

        dataStruct = None
        try:
            dataStruct = self.structType(base_struct.MmapStructureHeader(HEADER_UNIQUE_BYTES, time.time()))
        except TypeError:
            raise Err.CommonHeaderNotFoundIpMmapError(self.structType.__name__)

        return dataStruct

    def _createNewMmapFile(self, dataStruct):
        try:
            with open(self.mmapFilePath, "wb") as fs:
                fs.write(dataStruct)
        except OSError: 
            raise Err.CreateFileIpMmapError(self.mmapFilePath)

    def openMemory(self):
        """Map explicitly the IPMMAP's structure to shared memory space.

        This method will open both the file object and get the mmap instance.
        if you want to close resources or stop the process, you need to call closeMemory().
        """
        self.fs_master = open(self.mmapFilePath, 'r+b')
        self.mm_master = mmap.mmap(self.fs_master.fileno(), 0, access=mmap.ACCESS_DEFAULT)

        return

    
    def closeMemory(self):
        """Close the file object and the mmap instance explicitly.
        """
        if (not self.mm_master is None) and (not self.mm_master.closed):
            self.mm_master.close()
            self.mm_master = None

        if (not self.fs_master is None):
            self.fs_master.close()

        return


    