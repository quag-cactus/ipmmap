
class IpMmapError(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return "error occurred in ipmmap"

class StructNotFoundIpMmapError(IpMmapError):
    def __init__(self, structName):
        self.structName: str = structName

    def __str__(self):
        return "No ctypes.Structure named '{}' .".format(self.structName)


class CommonHeaderNotFoundIpMmapError(IpMmapError):
    def __init__(self, structName):
        self.structName: str = structName
    
    def __str__(self):
        return "Cannot use '{}' that does not insert " \
               "'ipmmap.base_struct.MmapStructureHeader' the top of it.".format(self.structName)