import ctypes

from ipmmap.struct import base_struct as bs

# point-2d structure
class Point2D(ctypes.Structure):
    _fields_ = (
        ('x', ctypes.c_double), 
        ('y', ctypes.c_double),
    )

class MultiPointsData(ctypes.Structure):
    _fields_ = (
        ('multi_data_int', ctypes.c_int32), 
        ('multi_points', Point2D * 24),
    )

class DemoMmapStructure(bs.BaseMmapStructure):
    _fields_ = (
        ('header', bs.MmapStructureHeader),
        ('data_int', ctypes.c_int32),
        ('data_string', ctypes.c_char * 256),
        ('data_xy', Point2D),
        ('multi_pts', MultiPointsData)
    )