import math
import random
from GridFunctions import Coordinates, MapGrid

ROUNDING_PLACES = 2

#Everything in this class should happen in state units


class VelocityVec():
    def __init__(self, XVel, YVel):
        self.X = XVel
        self.Y = YVel


def GenerateRandomLocation(Grid):
    X = random.uniform(Grid.StateMinX, Grid.StateMaxX)
    Y = random.uniform(Grid.StateMinY, Grid.StateMaxY)

    return Coordinates(X,Y, "State")

#Safely Get velocity that won't take us out of the map
def GetRandomVelocity(Grid, CurrentPosition, VelocityMagnitude):
    #First, get possibles Velocities for this step
    MovementBoundaries = GetMovementBoundaries(Grid, CurrentPosition, VelocityMagnitude)

    #get random x velocityround(random.uniform(num1, num2), 6)
    xVel = round(random.uniform(MovementBoundaries[0],MovementBoundaries[1]),ROUNDING_PLACES)
    YLimit = math.sqrt(VelocityMagnitude**2 - xVel**2)
    
    if (YLimit == 0):
        yVel = 0
    else:
        yMin = max(-YLimit, MovementBoundaries[2])
        yMax = min(YLimit, MovementBoundaries[3])
        yVel = round(random.uniform(yMin,yMax),ROUNDING_PLACES)

    return VelocityVec(xVel,yVel)

#Safely Get velocity that won't take us out of the map
def ApplyVelocityConstraints(VelocityVector, CurrentPosition, Grid):
    #First we get the cartesian range in state units
    xBoundaryMinDis = abs(Grid.StateMinX - CurrentPosition.X)
    xBoundaryMaxDis = abs(Grid.StateMaxX - CurrentPosition.X)
    yBoundaryMinDis = abs(Grid.StateMinY - CurrentPosition.Y)
    yBoundaryMaxDis = abs(Grid.StateMaxY - CurrentPosition.Y)

    VelocityVector.X = max(VelocityVector.X,-xBoundaryMinDis)
    VelocityVector.X = min(VelocityVector.X,xBoundaryMaxDis)
    VelocityVector.Y = max(VelocityVector.Y,-yBoundaryMinDis)
    VelocityVector.Y = min(VelocityVector.Y,yBoundaryMaxDis)

    return VelocityVector


def GetMovementBoundaries(Grid, CurrentPosition, VelocityMagnitude):
    #First we get the cartesian range in state units
    xBoundaryMinDis = abs(Grid.StateMinX - CurrentPosition.X)
    xBoundaryMaxDis = abs(Grid.StateMaxX - CurrentPosition.X)
    yBoundaryMinDis = abs(Grid.StateMinY - CurrentPosition.Y)
    yBoundaryMaxDis = abs(Grid.StateMaxY - CurrentPosition.Y)

    xBoundaryMin = max(-VelocityMagnitude,-xBoundaryMinDis)
    xBoundaryMax = min(VelocityMagnitude,xBoundaryMaxDis)
    yBoundaryMin = max(-VelocityMagnitude,-yBoundaryMinDis)
    yBoundaryMax = min(VelocityMagnitude,yBoundaryMaxDis)

    return [xBoundaryMin, xBoundaryMax,yBoundaryMin, yBoundaryMax]