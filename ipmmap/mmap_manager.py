
import mmap
import logging
import pathlib
from abc import ABCMeta

import fasteners

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
                stat = True

        else:
            fileMode = 'r'
            accessMode = mmap.ACCESS_READ

            if lock:
                self.rw_lock = fasteners.InterProcessReaderWriterLock(self.fastenerFilePath)
                stat = self.rw_lock.acquire_read_lock(blocking=blocking)
            else:
                stat = True

        if stat:
            self.fs = open(self.mmapFilePath, fileMode)
            self.mm = mmap.mmap(self.fs.fileno(), 0, access=accessMode)
            self.mm.seek(0)

        return stat

    def _releaseMmapResource(self, lock=True) -> None:

        if not self.mm is None:
            if not self.mm.closed:
                self.mm.close()
            self.mm = None

        if not self.fs is None:
            self.fs.close()
            self.fs = None

        if self.editable:
            if lock:
                self.rw_lock.release_write_lock()
        else:
            if lock:
                self.rw_lock.release_read_lock()

        return

    def __enter__(self):

        self._acquireMmapResource(lock=True)

        self.logger.info(">>> enter with block")
        
        return self

    def __exit__(self, e_type, e_value, traceback):

        self._releaseMmapResource(True)

        self.logger.info(">>> exit with block")

        return

