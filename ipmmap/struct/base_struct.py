
import ctypes

# プロセス間共有メモリ向けメモリマップ構造体（ベース）
# サブクラスの検索を容易にするために宣言している空の継承クラスです。
class BaseMmapStructure(ctypes.Structure):
    pass

# メモリマップ構造体の共通ヘッダ
class MmapStructureHeader(ctypes.Structure):
    _fields_ = (
        ('header_code', ctypes.c_short),    # MmapMangerの共有メモリデータであることを示すバイト列
        ('time_stamp', ctypes.c_double),    # タイムスタンプ（作成時・更新時に変更する必要があります）
    )

# 二次元座標構造体
class Point(ctypes.Structure):
    _fields_ = (
        ('x', ctypes.c_double), 
        ('y', ctypes.c_double),
    )


