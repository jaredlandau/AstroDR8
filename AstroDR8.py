## *************************
## AstroDR8 v0.1
##   Program for calculating and compensating for field rotation in a series of astronomical images.
##   Designed to improve maximum integration time for planetary imagers, whilst also providing a consistent rotational axis during timelapses.
##   
## ATTRIBUTION:
##   Original script created by the user M63 in the /r/astrophotography Discord server, who generously provided it to the community for free usage. 
## *************************

import os
from datetime import datetime
from skimage import img_as_uint
from skimage.io import imread
from tifffile import imwrite
from skimage.transform import rotate
from astropy.time import Time
from astropy.coordinates import solar_system_ephemeris, EarthLocation
from astropy.coordinates import get_body, AltAz, position_angle
from astropy import units

# Set filetype and directory locations
inputDir = r"D:\Users\Jared\Documents\GitRepos\AstroDR8\input"
outputDir = r"D:\Users\Jared\Documents\GitRepos\AstroDR8\output"
datatype = ".png"

# Set midpoint time of observation data, as well as observer coordinates, to use as a reference
refTime = "2022-12-20-0045_0"
latitude = -37.000
longitude = 144.000

# Get planetary body from user input
instructions = "Please enter a solar system body from the following list:\nMercury, Sun, Moon, Venus, Mars, Jupiter, Saturn, Uranus, Neptune\n"
solar_system_ephemeris.set('builtin')
solarSystemBodyList = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune']
validBody = False
while(not validBody): # selection menu for the user
    planetaryBody = input(instructions).lower()
    if planetaryBody in solarSystemBodyList:
        validBody = True
    else:
        print("Unrecognised solar system body.\n")

# Prepare variables
formattedRefTime = Time(datetime.strptime(refTime, "%Y-%m-%d-%H%M_%S"))
obsCoords = EarthLocation(lat=latitude, lon=longitude)
AltAzCoords = AltAz(location=obsCoords, obstime=formattedRefTime)
bodyRef = get_body(planetaryBody, formattedRefTime, obsCoords)
bodyRefAltAz = bodyRef.transform_to(AltAzCoords)
posAngleRef = position_angle(bodyRefAltAz.az, bodyRefAltAz.alt, 0*units.deg, latitude*units.deg)

# Loop over each frame in the input directory
print("Processing image series...")
for file in os.listdir(inputDir):
    filename = os.fsdecode(file)
    if filename[-len(datatype):] == datatype:
        # Set reference time and coordinates for each frame
        imageTime = Time(datetime.strptime(filename[:17], "%Y-%m-%d-%H%M_%S")) 
        planetImage = get_body(planetaryBody, imageTime, obsCoords)
        AltAzCoordImage = AltAz(location=obsCoords, obstime=imageTime)
        imagePlanetAltAz = planetImage.transform_to(AltAzCoordImage)
        posAngleImage = position_angle(imagePlanetAltAz.az, imagePlanetAltAz.alt, 0*units.deg, latitude*units.deg)
        rotateAngle = posAngleImage.deg - posAngleRef.deg
        
        # Set input and output directories
        inputFilePath = os.path.join(inputDir, filename)
        outputFilePath = os.path.join(outputDir, filename)
        
        # Read image file, derotate by calculated angle and save the newly aligned image
        image = imread(inputFilePath)
        image = rotate(image, rotateAngle)
        image = img_as_uint(image) # unsigned integer format allows for 16-bit colour depth
        print("Derotated ", filename, " by ", rotateAngle, " degrees.")
        imwrite(outputFilePath, image) # skimage.io.imsave forces lossy compression to 8-bit, so we use tifffile.imwrite instead