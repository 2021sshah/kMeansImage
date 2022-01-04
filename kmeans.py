# Siddharth Shah
import time, sys, random
import urllib.request
import io
from PIL import Image

def analyzeOriginal():
    pixToCount = {}
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            if not pix[x,y] in pixToCount: pixToCount[pix[x,y]] = 0
            pixToCount[pix[x,y]] += 1
    comCount = max(pixToCount.values())
    pixCom = (0,0,0)
    for pixel, count in pixToCount.items():
        if count == comCount: return pixToCount.keys(), pixToCount, pixel, count # Leave with Pixel
    return pixToCount.keys(), pixToCount, pixCom, comCount

def assignPixToMean(distPixLst, meansLst):
    meanToPixels = {mean:[] for mean in meansLst}
    for pix in distPixLst: # Determine Closest Mean
        minError, closestMean = determineError(pix, meansLst[0]), meansLst[0]
        for mean in meansLst[1:]:
            error = determineError(pix, mean)
            if error > minError: continue
            minError = error
            closestMean = mean
        meanToPixels[closestMean].append(pix)
    return meanToPixels

def determineError(pixA, pixB): # Distance to Mean
    return sum([(pixA[i]-pixB[i])**2 for i in range(3)])

def findkMeans(distPixLst, distPixToCount, meansLst, meanToPixels):
    # Find New Means Per Group
    newMeansLst = []
    for mean in meansLst:
        newMean = findNewMeanOfPixels(meanToPixels[mean], distPixToCount)
        newMeansLst.append(newMean)
    # Resort Distinct Pixels into Groups
    newMeanToPixels = assignPixToMean(distPixLst, newMeansLst)
    # Determine if any Pixels Changed Groups
    for idx in range(len(meansLst)):
        if len(meanToPixels[meansLst[idx]]) != len(newMeanToPixels[newMeansLst[idx]]):
            return findkMeans(distPixLst, distPixToCount, newMeansLst, newMeanToPixels) # Recur with Next Set
    meanToCount = {}
    for mean in newMeansLst:
        meanToCount[mean] = sum([distPixToCount[pix] for pix in newMeanToPixels[mean]])
    # {mean:len(newMeanToPixels[mean]) for mean in newMeansLst}
    roundedMeansLst = [(int(mean[0]), int(mean[1]), int(mean[2])) for mean in newMeansLst]
    distPixToIntMean = {pix:(int(mean[0]), int(mean[1]), int(mean[2])) for mean in newMeansLst for pix in newMeanToPixels[mean]}
    return newMeansLst, meanToCount, roundedMeansLst, distPixToIntMean

def findNewMeanOfPixels(pixelsLst, pixToCount):
    rSum, gSum, bSum, pixSum = 0, 0, 0, 0
    for pix in pixelsLst:
        rSum += pix[0]*pixToCount[pix]
        gSum += pix[1]*pixToCount[pix]
        bSum += pix[2]*pixToCount[pix]
        pixSum += pixToCount[pix]
    return rSum/pixSum, gSum/pixSum, bSum/pixSum

def replacePixelsWithFinalMeans(intMeansLst, distPixToIntMean):
    meanToLocSet = {mean:set() for mean in intMeansLst}
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            pix[x,y] = distPixToIntMean[pix[x,y]]
            meanToLocSet[pix[x,y]].add((x,y))
    return meanToLocSet

alreadySeen = set() # Global Set
def determineNewRegionCountLst(meansLst, meansToLocSet):
    meanToIdx = {meansLst[idx]:idx for idx in range(len(meansLst))}
    regionCountLst = [0 for mean in meansLst]
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            if (x,y) in alreadySeen: continue
            explorePixelRegion(x, y, meansToLocSet[pix[x,y]])
            regionCountLst[meanToIdx[pix[x,y]]] += 1
    return regionCountLst

def explorePixelRegion(inX, inY, possibleSet):
    pixQueue = [(inX,inY)]
    while pixQueue:
        x, y = pixQueue.pop()
        # Account for Pixel
        alreadySeen.add((x,y))
        # Horizontal and Vertical Neighbors
        if not (x-1,y) in alreadySeen and (x-1,y) in possibleSet: pixQueue.append((x-1,y))
        if not (x+1,y) in alreadySeen and (x+1,y) in possibleSet: pixQueue.append((x+1,y))
        if not (x,y-1) in alreadySeen and (x,y-1) in possibleSet: pixQueue.append((x,y-1))
        if not (x,y+1) in alreadySeen and (x,y+1) in possibleSet: pixQueue.append((x,y+1))
        # Diagonal Neighbors
        if not (x-1,y-1) in alreadySeen and (x-1,y-1) in possibleSet: pixQueue.append((x-1,y-1))
        if not (x+1,y+1) in alreadySeen and (x+1,y+1) in possibleSet: pixQueue.append((x+1,y+1))
        if not (x+1,y-1) in alreadySeen and (x+1,y-1) in possibleSet: pixQueue.append((x+1,y-1))
        if not (x-1,y+1) in alreadySeen and (x-1,y+1) in possibleSet: pixQueue.append((x-1,y+1))

def displayFinalMeans(meansLst, meanToCount, regionCountLst):
    print("Final means:")
    for idx in range(len(meansLst)):
        print("{}: {} => {}".format(idx+1, meansLst[idx], meanToCount[meansLst[idx]]))
    print("\nRegion counts: {}".format(regionCountLst))

startTime = time.time()
# Access Image and Manage Inputs
k = int(sys.argv[1]) # Number of Means
URL = sys.argv[2] # 'https://i.pinimg.com/originals/95/2a/04/952a04ea85a8d1b0134516c52198745e.jpg'
f = io.BytesIO(urllib.request.urlopen(URL).read()) if "http" in URL else URL
img = Image.open(f)
pix = img.load() # Can modify img through pix
# Print Original Properities
print("Size: {} x {}".format(img.size[0],img.size[1]))
print("Pixels: {}".format(img.size[0]*img.size[1]))
distPixLst, distPixToCount, pixCom, comCount = analyzeOriginal()
print("Distinct pixel count: {}".format(len(distPixLst)))
print("Most common pixel: {} => {}".format(pixCom, comCount))
# Choose Random Means and Determine kMeans
meansLst = [pix[random.randint(0,255),random.randint(0,255)] for i in range(k)]
meanToPixels = assignPixToMean(distPixLst, meansLst)
finalMeansLst, finalMeanToCount, intMeansLst, distPixToIntMean = findkMeans(distPixLst, distPixToCount, meansLst, meanToPixels)
# Work on Image with Rounded Means
intMeanToLocSet = replacePixelsWithFinalMeans(intMeansLst, distPixToIntMean)
regionCountLst = determineNewRegionCountLst(intMeansLst, intMeanToLocSet)
# Display Result and Save Image
displayFinalMeans(finalMeansLst, finalMeanToCount, regionCountLst)
img.save("2021sshah.png", "PNG")