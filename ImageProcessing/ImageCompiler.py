import cv2
import math
from ImageProcessing.ImageLoader import DisplayImage
from GridFunctions import ConvertPixels2State, ConvertState2Pixels
import LocationFunctions

#LocationDotData
LOCATIONDOTRADIUS = 10
LOCATIONDOTCOLOR = (255,0,0)
THICKNESS = 3
PARTICLE_RADIUS = 15
PARTICLE_COLOR = (255,255,0)

def CompileImage(image, Grid, DroneLocation, DroneScan = None, Particles = None):
    currImage = image

    if (Particles is not None):
        for particle in Particles:
            currImage = DrawLocationDot(currImage, ConvertState2Pixels(Grid, particle.Location), PARTICLE_COLOR, GetParticleWeightSize(particle))

    if (DroneLocation is not None):
        cvLocation = ConvertState2Pixels(Grid, DroneLocation)
        #DroneVelocity = DroneVelocity

        currImage = DrawLocationDot(currImage, cvLocation, LOCATIONDOTCOLOR, LOCATIONDOTRADIUS, True, True)
        
        DisplayImage(currImage, "CurrentState")
        if (DroneScan is not None):
            DisplayImage(DroneScan, "CurrentScan")
    else:
        DisplayImage(currImage, "CurrentState")

    cv2.waitKey(0)

    return currImage


def DrawLocationDot(image, Location, Color, Radius, HasOutline = False, IsFilled = False):

    NewImage = cv2.circle(image, (Location.X, Location.Y), Radius, Color, -1 if IsFilled else THICKNESS)
    if (HasOutline):
        NewImage = cv2.circle(NewImage, (Location.X, Location.Y), Radius, (255,255,255), THICKNESS)

    return NewImage

def GetParticleWeightSize(Particle):
    return math.floor(abs(Particle.VisualWeight) * PARTICLE_RADIUS)

"""
def DrawScannedSquare(image, currPosition, currVelocity):
    PreviousLoc =   

    return innerCircle = cv.arrowedLine(image, (currPosition.X), pt2, LOCATIONDOTCOLOR, 3)
"""