import cv2
import math
import ImageProcessing.ImageSet as ImageSet

def GetImage(MapEnum):
    ImageUrl = ImageSet.GetImageURL(MapEnum)

    return cv2.imread(ImageUrl)

def DisplayImage(image, MapName):
    cv2.imshow(MapName, image)

def ScanImage(image, CenterOfCapture, ApertureSize):
    minX = max(0, math.floor(CenterOfCapture.X - (ApertureSize/2)))
    maxX = min(image.shape[1], math.floor(CenterOfCapture.X + (ApertureSize/2)))
    minY = max(0, math.floor(CenterOfCapture.Y - (ApertureSize/2)))
    maxY = min(image.shape[0], math.floor(CenterOfCapture.Y + (ApertureSize/2)))

    return image[minY:maxY, minX:maxX]

def GetScanRelation(BinsPerChannel, Image1, Image2):
    image1RGB = cv2.cvtColor(Image1, cv2.COLOR_BGR2RGB)
    image2RGB = cv2.cvtColor(Image2, cv2.COLOR_BGR2RGB)

	# extract a 3D RGB color histogram from the image,
	# using 8 bins per channel, normalize, and update
	# the index
    hist1 = cv2.calcHist([image1RGB], [0, 1, 2], None, [BinsPerChannel, BinsPerChannel, BinsPerChannel],
        [0, 256, 0, 256, 0, 256])
    hist2 = cv2.calcHist([image2RGB], [0, 1, 2], None, [BinsPerChannel, BinsPerChannel, BinsPerChannel],
        [0, 256, 0, 256, 0, 256])

    hist1 = cv2.normalize(hist1, hist1).flatten()
    hist2 = cv2.normalize(hist2, hist2).flatten()

    return cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)