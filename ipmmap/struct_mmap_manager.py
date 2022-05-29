"""メモリマップファイル管理クラス(struct)
"""

import time
import pathlib

from .mmap_manager import BaseStructMmapManager

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