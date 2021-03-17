import LocationFunctions
import ImageProcessing.ImageLoader as ImageFunctions
import GridFunctions
from GridFunctions import Coordinates
from LocationFunctions import VelocityVec
import numpy as np
from copy import copy
import math

class Particle():
    def __init__(self, ApertureSize, Location, Image, Grid):
        self.ApertureSize = ApertureSize
        self.Location = Location
        self.Weight = 1
        self.VisualWeight = 1
        self.ScannedImage = self.Scan(Image, Grid)

    def SetWeight(self, Weight):
        self.Weight = Weight

    def SetVisualWeight(self, VisualWeight):
        self.VisualWeight = VisualWeight

    def DetermineWeight(self, BinsPerChannel, DroneScan):
        #Perform RGB Histogram comparison
        scanRelation = ImageFunctions.GetScanRelation(BinsPerChannel, self.ScannedImage, DroneScan)
        #For Correlation Plots only
        #scanRelation = (scanRelation + 1)/2
        calculatedWeight = max(0, scanRelation)
        calculatedWeight = calculatedWeight**2

        self.SetWeight(calculatedWeight)
        return calculatedWeight
    
    def NormalizeWeight(self, ParticlePercentCutoff, WeightsSum, MaxWeight, MinWeight, RemoveParticles):

        self.SetWeight(self.Weight/WeightsSum)
        if (MaxWeight == MinWeight):
            visualWeight = 1.0
        else: 
            visualWeight = max(((self.Weight - MinWeight) / (MaxWeight - MinWeight)),0.05)
        
        #Unweight all particles less than PARTICLE_PERCENT_CUTOFF% of the max partical size
        if visualWeight < ParticlePercentCutoff and RemoveParticles:
            self.SetWeight(0.0)
            self.SetVisualWeight(0.05)
        else:
            self.SetVisualWeight(visualWeight)
            
        
        self.SetVisualWeight(visualWeight)

    def Scan(self, Image, Grid):
        scannedImage = ImageFunctions.ScanImage(Image, GridFunctions.ConvertState2Pixels(Grid, self.Location)
            , self.ApertureSize)

        #cv2.imshow("MapName", scannedImage)
        return scannedImage

    def Step(self, DroneVelocity, Image, Grid):
        self.VelocityVec = LocationFunctions.ApplyVelocityConstraints(DroneVelocity, self.Location, Grid)

        self.Location = self.Move()

        self.ScannedImage = self.Scan(Image, Grid)

    def Move(self):
        return Coordinates(self.Location.X + self.VelocityVec.X
                        , self.Location.Y + self.VelocityVec.Y, "State")

    def AddResampleNoise(self, ResampleNoiseVar, Image, Grid):
        sampleNoise = VelocityVec(np.random.randn()*(1-self.VisualWeight)*ResampleNoiseVar
            ,np.random.randn()*(1-self.VisualWeight)*ResampleNoiseVar)
        self.Step(sampleNoise, Image, Grid)

"""
(NUMBER_OF_PARTICLES, APERTURE_SIZE
    , RESAMPLE_NOISE_VAR, PARTICLE_PERCENT_CUTOFF
    , BINS_PER_CHANNEL, Image, Grid)
    """

class ParticleFilter():

    def __init__(self, NumberOfParticles, ApertureSize
            , ResampleNoiseVar, ParticlePercentCutoff, BinsPerChannel
            , Image, Grid):
        self.ParticleList = self.GenerateParticles(NumberOfParticles, ApertureSize, Image, Grid)
        self.ResampleNoiseVar = ResampleNoiseVar
        self.ParticlePercentCutoff = ParticlePercentCutoff
        self.BinsPerChannel = BinsPerChannel
        self.AvgError = []
        self.WeightVariance = []
        self.LocationVariance = []
        self.MSE = []
        self.StepNumber = 0


    def GenerateParticles(self, NumberOfParticles, ApertureSize, Image, Grid, CurrentParticles = None):
        P = []

        for i in range(0,NumberOfParticles):
            pI = Particle(ApertureSize, LocationFunctions.GenerateRandomLocation(Grid), Image, Grid)
            P.append(pI)

        return P

    def GetParticleList(self):
        return self.ParticleList

    def LowVarianceSampler(self):
        M = len(self.ParticleList)=

        P = []
        randomVal = np.random.randn()
        randomVal = min(randomVal, .99) #Limit this at .99 so that it doesn't make U>incrementalWeight impossible
        r = randomVal * (1/M)
        incrementalWeight = self.ParticleList[0].Weight
        i = 0
        j = 0
        for m in range(0,M):
            U = r + m/M
            while U > incrementalWeight:
                i = i + 1
                incrementalWeight = incrementalWeight + self.ParticleList[i].Weight
            P.append(copy(self.ParticleList[i]))
            j = j + 1

        return P

        

    def RegenerateParticles(self, Image, Grid):
        self.ParticleList = self.LowVarianceSampler()

        for particle in self.ParticleList:
            particle.AddResampleNoise(self.ResampleNoiseVar, Image, Grid)
            

        return True

    def DetermineWeights(self, DroneScan):
        minWeight = 100.0
        maxWeight = 0.0
        weightsSum = 0.0

        for particle in self.ParticleList:
            particleWeight = particle.DetermineWeight(self.BinsPerChannel, DroneScan)
            minWeight = min(minWeight, particleWeight)
            maxWeight = max(maxWeight, particleWeight)
            weightsSum = weightsSum + particleWeight
        
        for particle in self.ParticleList:
            particle.NormalizeWeight(self.ParticlePercentCutoff, weightsSum, maxWeight/weightsSum, minWeight/weightsSum, True)
        
        #Since weights are changed above, we need to renormalize
        minWeight = 100.0
        maxWeight = 0.0
        weightsSum = 0.0

        for particle in self.ParticleList:
            minWeight = min(minWeight, particle.Weight)
            maxWeight = max(maxWeight, particle.Weight)
            weightsSum = weightsSum + particle.Weight
        
        for particle in self.ParticleList:
            particle.NormalizeWeight(self.ParticlePercentCutoff, weightsSum, maxWeight/weightsSum, minWeight/weightsSum, False)
        

    def Step(self, DroneVelocity, Image, Grid):
        for particle in self.ParticleList:
            particle.Step(DroneVelocity, Image, Grid)

        self.StepNumber = self.StepNumber + 1

    def CalculateMetrics(self, DroneLocation):
        AvgError = 0.0
        SumError = 0.0
        weightArray = []
        xArray = []
        yArray  = []

        for i in range(0,len(self.ParticleList)):
            particle = self.ParticleList[i]
            weightArray.append(particle.Weight*1000)
            xArray.append(particle.Location.X)
            yArray.append(particle.Location.Y)
            particleError = Coordinates.Distance(particle.Location, DroneLocation)**2
            AvgError = (i/(i+1))*AvgError + (1/(i+1))*particleError
            
        weightvariance = np.var(weightArray)*100
        locationVariance = math.sqrt((np.var(xArray))**2 + (np.var(yArray))**2)
        self.AvgError.append(AvgError)
        self.WeightVariance.append(weightvariance)
        self.LocationVariance.append(locationVariance)
        self.MSE.append((AvgError)**2 + (locationVariance)**2)
        

