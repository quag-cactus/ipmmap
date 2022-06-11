import ctypes

from ipmmap.struct import base_struct as bs

class DemoMmapStructure(bs.BaseMmapStacture):
    _fields_ = (
        ('header', bs.MmapStructureHeader),
        ('data_1', ctypes.c_int32),
        ('data_2', ctypes.c_int32),
    )