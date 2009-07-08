#!/bin/env python

import pSafeLogger
logger = pSafeLogger.getLogger('pM7Parser')

## @package pM7Parser
## @brief Basic module to parse the Magic 7 text file
#
# The constructor takes a path to a magic7 text file and builds a list of spacecraft
# position in ECI coordinate, each position is associated to the timestamp in MET(s).
#
# ECI (Earth-Centered Inertial) (X,Y,Z) rectangular coordinates
#
# The Magic 7 file contains information about the spacecraft attitude and position.
# Each line represents one "Magic-7" message. The fields of each line are as follows:
#
##  Record 	Fields 	Definition
# @li All 	1-2 	Human-readable timestamp
# @li All 	3 	Record type, either ATT for attitude messages or ORB for orbit-position messages
# @li All 	4 	Spacecraft message timestamp, seconds since 2001-01-01 00:00:00
# @li All 	5 	Spacecraft message timestamp, microseconds of the current second
# @li ATT 	6-9 	The x, y, z, and w components of the attitude quaternion in the ECI J2000 frame
# @li ATT 	10-12 	The body-axis x, y, and z components of the spacecraft angular velocity, in rad/sec
# @li ORB 	6-8 	The ECI J2000 orbit position, in meters
# @li ORB 	9-11 	The ECI J2000 orbit velocity, in meters/sec
# @li ORB 	12 	The spacecraft attitude-control mode 3==inertially pointed, 5==sky survey (TBR)
# @li ORB 	13 	Flag indicating whether or not the observatory is within the LAT SAA boundary 1==IN, 0==OUT



import time
import math
import bisect
from pSCPosition import pSCPosition
from pSAAPolygon import pSAAPolygon, pVertex

## @brief The Magic7 parser implementation
#
#  The constructor needs a full path to a magic7 text file

class pM7Parser:

    ## @brief Constructor
    ## @param self
    #  The class instance.
    ## @param inputFilePath
    #  The full path to the magic7 text file.

    def __init__(self, inputFilePath, saaDefinitionFile):
        ## @var m7FilePath
        ## @brief The magic7 file path
	
        ## @var m7FileContent
        ## @brief The Magic7 file content is read in the constructor
	
	## @var SCPositionTable
	## @brief The list of Space Craft Position is filled in when the file is parsed.
	
	## @var TimePoints
	## @brief The list of time stamps corresponding to each space craft position.
	#
	# This list is used to retreive the nearest space craft position corresponding to a time stamp.
	
        if saaDefinitionFile is None:
            logger.info('No SAA definition provided. Corresponding variables will not be filled.')
            self.SAAPolygon = None
        else:
            self.SAAPolygon = pSAAPolygon(saaDefinitionFile)
        self.m7FilePath = inputFilePath
	self.m7FileContent = file(self.m7FilePath ,'r').readlines()
	self.tweakM7content()
	self.SCPositionTable = []
        self.TimePoints = []
        self.parseIt()

    ## @brief Check magic 7 file content
    #  Use this function to check the magic 7 file quality
    ## @param self
    #  The class instance.
    def tweakM7content(self):
        # I need the M7 file to start with an ATT line, if it starts with an ORB line
	# then I'll just skip it
	if self.m7FileContent[0].strip('\n').split(' ')[2] == "ORB":
	    self.m7FileContent = self.m7FileContent[1:]
        return 0

    ## @brief Get the list of Space Craft Position
    #  
    ## @param self
    #  The class instance.

    def getSCPositionTable(self):
        if self.SCPositionTable == []:
	    print 'Warning : SCPositionTable has not been filled in yet.'
        return self.SCPositionTable
	
    ## @brief Parse the magic7 file content as stored in m7FileContent.
    #  
    ## @param self
    #  The class instance.
    #
    # The magic7 text file structure is detailed in the class description.
    #
    # We're interested in 4 quantities to build the space craft position table
    #
    # yearfloat is a float quantity calculated using the year and month read in the magic7 text file.
    #
    # SCTime is a pair containing the time stamp in MET (seconds, microseconds)
    #
    # OrbPosition is a 3D vector (X, Y, Z) giving the space craft orbit position in J2000 coordinates, in meters.
    #
    # SCAttitudeQuaternion is a 4D vector (x, y, z, w) with the components of the attitude quaternion in the ECI J2000 frame
    #
    
    def parseIt(self):
        i = 0
        OrbInSAA = 0
	for aline in self.m7FileContent:
	    #Useless to parse this human readable timestamp - SCTime is what we need
	    dataList = aline.strip('\n').split(' ')	    
	    yearfloat = self.getYearFloat(dataList)

	    #Spacecraft message timestamp, seconds since 2001-01-01 00:00:00
            #Spacecraft message timestamp, microseconds of the current second
	    SCTime = (dataList[3], dataList[4])
	    
	    #Message type : Attitude or Orbit
	    dtype = dataList[2]
	    if dtype == 'ATT':
                #The x, y, z, and w components of the attitude quaternion in the ECI J2000 frame
	        SCAttitudeQuaternion = (float(dataList[5]), float(dataList[6]), float(dataList[7]), float(dataList[8]))		
		#The body-axis x, y, and z components of the spacecraft angular velocity, in rad/sec
		SCAngularVelocity =  (dataList[9], dataList[10], dataList[11])

	    elif dtype == 'ORB':
                #ORB 	6-8 	The ECI J2000 orbit position, in meters
		OrbPosition = (float(dataList[5]), float(dataList[6]), float(dataList[7]))	
                #ORB 	9-11 	The ECI J2000 orbit velocity, in meters/sec
		OrbVelocity = (dataList[8], dataList[9], dataList[10])
                #ORB 	12 	The spacecraft attitude-control mode 3==inertially pointed, 5==sky survey (TBR)
		OrbMode = dataList[11]
                #ORB 	13 	Flag indicating whether or not the observatory is within the LAT SAA boundary 1==IN, 0==OUT
		OrbInSAA = dataList[12]
                
		# OrbPosition as just been read from the file, whereas we get the latest value of SCAttitudeQuaternion
		# As magic7 file contains many more ATT message than ORB ones that should work
		self.SCPositionTable.append(pSCPosition(SCTime, yearfloat, OrbPosition, SCAttitudeQuaternion, OrbMode,
                                                        OrbInSAA, self.SAAPolygon))
                self.TimePoints.append(int(SCTime[0]))	    
	    i+=1

    ## @brief Get the space craft position nearest to the corresponding timestamp.
    #
    # Using the bisect module on the TimePoints list to get the correct index in the space craft position list.
    #
    ## @param self
    #  The class instance.
    ## @param SCTime
    #  A space craft timestamp is a pair containing the MET : (seconds, microseconds).
    #  Only the seconds are used though to get the space craft position.
    #  Note that bisect return the length of the array when requiring a point which is
    #  larger than the maximum value of the array so that in that case we decrement the returned
    #   index by one in order to avoid an IndexError.
    
    def getSCPosition(self, SCTime):
        index = bisect.bisect(self.TimePoints, SCTime[0])
        if index == len(self.TimePoints):
            logger.info('Required index exceeds the length of TimePoints by one.')
            logger.info('Decreasing it by one.')
            index -= 1
        try:
            return self.SCPositionTable[index]
        except IndexError:
            logger.error('Invalid index in pM7Parser.getSCPosition().')
            logger.info('Required spacecraft time is %s.' % SCTime[0])
            logger.info('Index returned by bisect is %s (the SC table has %s rows).' %\
                        (index, len(self.SCPositionTable)))
            logger.info('Returning the last SC position table element...')
            return self.SCPositionTable[-1]
       
    ## @brief Parse any magic7 line having a human readable time stamp and returns a float corresponding to
    # the year and month of the data.
    #
    ## @param self
    #  The class instance.
    ## @param dataList
    #  Any line of the magic7 file contains a human readable time stamp, that we parse here when needed.
    #
    # This yearfloat is usefull for the igrf plugin.
    # We consider month level for now, as this is used to initialize the Earth geomagnetic model,
    # it should be sufficient.

    def getYearFloat(self, dataList):
        dayList = dataList[0].split('-')
	yearfloat = float(dayList[0]) + 0.1*float(dayList[1])*10/12.
	return float(yearfloat)


if __name__ == '__main__':
    m7FilePath = '/data37/users/ISOCdata/071009001/magic7_071009001.txt'
    p = pM7Parser(m7FilePath)
    p.parseIt()
    for met in p.TimePoints: 
        sc = p.getSCPosition((met,0))
        sc.processCoordinates()
        print sc.getLongitude(), sc.getLatitude(), sc.getDistanceToSAA(), sc.OrbInSAA
    
