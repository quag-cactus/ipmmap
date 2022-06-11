
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