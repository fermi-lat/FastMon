## @package pGeomagProcessor
## @brief Basic module to handle the processing of geomagnetic quantities using the IGRF package

from igrf import IGRF

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
        lat        = sc.getLatitude()
        lon        = sc.getLongitude()
        alt        = sc.getRelativeAltitude()/1000.
	
        self.getVariable('spacecraft_altitude')[0] = alt
	
        self.FieldModel.compute(lat,lon,alt,yearfloat)
        self.getVariable('geomagnetic_cutoff')[0] = self.FieldModel.RigidityCutoff
        self.getVariable('geomagnetic_bb0')[0]    = self.FieldModel.BB0
        self.getVariable('geomagnetic_InvariantLambda')[0]   = self.FieldModel.InvariantLambda
        self.getVariable('geomagnetic_InvariantLatitude')[0] = self.FieldModel.InvariantLatitude
        self.getVariable('geomagnetic_InvariantRadius')[0]   = self.FieldModel.InvariantRadius
        self.getVariable('geomagnetic_McIlwainL')[0]         = self.FieldModel.McIlwainL
