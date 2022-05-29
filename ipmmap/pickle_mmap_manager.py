"""メモリマップファイル管理クラス（pickle）
pickleデータを利用したマップファイルは共通ヘッダを持ちません
"""

import pickle
import pathlib

from .mmap_manager import BasePickleMmapManager

class PickleMmapReader(BasePickleMmapManager):

    def __init__(self, mmapDir: pathlib.Path, tagName: str):
        super().__init__(mmapDir, tagName)

class PickleMmapEditor(BasePickleMmapManager):

    def __init__(self, mmapDir: pathlib.Path, tagName: str, targetDict: dict=None, size: int=0, create: bool=False, force: bool=False):
        super().__init__(mmapDir, tagName)
        self.editable = True

        # 新規作成処理
        if create:
            # forceフラグが立っている場合、ファイルが存在していても上書きして作成
            if force or (not self.mmapFilePath.exists()):
                
                # prioritize serialized dict size
                if not targetDict is None:
                    binData = pickle.dumps(targetDict)
                else:
                    binData = bytearray(size)

                self._createNewMmapFile(binData)

                print("file generated: ", self.mmapFilePath)
            else:
                print("file already exist")