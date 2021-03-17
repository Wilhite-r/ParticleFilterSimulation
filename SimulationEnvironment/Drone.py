import math
import GridFunctions
import LocationFunctions
from LocationFunctions import VelocityVec
from GridFunctions import Coordinates, MapGrid
from ImageProcessing.ImageLoader import ScanImage
import cv2
import numpy as np

class VirtualDrone():
    #Set initial State
    def __init__(self, ApertureSize, VelocityMag, MovementNoiseVar,  Image, Grid
            , StartingLocation = None):
        self.ApertureSize = ApertureSize
        self.VelocityMag = VelocityMag
        self.MovementNoiseVar = MovementNoiseVar

        if (StartingLocation == None):
            self.PredictedLocation = LocationFunctions.GenerateRandomLocation(Grid)
            self.ActualLocation = self.PredictedLocation
        else:
            self.PredictedLocation = StartingLocation
            self.ActualLocation = self.PredictedLocation
        
        self.VelocityVec = None
        self.ScannedImage = self.Scan(Image, Grid)
        
    #The only function which modifies state for the Drone,
    def Step(self, Image, Grid):
        self.VelocityVec = LocationFunctions.GetRandomVelocity(Grid, self.ActualLocation, self.VelocityMag)

        (self.PredictedLocation, self.ActualLocation) = self.Move()

        self.ActualLocation = self.AddMovementNoise(Grid)

        self.ScannedImage = self.Scan(Image, Grid)

        return self.GetState()


    def Move(self):
        return (Coordinates(self.PredictedLocation.X + self.VelocityVec.X
                        , self.PredictedLocation.Y + self.VelocityVec.Y, "State"),
                Coordinates(self.ActualLocation.X + self.VelocityVec.X
                        , self.ActualLocation.Y + self.VelocityVec.Y, "State"))

    def AddMovementNoise(self, Grid):
        boundaries = LocationFunctions.GetMovementBoundaries(Grid, self.ActualLocation, self.MovementNoiseVar)

        #set our random normal noise in the x and y range, in state units
        xNoise = min(max(np.random.randn(),boundaries[0]),boundaries[1])
        yNoise = min(max(np.random.randn(),boundaries[2]),boundaries[3])

        return Coordinates(self.ActualLocation.X + xNoise,
                            self.ActualLocation.Y + yNoise, "State")

    def Scan(self, Image, Grid):
        scannedImage = ScanImage(Image, GridFunctions.ConvertState2Pixels(Grid, self.ActualLocation), self.ApertureSize)

        #cv2.imshow("MapName", scannedImage)
        return scannedImage

    def GetState(self):
        return (self.PredictedLocation, self.ActualLocation, self.VelocityVec, self.ScannedImage)

