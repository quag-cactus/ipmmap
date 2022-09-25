
import ctypes

class BaseMmapStructure(ctypes.Structure):
    """A base struture to map IPMMAP's shared memory space.
    This is a empty class to be inherited by your Structure and search it. 
    """
    pass

class MmapStructureHeader(ctypes.Structure):
    """A common-header of IPMMAP's shared memory space.
    """
    _fields_ = (
        ('header_code', ctypes.c_short),    # Unique bytes of indicating that it is Structure for IPMMAP.
        ('time_stamp', ctypes.c_double),    # Timestamp, UNIX epoch time.
    )

