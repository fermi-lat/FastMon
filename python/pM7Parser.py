#!/bin/env python

## @package pM7Parser
## @brief Basic module to parse the Magic 7 text file

import time
import math
import bisect
from pSCPosition import pSCPosition 

## @brief The Magic7 parser implementation

class pM7Parser:

    def __init__(self, inputFilePath):
        self.m7FilePath = inputFilePath
	self.m7FileContent = file(self.m7FilePath ,'r').readlines()
	self.SCPositionTable = []
        self.TimePoints = []
        self.parseIt()

    def getSCPositionTable(self):
        """ Dumb getter method
	"""
        return self.SCPositionTable
	
    def parseIt(self):
        i = 0
        OrbInSAA = 0
	for aline in self.m7FileContent:
	    #Useless to parse this human readable timestamp - SCTime is what we need
	    dataList = aline.strip('\n').split(' ')	    
	    # useless
	    #timestamp = self.getTimeMicroSeconds(dataList)
	    yearfloat = self.getYearFloat(dataList)

	    #Spacecraft message timestamp, seconds since 2001-01-01 00:00:00
            #Spacecraft message timestamp, microseconds of the current second
	    SCTime = (dataList[3], dataList[4])
	    
	    #Message type : Attitude or Orbit
	    dtype = dataList[2]
	    if dtype == 'ATT':
                #The x, y, z, and w components of the attitude quaternion in the ECI J2000 frame
	        SCAttitudeQuaternion = (dataList[5], dataList[6], dataList[7], dataList[8])		
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

		self.SCPositionTable.append(pSCPosition(SCTime, yearfloat, OrbPosition))
                self.TimePoints.append(int(SCTime[0]))
	    
	    i+=1
	    #if i%10000 == 0:
	    #    Radius = OrbPosition[0]*OrbPosition[0] + OrbPosition[1]*OrbPosition[1] + OrbPosition[2]*OrbPosition[2]
	    #    print timestamp, math.sqrt(Radius)
	    #if i == 100000:
	    #    break

    def getSCPosition(self, SCTime):
        #index = bisect.bisect(self.SCPositionTable, pSCPosition(SCTime))
        index = bisect.bisect(self.TimePoints, SCTime[0])
        #print self.TimePoints
        #print SCTime[0]
        #print index
        return self.SCPositionTable[index]

    def getTimeMicroSeconds(self, dataList):
        #I do not know a way to handle the microseconds properly
	#useless - use SCTime instead
	microseconds = 0
        timeString = dataList[0] +'T'+ dataList[1]
	if len(dataList[1].split('.')) > 1:
	    microseconds = float(dataList[1].split('.')[1])
	    timeString = dataList[0] +'T'+ dataList[1].split('.')[0]
	sTime = time.strptime(timeString, "%Y-%m-%dT%H:%M:%S")
	timeinseconds = time.mktime(sTime)
	return int(timeinseconds*1000000+microseconds)

    def getYearFloat(self, dataList):
	#usefull for igrf plugin
	# consider month level for now
        dayList = dataList[0].split('-')
	yearfloat = float(dayList[0]) + 0.1*float(dayList[1])*10/12.
	return float(yearfloat)


if __name__ == '__main__':
    m7FilePath = '/data37/users/ISOCdata/071009001/magic7_071009001.txt'
    p = pM7Parser(m7FilePath)
    p.parseIt()
    for met in [252672900, 252674520, 252675925]: 
        sc = p.getSCPosition((met,0))
        sc.processCoordinates()
        print sc
    
