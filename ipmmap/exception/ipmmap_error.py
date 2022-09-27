
class IpMmapError(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return "error occurred in ipmmap"

class CreateFileIpMmapError(IpMmapError):
    def __init__(self, filePath):
        self.filePath: str = filePath

    def __str__(self):
        return "{}: Failed to create a file for memory mapping of IPMMAP.".format(self.filePath)

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