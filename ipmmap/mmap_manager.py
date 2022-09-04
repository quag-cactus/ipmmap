
import io
import time
import mmap
import logging
import pathlib
from abc import ABCMeta
from xmlrpc.client import Boolean

import fasteners

from .struct import base_struct
from .exception import ipmmap_error as Err

DEFAULT_MMAP_FILE_DIR = "./.mmap"
DEFAULT_FASTENERS_FILE_DIR = "./.fasteners"

DEFAULT_LOGGER = logging.getLogger(__name__)

class AbstractMmapManger(metaclass=ABCMeta):

    def __init__(self, mmapDir: pathlib.Path=None, fastenerDir: pathlib.Path=None, logger: logging.Logger=None):
        self.mmapFilePath = None
        self.fastenerFilePath = None
        self.editable = False
        self.mm = None
        self.fs = None
        self.logger = self._getLogger(logger)

        # make mmap dir
        self._getUseFDir(DEFAULT_MMAP_FILE_DIR, mmapDir).mkdir(exist_ok=True)
        # make fastener dir
        self._getUseFDir(DEFAULT_FASTENERS_FILE_DIR, fastenerDir).mkdir(exist_ok=True)


    def _getLogger(self, argsLogger):
        return DEFAULT_LOGGER if argsLogger is None else argsLogger

    def _getUseFDir(self, defaultDir, argsDir):
        return pathlib.Path(defaultDir).resolve() if argsDir is None else argsDir

    def _acquireMmapResource(self, lock=True, blocking=True) -> bool:

        stat: bool = False

        if self.editable:
            fileMode = 'r+b'
            accessMode = mmap.ACCESS_DEFAULT

            if lock:
                self.rw_lock = fasteners.InterProcessReaderWriterLock(self.fastenerFilePath)
                stat = self.rw_lock.acquire_write_lock(blocking=blocking)

        else:
            fileMode = 'r'
            accessMode = mmap.ACCESS_READ

            if lock:
                self.rw_lock = fasteners.InterProcessReaderWriterLock(self.fastenerFilePath)
                stat = self.rw_lock.acquire_read_lock(blocking=blocking)

        if stat:
            self.fs = open(self.mmapFilePath, fileMode)
            self.mm = mmap.mmap(self.fs.fileno(), 0, access=accessMode)
            self.mm.seek(0)

        return stat

    def _releaseMmapResource(self, lock=True) -> None:

        self.mm = None
        if not self.fs is None:
            self.fs.close()

        if self.editable:
            if lock:
                self.rw_lock.release_write_lock()
        else:
            if lock:
                self.rw_lock.release_read_lock()

        return

    def __enter__(self):
        """
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
        """
        self._acquireMmapResource(lock=True)

        self.logger.info(">>> enter with block")
        
        return self

    def __exit__(self, e_type, e_value, traceback):

        """
        self.mm = None
        self.fs.close()

        if self.editable:
            self.rw_lock.release_write_lock()
        else:
            self.rw_lock.release_read_lock()
        """
        self._releaseMmapResource(True)

        self.logger.info(">>> exit with block")

        return

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