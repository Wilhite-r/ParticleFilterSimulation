import math
DISTANCE_UNITS = 50

#All conversions between pixels and state units should happen here.
#I am not happy with the way I have set up the state units, I would like to modify this class
#once I finish the filter

#These can be in pixels or state units
class Coordinates:
    @staticmethod
    def Distance(Coor1, Coor2):
        dis = math.sqrt((Coor2.X - Coor1.X)**2 + (Coor2.Y - Coor1.Y)**2)

        return dis

    def __init__(self, X, Y, Format):
        self.X = X
        self.Y = Y
        self.Format = Format

#This contains both state and pixel limits
class MapGrid:

    def __init__(self, CoordinateMin, CoordinateMax):
        self.PixelMinX = CoordinateMin.X
        self.PixelMaxX = CoordinateMax.X
        self.PixelMinY = CoordinateMin.Y
        self.PixelMaxY = CoordinateMax.Y

        self.StateMinX = CoordinateMin.X / DISTANCE_UNITS
        self.StateMaxX = CoordinateMax.X / DISTANCE_UNITS
        self.StateMinY = CoordinateMin.Y / DISTANCE_UNITS
        self.StateMaxY = CoordinateMax.Y / DISTANCE_UNITS

        self.PixelRangeX = CoordinateMax.X - CoordinateMin.X + 1
        self.PixelRangeY = CoordinateMax.Y - CoordinateMin.Y + 1
        self.StateRangeX = self.StateMaxX - self.StateMinX
        self.StateRangeY = self.StateMaxY - self.StateMinY


#Image is in Pixels, we must go to State units
def GetGridFromImage(image):
    RangeX = image.shape[1]
    RangeY = image.shape[0]

    #Middle is 0, so left is  0 - RangeX/2
    AdjL = (RangeX -1)/ 2
    AdjH = (RangeY -1)/ 2
    
    BottomLeft = Coordinates((0 - math.floor(AdjL))
                            , (0 - math.floor(AdjH))
                            , "Pixel")
    TopRight = Coordinates((0 + math.ceil(AdjL))
                            , (0 + math.ceil(AdjH))
                            , "Pixel")
    return MapGrid(BottomLeft, TopRight)


#Returns Coordinates Object in State units, from pixels
def ConvertPixels2State(Grid, Coor):
    return Coordinates(
        Coor.X + Grid.PixelMinX / DISTANCE_UNITS
        , (Grid.PixelMaxY - Coor.Y) / DISTANCE_UNITS
        , "State")

#Returns Coordinate Object in pixels, from state units
def ConvertState2Pixels(Grid, Coor):
    return Coordinates(
        math.floor(Coor.X * DISTANCE_UNITS) - Grid.PixelMinX
        , Grid.PixelMaxY - math.floor(Coor.Y * DISTANCE_UNITS)
        , "Pixel")
