from igrf import IGRF

## from IGRF documentation
## Magnetic Model Data members:
##  BNorth            : North component of the geomagnetic field (Gauss)
##  BEast             : East component of the geomagnetic field (Gauss)
##  BDown             : Down component of the geomagnetic field (Gauss)
##  BAbs              : Absolute value of the geomagnetic field (Gauss)
##  BEquator          : B field at the equator following the local field line (Gauss) 
##  BB0               : BAbs/BEquator
##  McIlwainL         : McIlwain L parameter
##  RigidityCutoff    : Rigidity cutoff in GV from approximation DipoleMoment/(McIlwain L)**2 
##  InvariantLatitude : Invariant magnetic Latitude 
##  InvariantLambda   : Invariant lambda parameter (only valid for BB0<10)
##  InvariantRadius   : Invariant radius (only valid for BB0<10)
##  DipoleMoment      : Dipole Moment of the Earth


class pGeomagProcessor:

    def __init__(self, treeMaker):
        self.TreeMaker = treeMaker
        self.FieldModel = IGRF()

    def getVariable(self, varName):
        return self.TreeMaker.getVariable(varName)

    def process(self, sc):
        yearfloat  = sc.getYearFloat()
        lat        = sc.getLatitude()
        lon        = sc.getLongitude()
        alt        = sc.getRelativeAltitude()/1000.
	
        self.getVariable('spacecraft_altitude')[0] = alt	
	
        self.FieldModel.compute(lat,lon,alt,yearfloat)
        self.getVariable('geomagnetic_cutoff')[0] = self.FieldModel.RigidityCutoff
        self.getVariable('geomagnetic_bb0')[0] = self.FieldModel.BB0
        self.getVariable('geomagnetic_InvariantLambda')[0] = self.FieldModel.InvariantLambda
        self.getVariable('geomagnetic_InvariantLatitude')[0] = self.FieldModel.InvariantLatitude
        self.getVariable('geomagnetic_InvariantRadius')[0] = self.FieldModel.InvariantRadius
        self.getVariable('geomagnetic_McIlwainL')[0] = self.FieldModel.McIlwainL
