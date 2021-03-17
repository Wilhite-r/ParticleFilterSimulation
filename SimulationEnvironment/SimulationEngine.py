import sys
sys.path.append('/Users/rosswilhite/Documents/codebase/ProbabilisticsRoboticsTools/ImageProcessing')
sys.path.append('/Users/rosswilhite/Documents/codebase/ProbabilisticsRoboticsTools/ParticleFilter')
sys.path.append('../')
from time import time, sleep
import math
from copy import copy
import LocationFunctions
import GridFunctions
from GridFunctions import Coordinates, MapGrid
import enum
import ImageProcessing.ImageSet as ImageSet
from ImageProcessing.ImageLoader import GetImage
import ImageProcessing.ImageCompiler as ImageCompiler
import Drone
import ParticleFilter.ParticleFilter as ParticleFilter
import matplotlib.pyplot as plt

#Constant Variables
NUMBER_OF_PARTICLES = 1000
APERTURE_SIZE = 75
RESAMPLE_NOISE_VAR = 0.8
PARTICLE_PERCENT_CUTOFF = 0.6
DRONE_MOVEMENT_NOISE_VAR = 0.2
DRONE_VELOCITY_MAG = 1.0
BINS_PER_CHANNEL = 32
PLOT_METRICS = False

#Background Constant Objects
MapId = ImageSet.MapIds.MarioMap
BGImage = GetImage(MapId)
Grid = GridFunctions.GetGridFromImage(BGImage)

##Perform Main Functionality
def Step(Grid, Image, SimDrone, Filter):
    global BGImage
    Filter.RegenerateParticles(BGImage, Grid)

    #[self.PredictedLocation, self.ActualLocation, self.VelocityVec, self.ScannedImage]
    (PredictedDroneLocation, ActualDroneLocation, ActualDroneVelocity, DroneScan) = SimDrone.Step(BGImage, Grid)
    
    Filter.Step(ActualDroneVelocity, BGImage, Grid)
    Filter.DetermineWeights(DroneScan)
    if (PLOT_METRICS):
        Filter.CalculateMetrics(ActualDroneLocation)
        PlotErrors(Filter)

    Particles = Filter.GetParticleList()
    newImage = ImageCompiler.CompileImage(Image, Grid, ActualDroneLocation, DroneScan, Particles)

    
    return newImage

#Plot Metrics
def PlotErrors(Filter):
    plt.plot(range(0,Filter.StepNumber + 1), Filter.AvgError, label="Bias")
    plt.plot(range(0,Filter.StepNumber + 1), Filter.WeightVariance, label="Weight Variance")
    plt.plot(range(0,Filter.StepNumber + 1), Filter.LocationVariance, label="Location Variance")
    print("Step " + str(Filter.StepNumber) + ", Bias: " + str(Filter.AvgError[Filter.StepNumber]))
    print("Step " + str(Filter.StepNumber) + ", Weight Variance: " + str(Filter.WeightVariance[Filter.StepNumber]))
    print("Step " + str(Filter.StepNumber) + ", Location Variance: " + str(Filter.LocationVariance[Filter.StepNumber]))
    #plt.plot(range(0,Filter.StepNumber + 1), Filter.MSE, label="MSE")
    plt.title('Average Error')
    plt.xlabel('Steps')
    plt.legend()
    plt.show()

#Create Environment
Image = copy(BGImage)
SimDrone = Drone.VirtualDrone(APERTURE_SIZE, DRONE_VELOCITY_MAG, DRONE_MOVEMENT_NOISE_VAR, BGImage, Grid)
Filter = ParticleFilter.ParticleFilter(NUMBER_OF_PARTICLES, APERTURE_SIZE
    , RESAMPLE_NOISE_VAR, PARTICLE_PERCENT_CUTOFF
    , BINS_PER_CHANNEL, Image, Grid)

#Display Initial Position
ImageCompiler.CompileImage(Image, Grid, SimDrone.ActualLocation)

#Get First Calculations
(PredictedDroneLocation, ActualDroneLocation, ActualDroneVelocity, DroneScan) = SimDrone.GetState()
Filter.DetermineWeights(DroneScan)
if (PLOT_METRICS):
    Filter.CalculateMetrics(ActualDroneLocation)
    
#Display Initial Particles
Particles = Filter.GetParticleList()
ImageCompiler.CompileImage(Image, Grid, ActualDroneLocation, DroneScan, Particles)

while(True):
    Image = Step(Grid, copy(BGImage), SimDrone, Filter)
