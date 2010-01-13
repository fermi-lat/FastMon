import pSafeLogger
logger = pSafeLogger.getLogger('drawOrbit2d')

import time

from pM7Parser     import *
from pSafeROOT     import *
from pSAAPolygon   import *
from pOptionParser import *

ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPadTopMargin(0.03)
ROOT.gStyle.SetPadLeftMargin(0.08)
ROOT.gStyle.SetPadRightMargin(0.01)
ROOT.gStyle.SetPadBottomMargin(0.1)

EARTH_GRID.GetYaxis().SetRangeUser(-30, 30)

# Time difference between two consecutive time steps.
DELTA_TIME_STEP_MIN = 10
DELTA_TIME_STEP_SEC = DELTA_TIME_STEP_MIN*60

# Parameters for the SAA POCA
SAA_POCA_TIME_PADDING_MIN = 10
SAA_POCA_TIME_PADDING_SEC = SAA_POCA_TIME_PADDING_MIN*60
SAA_POCA_MAX_DISTANCE = 750

MET_OFFSET = 978307200


class pTimeStep:

    def __init__(self, met, longitude, latitude, labelText = '',
                 textAlign = 12, color = ROOT.kBlack):
        self.Met = met
        self.Longitude = longitude
        self.Latitude = latitude
        self.LabelText = labelText
        self.__setupMarker(color)
        self.__setupLabel(color, textAlign)

    def __setupMarker(self, color, style = 20, size = 1):
        self.Marker = ROOT.TMarker(self.Longitude, self.Latitude, style)
        self.Marker.SetMarkerSize(size)
        self.Marker.SetMarkerColor(color)

    def __setupLabel(self, color, textAlign, textAngle = 0, textSize = 0.035):
        self.Label = ROOT.TLatex(self.Longitude, self.Latitude, self.LabelText)
        self.Label.SetTextAngle(textAngle)
        self.Label.SetTextSize(textSize)
        self.Label.SetTextColor(color)
        self.Label.SetTextAlign(textAlign)

    def adjustAlignment(self):
        textAlign = self.Label.GetTextAlign()
        # From the ROOT documentation:
        # align = 10*HorizontalAlign + VerticalAlign
        # For Horizontal alignment the following convention applies:
        # 1=left adjusted, 2=centered, 3=right adjusted
        # For Vertical alignment the following convention applies:
        # 1=bottom adjusted, 2=centered, 3=top adjusted
        horAlign = textAlign/10
        verAlign = textAlign - horAlign*10
        x = self.Label.GetX()
        dx = self.Label.GetXsize()
        #print horAlign, self.Label.GetX(), self.Label.GetXsize()
        xmax = x + 0.5*(3 - horAlign)*dx
        xmin = x + 0.5*(1 - horAlign)*dx
        if xmax > 180 and horAlign == 1:
            horAlign = 3
        textAlign = 10*horAlign + verAlign
        self.Label.SetTextAlign(textAlign)

    def draw(self, options = 'm'):
        if 'm' in options:
            self.Marker.Draw()
        if 'l' in options:
            self.Label.Draw()

    def __str__(self):
        return 'met = %s, position = (%.2f, %.2f)' %\
               (self.Met, self.Longitude, self.Latitude)


def metToDate(met, fmtstring = '%b %d, %Y %H:%M:%S'):
    return time.strftime(fmtstring, time.gmtime(met + MET_OFFSET))


def getCoordinates(position):
    position.processCoordinates()
    lon = position.getLongitude()
    lat = position.getLatitude()
    dsaa = position.getDistanceToSAA()
    return (lon, lat, dsaa)

    

if __name__ == '__main__':
    optparser = pOptionParser('so', 1, 1, False)
    orbit = ROOT.TGraph()
    orbit.SetMarkerStyle(20)
    orbit.SetMarkerSize(0.15)
    equator = ROOT.TLine(-180, 0, 180, 0)
    equator.SetLineStyle(7)
    timeSteps = []
    parser = pM7Parser(optparser.Argument, optparser.Options.s)
    startMet = parser.TimePoints[0]
    stopMet = parser.TimePoints[-1]
    saaDoca = SAA_POCA_MAX_DISTANCE
    saaPoca = None
    logger.info('Looping over the input file...')
    for (i, met) in enumerate(parser.TimePoints[:-1]):
        secFromStart = met - startMet
        secToEnd = stopMet - met
        position = parser.getSCPosition((met, 0))
        (lon, lat, dsaa) = getCoordinates(position)
        orbit.SetPoint(i, lon, lat)
        if i == 0:
            startDate = metToDate(met)
            labelText = '  Start: %s  ' % startDate
            timeSteps.append(pTimeStep(met, lon, lat, labelText, 11))
            logger.info('Run started on %s (approximately); %s.' %\
                        (startDate, timeSteps[-1]))
        else:
            if (met - timeSteps[-1].Met) > DELTA_TIME_STEP_SEC:
                elapsedMin = DELTA_TIME_STEP_MIN*len(timeSteps)
                labelText = '#splitline{+%d min}{}' % elapsedMin
                timeSteps.append(pTimeStep(met, lon, lat, labelText, 21, 921))
        if secFromStart > SAA_POCA_TIME_PADDING_SEC and \
           secToEnd > SAA_POCA_TIME_PADDING_SEC:
            if dsaa < saaDoca:
                saaDoca = dsaa
                saaPocaDate = metToDate(met, '%H:%M:%S')
                labelText = '  SAA POCA: %s (~%d km)' % (saaPocaDate, dsaa)
                saaPoca = pTimeStep(met, lon, lat, labelText, 11, 632)
    stopDate = metToDate(met)
    labelText = '  Stop: %s  ' % stopDate
    timeSteps.append(pTimeStep(met, lon, lat, labelText, 13))
    logger.info('Run stopped on %s (approximately); %s.' %\
                (stopDate, timeSteps[-1]))
    if saaPoca is not None:
        logger.info('POCA to SAA around %s (DOCA ~ %d km)' %\
                    (saaPocaDate, saaDoca))
    logger.info('Done.')
    
    canvas = ROOT.TCanvas('orbit', 'Orbit 2D', 1000, 500)
    canvas.SetGridx(True)
    canvas.SetGridy(True)
    EARTH_GRID.Draw()
    parser.SAAPolygon.draw('v')
    equator.Draw()
    orbit.Draw('psame')
    for timeStep in timeSteps:
        timeStep.draw('ml')
    if saaPoca is not None:
        saaPoca.draw('ml')
    canvas.Update()
    for timeStep in timeSteps:
        timeStep.adjustAlignment()
    if optparser.Options.o is not None:
        canvas.SaveAs(optparser.Options.o)
