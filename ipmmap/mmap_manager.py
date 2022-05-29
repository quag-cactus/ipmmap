
import io
import time
import mmap
import logging
import pathlib
from abc import ABCMeta

import fasteners

from .struct import base_struct

DEFAULT_MMAP_FILE_DIR = "./.mmap"
DEFAULT_FASTENERS_FILE_DIR = "./.fasteners"

DEFAULT_LOGGER = logging.getLogger(__name__)

class AbstractMmapManger(metaclass=ABCMeta):

    def __init__(self, mmapDir: pathlib.Path=None, fastenerDir: pathlib.Path=None, logger: logging.Logger=None):
        print(">>> abc init called...")
        self.mmapFilePath = None
        self.fastenerFilePath = None
        self.editable = False
        self.mm = None
        self.logger = self._getLogger(logger)

        # make mmap dir
        self._getUseFDir(DEFAULT_MMAP_FILE_DIR, mmapDir).mkdir(exist_ok=True)
        # make fastener dir
        self._getUseFDir(DEFAULT_FASTENERS_FILE_DIR, fastenerDir).mkdir(exist_ok=True)


    def _getLogger(self, argsLogger):
        return DEFAULT_LOGGER if argsLogger is None else argsLogger


    def _getUseFDir(self, defaultDir, argsDir):
        return pathlib.Path(defaultDir).resolve() if argsDir is None else argsDir


    def __enter__(self):

        self.rw_lock = fasteners.InterProcessReaderWriterLock(self.fastenerFilePath)

        if self.editable:
            fileMode = 'r+b'
            self.rw_lock.acquire_write_lock()
            accessMode = mmap.ACCESS_DEFAULT
        else:
            fileMode = 'r'
            self.rw_lock.acquire_read_lock()
            accessMode = mmap.ACCESS_READ

        self.fs = open(self.mmapFilePath, fileMode)
        self.mm = mmap.mmap(self.fs.fileno(), 0, access=accessMode)
        self.mm.seek(0)

        self.logger.info(">>> enter with block")
        
        return self


    def __exit__(self, e_type, e_value, traceback):
        self.mm = None
        self.fs.close()

        if self.editable:
            self.rw_lock.release_write_lock()
        else:
            self.rw_lock.release_write_lock()

        self.logger.info(">>> exit with block")


class BaseStructMmapManager(AbstractMmapManger):
    
    # コンストラクタ
    def __init__(self, structName: str, mmapDir: pathlib.Path=None, fastenerDir: pathlib.Path=None):
        super().__init__(mmapDir, fastenerDir)
        self.structType = self._searchStructType(structName)
        self.mmapFilePath = (self._getUseFDir(DEFAULT_MMAP_FILE_DIR, mmapDir) / self.structType.__name__).with_suffix('.mmap').resolve()
        self.fastenerFilePath = (self._getUseFDir(DEFAULT_FASTENERS_FILE_DIR, fastenerDir) / self.structType.__name__).with_suffix('.lockfile').resolve()


    # マッピングデータ部構造体定義検索関数
    def _searchStructType(self, structName: str):
        for st in base_struct.BaseMmapStacture.__subclasses__():
            if structName == st.__name__:
                return st

        # 指定された構造体が存在しない場合は独自エラー


    # マッピングデータ部構造体生成関数
    def _generateStruct(self):
        return self.structType(base_struct.MmapStructureHeader(0x1128, time.time()))


    # マッピング用ファイル生成関数
    def _createNewMmapFile(self, dataStruct):
        try:
            with open(self.mmapFilePath, "wb") as fs:
                fs.write(dataStruct)
        except Exception as e: 
            pass


    # 最終更新時刻取得関数
    def getLastUpdate(self) -> float:
        if not self.mm is None:
            self.mm.seek(0)
            mmData = self.structType.from_buffer_copy(self.mm)
            return mmData.header.time_stamp
        else:
            return -1


class BasePickleMmapManager(AbstractMmapManger):
    def __init__(self, mmapDir: pathlib.Path, tagName: str):
        super().__init__(mmapDir)
        self.mmapFilePath =  (mmapDir / tagName).with_suffix('.mmap').resolve()

    # マッピング用ファイル生成関数
    def _createNewMmapFile(self, binData):

        try:
            with open(self.mmapFilePath, "wb") as fs:
                fs.write(binData)
        except Exception as e: 
            pass
