import enum

imageDirectory = "/Users/rosswilhite/Documents/codebase/ProbabilisticRoboticsTools/Maps/"

class MapIds(enum.Enum):
    BayMap = 1
    CityMap = 2
    MarioMap = 3

def GetImageURL(MapId):
        if (MapId.value == 1):
            return imageDirectory + "BayMap.png"
        if (MapId.value == 2):
            return imageDirectory + "CityMap.png"
        if (MapId.value == 3):
            return imageDirectory + "MarioMap.png"