#!/bin/env python

## @package pSCPosition
## @brief Basic module to handle a spacecraft position in the sky
#
# Conversion from  ECI J2000 orbit position to geocentric coordinate
#
# From astro package : ScienceTools/ScienceTools_v8r0p4/astro/v2r8p1
#
# src/EarthCoordinate.cxx astro/EarthCoordinate.h
#
# src/JulianDate.cxx  astro/JulianDate.h

import time
import math
import bisect
from pSafeROOT import ROOT

#Earth Flattening Coeff.
EARTH_FLAT      = 1/298.25 
EARTH_RADIUS    = 6378145
SECONDS_PER_DAY = 24*60*60

## @brief The space craft position implementation.

class pSCPosition:
    
    ## @brief Constructor.
    ## @param self
    #  The class instance.
    ## @param time
    #  The Time stamp in MET as a pair (seconds, microseconds)    
    ## @param yearfloat
    #  A float representing the Year and Month of the data
    ## @param position
    #  The space craft position on orbit in meters, as a 3D tuple (X, Y, Z) in ECI J2000 coordinates
    ## @param quaternion
    #  The space craft attitude quaternion, as a 4D vector (x, y, z, w) in the ECI J2000 frame
    #

    def __init__(self, time,yearfloat = None, position=None, quaternion=None):
       ## @var YearFloat
       ## @brief A float representing the Year and Month of the data
       
       ## @var MetInSeconds
       ## @brief The Mission Elapsed Time in seconds
       
       ## @var MetMicroSeconds
       ## @brief The microseconds part of the Mission Elapsed Time
       
       ## @var Position
       ## @brief The space craft position on orbit in meters, as a 3D tuple (X, Y, Z) in ECI J2000 coordinates
       
       ## @var Quaternion
       ## @brief The space craft attitude quaternion, as a 4D vector (x, y, z, w) in the ECI J2000 frame
       
       ## @var EarthCoordinates
       ## @brief The space craft position in the earth coordinates as a 3D tuple (Latitude, Longitude, Altitude)
       
       ## @var Latitude
       ## @brief The space craft latitude
       
       ## @var Longitude
       ## @brief The space craft longitude
       
       ## @var Altitude
       ## @brief The space craft altitude relative to the Earth center
       
       ## @var PitchRollYaw
       ## @brief The space craft Roll, Pithc and Yaw angles in a 3D tuple
       
       ## @var Roll
       ## @brief The space craft Roll angle
       
       ## @var Pitch
       ## @brief The space craft Pitch angle
       
       ## @var Yaw
       ## @brief The space craft Yaw angle
       
       ## @var Zaxis
       ## @brief The space craft Z axis pointing direction in equatorial coordinates (Ra, Dec)
       
       ## @var ZRa
       ## @brief The space craft Z axis pointing direction Right Ascension
       
       ## @var ZDec
       ## @brief The space craft Z axis pointing direction Declination
       
       ## @var XRa
       ## @brief The space craft X axis pointing direction Right Ascension
       
       ## @var XDec
       ## @brief The space craft X axis pointing direction Declination
       
       ## @var JulianDate
       ## @brief The Time stamp as a Julian Date.
       
       ## @var GMSTime
       ## @brief The Time stamp in the Greenwich Meridian Sideral Time 

       self.YearFloat  = yearfloat
       self.MetInSeconds    = int(time[0])
       self.MetMicroSeconds = int(time[1])
       self.Position   = position
       self.Quaternion  = quaternion
       self.EarthCoordinates = (None, None, None)
       self.Latitude  = None
       self.Longitude = None
       self.Altitude  = None
       self.PitchRollYaw = (None, None, None)
       self.Roll  = None
       self.Pitch = None
       self.Yaw   = None
       self.Zaxis = (None, None)
       self.ZRa   = None
       self.ZDec  = None
       self.JulianDate = None
       self.GMSTime = None
       self.processCoordinates()
       
    ## @brief Compare 2 space craft positions using the time stamp in seconds
    ## @param self
    #  The class instance.
    def __cmp__(self, other):
        return self.MetInSeconds - other.MetInSeconds

    ## @brief Print the Space Craft position parameters
    ## @param self
    #  The class instance.
    def __str__(self):
        return '\nSpace Craft Position parameters:\n'                          \
	      +'MetInSeconds                 = %d\n' % self.MetInSeconds       \
	      +'MetMicroSeconds              = %s\n' % self.MetMicroSeconds    \
	      +'Position (x, y, z) in meters = (%s, %s, %s)\n' % self.Position \
	      +'JulianDate                   = %s\n' % self.JulianDate         \
	      +'GMSTime                      = %s\n' % self.GMSTime            \
	      +'Earth Coords (lat, long, alt)= (%s, %s, %s)\n' % self.EarthCoordinates\
	      +'Local Rock n Roll (pitch, roll, yaw)= (%s, %s, %s)\n' % self.PitchRollYaw 

    ## @brief Returns the current value of yearfloat.
    ## @param self
    #  The class instance.
    def getYearFloat(self):
	return self.YearFloat 


    ## @brief Returns the space craft Latitude.
    #
    #  If Latitude is None, try to process the coordinates before giving Latitude
    ## @param self
    #  The class instance.
    def getLatitude(self):
	if self.Latitude is None:
	    self.processCoordinates()
	return self.Latitude 
    
    ## @brief Returns the space craft Longitude.
    #
    #  If Longitude is None, try to process the coordinates before giving Longitude
    ## @param self
    #  The class instance.
    def getLongitude(self):
	if self.Longitude is None:
	    self.processCoordinates()
	return self.Longitude 

    ## @brief Returns the space craft Altitude.
    #
    #  If Altitude is None, try to process the coordinates before giving Altitude
    ## @param self
    #  The class instance.
    def getAltitude(self):
	if self.Altitude is None:
	    self.processCoordinates()
	return self.Altitude 

    ## @brief Returns the space craft Altitude relative to the earth surface.
    #
    #  If Altitude is None, try to process the coordinates before giving Altitude minus the Earth radius.
    ## @param self
    #  The class instance.
    def getRelativeAltitude(self):
	if self.Altitude is None:
	    self.processCoordinates()
	return self.Altitude - EARTH_RADIUS

    ## @brief Returns the current value of position.
    ## @param self
    #  The class instance.
    def getPosition(self):
	return self.Position

    ## @brief Returns the space craft Pitch (Theta).
    #
    #  If Pitch is None, try to process the coordinates before giving Pitch
    ## @param self
    #  The class instance.
    def getPitch(self):
	if self.Pitch is None:
	    self.processCoordinates()
	return self.Pitch

    ## @brief Returns the space craft Roll (Phi).
    #
    #  If Roll is None, try to process the coordinates before giving Roll
    ## @param self
    #  The class instance.
    def getRoll(self):
	if self.Roll is None:
	    self.processCoordinates()
	return self.Roll

    ## @brief Returns the space craft Yaw (Psi).
    #
    #  If Yaw is None, try to process the coordinates before giving Yaw
    ## @param self
    #  The class instance.
    def getYaw(self):
	if self.Yaw is None:
	    self.processCoordinates()
	return self.Yaw

    ## @brief Returns the space craft Z axis RA
    #
    #  If ZRa is None, try to process the coordinates before giving ZRa
    ## @param self
    #  The class instance.
    def getZRa(self):
	if self.ZRa is None:
	    self.processCoordinates()
	return self.ZRa

    ## @brief Returns the space craft Z axis Dec
    #
    #  If ZDec is None, try to process the coordinates before giving ZDec
    ## @param self
    #  The class instance.
    def getZDec(self):
	if self.ZDec is None:
	    self.processCoordinates()
	return self.ZDec

    ## @brief Returns the space craft X axis RA
    #
    #  If XRa is None, try to process the coordinates before giving XRa
    ## @param self
    #  The class instance.
    def getXRa(self):
	if self.XRa is None:
	    self.processCoordinates()
	return self.XRa

    ## @brief Returns the space craft X axis Dec
    #
    #  If XDec is None, try to process the coordinates before giving XDec
    ## @param self
    #  The class instance.
    def getXDec(self):
	if self.XDec is None:
	    self.processCoordinates()
	return self.XDec

    ## @brief Returns the Julian date for a given mission elapsed time 
    ## @param self
    #  The class instance is actually not used in this stand alone function
    ## @param An
    #  The year
    ## @param Me
    #  The month
    ## @param Gio
    #  The day
    ## @param met
    #  The mission elapsed time in seconds
    
    def getJulianDate(self, An, Me, Gio, met):
        """Calculate Julian Date of 0.0 Jan year
	   convert from MET to JD
	   Changed Trunc to math.floor
	"""
        if Me>2 :
	    pass
        else:
	    An = An - 1
            Me = Me + 12

        A = An/100.
        B = 2 - A + A/4.
        C = 365.25 * An 
        if An < 0:
	    C = C - 1
        D = int(30.6001 * (Me + 1))
        m_JD = B + C + D + Gio + 1720994.5 + float(met) / SECONDS_PER_DAY
        return m_JD

    ## @brief Returns the Julian Date since start of the mission
    ## @param self
    #  The class instance is actually not used in this stand alone function
    ## @param met
    #  The mission elapsed time in seconds
    def getGLASTDate(self, met):
        """
	   Changed Trunc to math.floor
	"""
	return self.getJulianDate(2001,1,1,met)

    ## @brief Returns the Julian Date for the mission start date : 1 Jan 2001 00:00
    ## @param self
    #  The class instance is actually not used in this stand alone function
    #
    ## the GLAST official mission start is : 1 Jan 2001 00:00
    #
    ##  Should return 2451910.5, currently returning 2451910.9
    def getMissionStart(self):
        return self.getGLASTDate(0)

    ## @brief Returns the Julian Date for the J2000 reference.
    ## @param self
    #  The class instance is actually not used in this stand alone function
    def getJ2000(self):
        return self.getJulianDate(2000,1,1,12)

    ## @brief Returns the Greenwich Meridian Sideral Time for a given Julian Date
    #  Routine was checked against astro package code, Jun 13th 2008 JB
    ## @param self
    #  The class instance is actually not used in this stand alone function
    ## @param jd
    #  A Julian Date
    def getGMSTime(self, jd):
	# integer part - Not Used
	M=math.modf(jd-0.5)[1] 
	# fractional part
	Ora_Un_Dec = math.modf(jd-0.5)[0]*24. 
	
	jd-=Ora_Un_Dec/24.
	
     	T = (jd - self.getJ2000()) / 36525.
     	T1 = (24110.54841 + 8640184.812866 * T + 0.0093103 * T * T)/86400.0
     	
	Tempo_Siderale_0 = math.modf(T1)[0] * 24.
        # integer part - Not Used
	M = math.modf(T1)[1]  
	
     	Tempo_Siderale_Ora = Tempo_Siderale_0 + Ora_Un_Dec * 1.00273790935
        
	if Tempo_Siderale_Ora < 0.:
	    Tempo_Siderale_Ora = Tempo_Siderale_Ora + 24.
        if Tempo_Siderale_Ora >= 24.:
	     Tempo_Siderale_Ora = Tempo_Siderale_Ora - 24.
        
	return float(Tempo_Siderale_Ora*15.)



    ## @brief Calculate and return the space craft position in Earth coordinates
    #  Routine was checked against astro package code, Jun 13th 2008 JB
    ## @param self
    #  The class instance.
    def getEarthCoordinate(self):
        # get the individual components
 	x = self.Position[0]
	y = self.Position[1]
	z = self.Position[2]

        # use ROOT TVector3 to avoid dumb errors
	v3    = ROOT.TVector3(x, y, z)
	r     = v3.Mag()
	theta = v3.Theta()
        phi   = v3.Phi()
	
	# Latitude
        m_lat = math.pi/2. - theta
    		
    	# Longitude
	m_lon = phi - self.GMSTime*math.pi/180.
    	m_lon = math.fmod(m_lon, 2*math.pi) # fmod(m_lon, 2*M_PI) rest of the division of m_lon by 2Pi
    	if m_lon<math.pi:
	     m_lon+=2.*math.pi   # for -180 to 180?
    	if m_lon>math.pi:
	     m_lon-=2.*math.pi

    	# oblateness correction to obtain geodesic latitude 
    	m_lat = math.atan(math.tan(m_lat)) /( (1.-EARTH_FLAT)*(1.-EARTH_FLAT) ) 

    	# this is also such a correction: the number 0.00669454 is the geodesic eccentricity squared?
    	# see http://www.cage.curtin.edu.au/~will/gra64_05.pdf
    	# or http://www.colorado.edu/geography/gcraft/notes/datum/gif/ellipse.gif
    	m_altitude=math.sqrt(x*x+y*y)/math.cos(m_lat)\
    	           -EARTH_RADIUS / (1000.*math.sqrt(1.-math.pow(0.00669454*math.sin(m_lat), 2)))
        
	# convert latitude and longitude from radian to degree
	m_lat = math.degrees(m_lat)
	m_lon = math.degrees(m_lon)
	
        return (m_lat, m_lon, m_altitude)

    ## @brief Convert the quaternion to Euler angles
    ## From http://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles
    ## @param self
    #  The class instance.
    def getRockNRoll(self):
        # I have verified that the quaternion is normalized.
        # get the quaternion individual components
        q0 = self.Quaternion[0]
        q1 = self.Quaternion[1]
        q2 = self.Quaternion[2]
        q3 = self.Quaternion[3]
	# Invert the matrix and return angles in degrees
	theta = math.degrees(math.atan( 2*(q0*q1+q2*q3)/(1-2*(q1*q1+q2*q2)) ))
	phi   = math.degrees(math.asin( 2*(q0*q2-q3*q1) ))
	psi   = math.degrees(math.atan( 2*(q0*q3+q1*q2)/(1-2*(q2*q2+q3*q3)) ))
        
	return (theta, phi, psi)

    ## @brief Get the quaternion z axis pointing direction in equatorial coordinates (Ra, Dec)
    ## @param self
    #  The class instance.
    def getZaxisPointing(self):
        q = ROOT.TQuaternion(self.Quaternion[0], self.Quaternion[1], self.Quaternion[2], self.Quaternion[3])
	zaxis = q.Rotation(ROOT.TVector3(0,0,1))
	zra  = math.degrees(zaxis.Theta())
	zdec = math.degrees(zaxis.Phi())
        return (zra, zdec)

    ## @brief Get the quaternion x axis pointing direction in equatorial coordinates (Ra, Dec)
    ## @param self
    #  The class instance.
    def getXaxisPointing(self):
        q = ROOT.TQuaternion(self.Quaternion[0], self.Quaternion[1], self.Quaternion[2], self.Quaternion[3])
	xaxis = q.Rotation(ROOT.TVector3(1,0,0))
	xra  = math.degrees(xaxis.Theta())
	xdec = math.degrees(xaxis.Phi())
        return (xra, xdec)
    	
    ## @brief Call processing of the earth coordinates
    ## @param self
    #  The class instance.
    def processCoordinates(self):
        self.JulianDate = self.getGLASTDate(self.MetInSeconds)
        self.GMSTime    = self.getGMSTime(self.JulianDate)
        self.EarthCoordinates = self.getEarthCoordinate()
        self.Latitude  = self.EarthCoordinates[0]
        self.Longitude = self.EarthCoordinates[1]
        self.Altitude  = self.EarthCoordinates[2]
	self.PitchRollYaw = self.getRockNRoll()
	self.Pitch = self.PitchRollYaw[0]
	self.Roll  = self.PitchRollYaw[1]
	self.Yaw   = self.PitchRollYaw[2]
	self.Zaxis = self.getZaxisPointing()
	self.ZRa  = self.Zaxis[0]
	self.ZDec = self.Zaxis[1]
	self.Xaxis = self.getXaxisPointing()
	self.XRa  = self.Xaxis[0]
	self.XDec = self.Xaxis[1]
	
if __name__ == '__main__':
    sc = pSCPosition(2008.5, (252672900, 0))
    print sc

    
