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

    def __init__(self, time,yearfloat = None, position=None):
       ## @var YearFloat
       ## @brief A float representing the Year and Month of the data
       
       ## @var MetInSeconds
       ## @brief The Mission Elapsed Time in seconds
       
       ## @var MetMicroSeconds
       ## @brief The microseconds part of the Mission Elapsed Time
       
       ## @var Position
       ## @brief The space craft position on orbit in meters, as a 3D tuple (X, Y, Z) in ECI J2000 coordinates
       
       ## @var EarthCoordinates
       ## @brief The space craft position in the earth coordinates as a 3D tuple (Latitude, Longitude, Altitude)
       
       ## @var Latitude
       ## @brief The space craft latitude
       
       ## @var Longitude
       ## @brief The space craft longitude
       
       ## @var Altitude
       ## @brief The space craft altitude relative to the Earth center
       
       ## @var JulianDate
       ## @brief The Time stamp as a Julian Date.
       
       ## @var GMSTime
       ## @brief The Time stamp in the Greenwich Meridian Sideral Time 

       self.YearFloat  = yearfloat
       self.MetInSeconds    = int(time[0])
       self.MetMicroSeconds = int(time[1])
       self.Position   = position
       self.EarthCoordinates = (None, None, None)
       self.Latitude  = None
       self.Longitude = None
       self.Altitude  = None
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
	      +'Earth Coords (lat, long, alt)= (%s, %s, %s)\n' % self.EarthCoordinates 

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
        D = 30.6001 * (Me + 1)
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
    ## @param self
    #  The class instance is actually not used in this stand alone function
    ## @param jd
    #  A Julian Date
    def getGMSTime(self, jd):
	# integer part
	M=math.modf(jd-0.5)[1] 
	# fractional part
	Ora_Un_Dec = math.modf(jd-0.5)[0]*24 
	
	jd-=Ora_Un_Dec/24
	
     	T = (jd - self.getJ2000()) / 36525.
     	T1 = (24110.54841 + 8640184.812866 * T + 0.0093103 * T * T)/86400.0
     	
	Tempo_Siderale_0 = math.modf(T1)[0] * 24.
     	Tempo_Siderale_Ora = Tempo_Siderale_0 + Ora_Un_Dec * 1.00273790935
        
	if Tempo_Siderale_Ora < 0.:
	    Tempo_Siderale_Ora = Tempo_Siderale_Ora + 24.
        if Tempo_Siderale_Ora >= 24.:
	     Tempo_Siderale_Ora = Tempo_Siderale_Ora - 24.
        
	return float(Tempo_Siderale_Ora*15.)



    ## @brief Calculate and return the space craft position in Earth coordinates
    ## @param self
    #  The class instance.
    def getEarthCoordinate(self):
 	x = self.Position[0]
	y = self.Position[1]
	z = self.Position[2]
	r = math.sqrt(x*x + y*y + z*z)
	theta = math.acos(z/r)
	phi   = math.atan(y/x)
	
	# Latitude
        m_lat = math.pi/2. - theta
    		
    	# Longitude
	m_lon = phi - self.GMSTime*math.pi/180.
    	m_lon = math.modf(m_lon/(2*math.pi))[0] # fmod(m_lon, 2*M_PI) rest of the division of m_lon by 2Pi
    	if m_lon<math.pi:
	     m_lon+=2.*math.pi   # for -180 to 180?
    	if m_lon>math.pi:
	     m_lon-=2.*math.pi

    	# oblateness correction to obtain geodedic latitude 
    	m_lat = math.atan(math.tan(m_lat)) /( (1.-EARTH_FLAT)*(1.-EARTH_FLAT) ) 

    	# this is also such a correction: the number 0.00669454 is the geodetic eccentricity squared?
    	# see http://www.cage.curtin.edu.au/~will/gra64_05.pdf
    	# or http://www.colorado.edu/geography/gcraft/notes/datum/gif/ellipse.gif
    	m_altitude=math.sqrt(x*x+y*y)/math.cos(m_lat)\
    	           -EARTH_RADIUS / (1000.*math.sqrt(1.-math.pow(0.00669454*math.sin(m_lat), 2)))

        return (m_lat, m_lon, m_altitude)
	
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


	
if __name__ == '__main__':
    sc = pSCPosition(2008.5, (252672900, 0))
    print sc

    
