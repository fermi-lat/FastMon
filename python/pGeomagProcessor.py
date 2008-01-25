from igrf import IGRF


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
        self.FieldModel.compute(lat,lon,alt,yearfloat)

        self.getVariable('geomagnetic_cutoff')[0] = self.FieldModel.RigidityCutoff
