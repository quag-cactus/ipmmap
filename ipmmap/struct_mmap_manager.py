"""メモリマップファイル管理クラス(struct)
"""

import time
import pathlib
import importlib

from .mmap_manager import AbstractMmapManger, DEFAULT_MMAP_FILE_DIR, DEFAULT_FASTENERS_FILE_DIR
from .struct import base_struct
from .exception import ipmmap_error as Err 


class BaseStructMmapManager(AbstractMmapManger):

    @staticmethod
    def setUserStructs(moduleNameList):
        for name in moduleNameList:
            importlib.import_module(name)

    
    # コンストラクタ
    def __init__(self, structName: str, mmapDir: pathlib.Path=None, fastenerDir: pathlib.Path=None):
        super().__init__(mmapDir, fastenerDir)
        self.structType = self._searchStructType(structName)
        self.mmapFilePath = (self._getUseFDir(DEFAULT_MMAP_FILE_DIR, mmapDir) / self.structType.__name__).with_suffix('.mmap').resolve()
        self.fastenerFilePath = (self._getUseFDir(DEFAULT_FASTENERS_FILE_DIR, fastenerDir) / self.structType.__name__).with_suffix('.lockfile').resolve()


    # マッピングデータ部構造体定義検索関数
    def _searchStructType(self, structName: str):
        for st in base_struct.BaseMmapStacture.__subclasses__():
            print(st.__name__)
            if structName == st.__name__:
                return st

        # 指定された構造体が存在しない場合は独自エラー
        raise Err.StructNotFoundIpMmapError(structName)


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


# 読み出し専用クラス
class DataStructMmapReader(BaseStructMmapManager):
    def __init__(self, structName: str, mmapDir: pathlib.Path=None, fastenerDir: pathlib.Path=None):
        super().__init__(structName, mmapDir, fastenerDir)
        self.editable = False

        # mmapオブジェクトを取得

    def readData(self, key):
        pass


# 編集クラス（新規作成権限あり）
class DataStructMmapEditor(DataStructMmapReader):
    def __init__(self, structName: str, mmapDir: pathlib.Path=None, fastenerDir: pathlib.Path=None, create: bool=False, force: bool=False):
        super().__init__(structName, mmapDir, fastenerDir)
        self.editable = True

        # 新規作成処理
        if create:
            # forceフラグが立っている場合、ファイルが存在していても上書きして作成
            if force or (not self.mmapFilePath.exists()):
                self._createNewMmapFile(self._generateStruct())
                print("file generated: ", self.mmapFilePath)
            else:
                print("file already exist")

        # mmapオブジェクトを取得

    # 最終更新時刻更新関数
    def updateLastUpdate(self) -> None:
        if not self.mm is None:
            self.mm.seek(0)
            mmData = self.structType.from_buffer(self.mm)
            print("GET:", getattr(mmData.header, "time_stamp"))
            mmData.header.time_stamp = time.time()

    def writeData(self, key):
        pass