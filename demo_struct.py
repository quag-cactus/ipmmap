import ctypes

from ipmmap.struct import base_struct as bs

# point-2d structure
class Point2D(ctypes.Structure):
    _fields_ = (
        ('x', ctypes.c_double), 
        ('y', ctypes.c_double),
    )

# point-3d structure
class Point3D(ctypes.Structure):
    _fields_ = (
        ('x', ctypes.c_double), 
        ('y', ctypes.c_double),
        ('z', ctypes.c_double)
    )

class MultiPointsData(ctypes.Structure):
    _fields_ = (
        ('multi_data_1', ctypes.c_int32), 
        ('multi_points', Point2D * 24),
    )

class DemoMmapStructure(bs.BaseMmapStacture):
    _fields_ = (
        ('header', bs.MmapStructureHeader),
        ('data_1', ctypes.c_int32),
        ('data_2', ctypes.c_int32),
        ('data_string', ctypes.c_char * 256),
        ('data_xy', Point2D),
        ('data_xyz', Point3D),
        ('multi_pts', MultiPointsData)
    )