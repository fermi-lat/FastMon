## @package pGeomagProcessor
## @brief Basic module to handle the processing of geomagnetic quantities using the IGRF package

from IGRF import IGRF

## @brief The data processor implementation.
#
# from IGRF documentation
#
# Magnetic Model Data members:
# @li BNorth            : North component of the geomagnetic field (Gauss)
# @li  BEast             : East component of the geomagnetic field (Gauss)
# @li  BDown             : Down component of the geomagnetic field (Gauss)
# @li  BAbs              : Absolute value of the geomagnetic field (Gauss)
# @li  BEquator          : B field at the equator following the local field line (Gauss) 
# @li  BB0               : BAbs/BEquator
# @li  McIlwainL         : McIlwain L parameter
# @li  RigidityCutoff    : Rigidity cutoff in GV from approximation DipoleMoment/(McIlwain L)**2 
# @li  InvariantLatitude : Invariant magnetic Latitude 
# @li  InvariantLambda   : Invariant lambda parameter (only valid for BB0<10)
# @li  InvariantRadius   : Invariant radius (only valid for BB0<10)
# @li  DipoleMoment      : Dipole Moment of the Earth


class pGeomagProcessor:

    ## @brief Constructor.
    ## @param self
    #  The class instance.
    ## @param treeMaker
    #  The Tree maker object

    def __init__(self, treeMaker):

        ## @var TreeMaker
        ## @brief The Tree maker object

        ## @var FieldModel
        ## @brief The GeoMagnetic Field Model created using the IGRF library

        self.TreeMaker = treeMaker
        self.FieldModel = IGRF()

    ## @brief Return the tree branch corresponding to the variable name
    ## @param self
    #  The class instance.
    ## @param varName
    #  The variable name
    
    def getVariable(self, varName):
        return self.TreeMaker.getVariable(varName)

    ## @brief Process the geomagnetic quantities of the IGRF model given a space craft position
    ## @param self
    #  The class instance.
    ## @param sc
    #  A space craft position as an object of the @ref pSCPosition class
    def process(self, sc):
        yearfloat  = sc.getYearFloat()
	orbmode    = sc.getOrbMode()
	orbinsaa   = sc.getOrbInSAA()
        lat        = sc.getLatitude()
        lon        = sc.getLongitude()
        alt        = sc.getRelativeAltitude()/1000.
	pitch      = sc.getPitch()
	roll       = sc.getRoll()
	yaw        = sc.getYaw()
	rock       = sc.getRockAngle()
	xra        = sc.getXRa()
	xdec       = sc.getXDec()	
	yra        = sc.getYRa()
	ydec       = sc.getYDec()	
	zra        = sc.getZRa()
	zdec       = sc.getZDec()
	hor        = sc.getLimbAngle()	
	limb       = sc.getArcAngleEarthLimb()	
	zgalL      = sc.getZGalL()
        zgalB      = sc.getZGalB()
	
	# Spacecraft mode
	self.getVariable('spacecraft_orbit_mode')[0]  = orbmode
	self.getVariable('spacecraft_orbit_inSAA')[0] = orbinsaa
	
	# Spacecraft position
        self.getVariable('spacecraft_latitude')[0]  = lat
        self.getVariable('spacecraft_longitude')[0] = lon
        self.getVariable('spacecraft_altitude')[0]  = alt

	# Spacecraft attitude
        self.getVariable('spacecraft_pitch')[0] = pitch
        self.getVariable('spacecraft_roll')[0]  = roll
        self.getVariable('spacecraft_yaw')[0]   = yaw
        self.getVariable('spacecraft_rock')[0]  = rock

	# Spacecraft orientation
        self.getVariable('spacecraft_xra')[0]   = xra
        self.getVariable('spacecraft_xdec')[0]  = xdec
        self.getVariable('spacecraft_yra')[0]   = yra
        self.getVariable('spacecraft_ydec')[0]  = ydec
        self.getVariable('spacecraft_zra')[0]   = zra
        self.getVariable('spacecraft_zdec')[0]  = zdec
 
        self.getVariable('spacecraft_zgalL')[0]   = zgalL
        self.getVariable('spacecraft_zgalB')[0]   = zgalB
       
	# Earth limb arc angle in LAT field of View
        self.getVariable('spacecraft_earthlimb')[0]     = hor
        self.getVariable('spacecraft_earthlimb_fov')[0] = limb
	
	# Geomagnetic field
        self.FieldModel.compute(lat,lon,alt,yearfloat)
        self.getVariable('geomagnetic_cutoff')[0] = self.FieldModel.RigidityCutoff
        self.getVariable('geomagnetic_bb0')[0]    = self.FieldModel.BB0
        self.getVariable('geomagnetic_InvariantLambda')[0]   = self.FieldModel.InvariantLambda
        self.getVariable('geomagnetic_InvariantLatitude')[0] = self.FieldModel.InvariantLatitude
        self.getVariable('geomagnetic_InvariantRadius')[0]   = self.FieldModel.InvariantRadius
        self.getVariable('geomagnetic_McIlwainL')[0]         = self.FieldModel.McIlwainL
