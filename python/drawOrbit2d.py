import pSafeLogger
logger = pSafeLogger.getLogger('drawOrbit2d')

from pM7Parser     import *
from pSafeROOT     import *
from pSAAPolygon   import *
from pOptionParser import *

import pTimeUtils

ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPadTopMargin(0.03)
ROOT.gStyle.SetPadLeftMargin(0.08)
ROOT.gStyle.SetPadRightMargin(0.01)
ROOT.gStyle.SetPadBottomMargin(0.1)

MIN_LON = -180
MAX_LON = 180
MIN_LAT = -30
MAX_LAT = 30
EARTH_GRID.GetXaxis().SetRangeUser(MIN_LON, MAX_LON)
EARTH_GRID.GetYaxis().SetRangeUser(MIN_LAT, MAX_LAT)


class pTimeStep:

    def __init__(self, met, longitude, latitude, labelText = '',
                 textAlign = 12, color = ROOT.kBlack, labelVertOffset = 0):
        self.Met = met
        self.Longitude = longitude
        self.Latitude = latitude
        self.LabelText = labelText
        self.__setupMarker(color)
        self.__setupLabel(color, textAlign, labelVertOffset)

    def __setupMarker(self, color, style = 20, size = 1):
        self.Marker = ROOT.TMarker(self.Longitude, self.Latitude, style)
        self.Marker.SetMarkerSize(size)
        self.Marker.SetMarkerColor(color)

    def __setupLabel(self, color, textAlign, vertOffset, textAngle = 0,
                     textSize = 0.035):
        self.Label = ROOT.TLatex(self.Longitude, self.Latitude + vertOffset,\
                                 self.LabelText)
        self.Label.SetTextAngle(textAngle)
        self.Label.SetTextSize(textSize)
        self.Label.SetTextColor(color)
        self.Label.SetTextAlign(textAlign)
        # Adjust the alignment
        #
        # From the ROOT documentation:
        # align = 10*HorizontalAlign + VerticalAlign
        # For Horizontal alignment the following convention applies:
        # 1=left adjusted, 2=centered, 3=right adjusted
        # For Vertical alignment the following convention applies:
        # 1=bottom adjusted, 2=centered, 3=top adjusted
        horAlign = textAlign/10
        verAlign = textAlign - horAlign*10
        x = self.Label.GetX()
        # Estimate the label width once on the canvas
        # This is not exact as is it does not take into account the fact the
        # font is not monospace. The issue here is that ROOT won't tell the
        # actual width of the TLatex object until it is drawn on the canvas,
        # and this does not work well in batch mode.
        # The 80 factor is put in by hand, in case sombody cares.
        dx = 80.*len(self.LabelText)*self.Label.GetTextSize()
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


class pOrbitViewer:

    def __init__(self, m7FilePath, saaFilePath):
        self.Orbit = ROOT.TGraph()
        self.Orbit.SetMarkerStyle(20)
        self.Orbit.SetMarkerSize(0.15)
        self.Equator = ROOT.TF1('equator', '0', MIN_LON, MAX_LON)
        self.Equator.SetLineStyle(7)
        self.Equator.SetLineWidth(1)
        self.TimeSteps = []
        self.M7Parser = pM7Parser(m7FilePath, saaFilePath)
        self.StartMet = self.M7Parser.TimePoints[0]
        self.StopMet  = self.M7Parser.TimePoints[-1]
        self.SaaPoca  = None

    def getCoordinates(self, position):
        position.processCoordinates()
        lon = position.getLongitude()
        lat = position.getLatitude()
        dsaa = position.getDistanceToSAA()
        return (lon, lat, dsaa)

    def run(self, deltaTimeStepMin, saaPocaTimePaddingMin, saaPocaMaxDistance):
        deltaTimeStepSec = deltaTimeStepMin*60.
        saaPocaTimePaddingSec = saaPocaTimePaddingMin*60
        saaDoca = saaPocaMaxDistance
        logger.info('Looping over the input file...')
        for (i, met) in enumerate(self.M7Parser.TimePoints[:-1]):
            secFromStart = met - self.StartMet
            secToEnd = self.StopMet - met
            position = self.M7Parser.getSCPosition((met, 0))
            (lon, lat, dsaa) = self.getCoordinates(position)
            self.Orbit.SetPoint(i, lon, lat)
            if i == 0:
                date = pTimeUtils.met2utc(met, '%b %d, %Y %H:%M:%S')
                text = '  M7 start: %s  ' % date
                timeStep = pTimeStep(met, lon, lat, text, 11, ROOT.kBlack,
                                     0.5*(abs(lat) < 0.1))
                self.TimeSteps.append(timeStep)
                logger.info('M7 starting at %s, %s.' % (date, timeStep))
            else:
                if (met - timeStep.Met) > deltaTimeStepSec:
                    elapsedMinutes = deltaTimeStepMin*len(self.TimeSteps)
                    text = '+%d min' % elapsedMinutes
                    timeStep = pTimeStep(met, lon, lat, text,
                                         21, ROOT.kGray+1, 1)
                    self.TimeSteps.append(timeStep)
            if secFromStart > saaPocaTimePaddingSec and \
                   secToEnd > saaPocaTimePaddingSec:
                if dsaa < saaDoca:
                    saaDoca = dsaa
                    date = pTimeUtils.met2utc(met, '%H:%M:%S')
                    text = '  SAA POCA: %s (~%d km)' % (date, dsaa)
                    self.SaaPoca = pTimeStep(met, lon, lat, text, 11,
                                             ROOT.kRed)
        date = pTimeUtils.met2utc(met, '%b %d, %Y %H:%M:%S')
        text = '  M7 stop: %s  ' % date
        timeStep = pTimeStep(met, lon, lat, text, 13, ROOT.kBlack,
                             -0.5*(abs(lat) < 0.1))
        self.TimeSteps.append(timeStep)
        logger.info('M7 ending at %s, %s.' % (date, timeStep))
        if self.SaaPoca is not None:
            logger.info('SAA DOCA ~ %d km' %  saaDoca)
        logger.info('Done.')

    def getPocaWindow(self, timePadding):
        logger.info('Retrieving the POCA window for the zoomed plot...')
        timePadding *= 60
        minLon = MAX_LON
        maxLon = MIN_LON
        minLat = MAX_LAT
        maxLat = MIN_LAT
        for (i, met) in enumerate(self.M7Parser.TimePoints[:-1]):
            if abs(met - self.SaaPoca.Met) < timePadding:
                position = self.M7Parser.getSCPosition((met, 0))
                (lon, lat, dsaa) = self.getCoordinates(position)
                if lon < minLon:
                    minLon = lon
                if lon > maxLon:
                    maxLon = lon
                if lat < minLat:
                    minLat = lat
                if lat > maxLat:
                    maxLat = lat
        logger.info('Done, window is (%.2f--%.2f, %.2f--%.2f)' %\
                    (minLon, maxLon, minLat, maxLat))
        return (minLon, maxLon, minLat, maxLat)

    def createImage(self, interactive, width, zoomTimePadding):
        height = int(width*0.45)
        if self.SaaPoca is None or zoomTimePadding is None:
            self.Canvas = ROOT.TCanvas('orbit', 'Orbit 2D', width, height)
            self.Canvas.SetGridx(True)
            self.Canvas.SetGridy(True)
        else:
            height *= 2
            self.Canvas = ROOT.TCanvas('orbit', 'Orbit 2D', width, height)
            self.Canvas.Divide(1, 2)
            self.Canvas.cd(1)
            self.Canvas.GetPad(1).SetGridx(True)
            self.Canvas.GetPad(1).SetGridy(True)
        EARTH_GRID.DrawCopy()
        self.M7Parser.SAAPolygon.draw('v')
        self.Equator.Draw('same')
        self.Orbit.Draw('psame')
        for timeStep in self.TimeSteps:
            timeStep.draw('ml')
        if self.SaaPoca is not None:
            self.SaaPoca.draw('ml')
            if zoomTimePadding is not None:
                self.Canvas.cd(2)
                self.Canvas.GetPad(2).SetGridx(True)
                self.Canvas.GetPad(2).SetGridy(True)
                (minLon, maxLon, minLat, maxLat) =\
                         self.getPocaWindow(zoomTimePadding)
                EARTH_GRID.GetXaxis().SetRangeUser(minLon, maxLon)
                EARTH_GRID.GetYaxis().SetRangeUser(minLat, maxLat)
                EARTH_GRID.DrawCopy()
                self.M7Parser.SAAPolygon.draw('v')
                self.Equator.Draw('same')
                self.Orbit.Draw('psame')
                self.SaaPoca.draw('ml')
        self.Canvas.Update()
        if interactive:
            raw_input('Press enter to quit.')

    def saveImage(self, outputFilePath):
        self.Canvas.Update()
        self.Canvas.SaveAs(outputFilePath)

        



if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-o', '--output-file', dest = 'o',
                      default = None, type = str,
                      help = 'path to the output file')
    parser.add_option('-v', '--verbose', dest = 'v',
                      default = False, action = 'store_true',
                      help = 'print (a lot of!) debug messages')
    parser.add_option('-s', '--saa-def-file-path', dest = 's',
                      default = None, type = str,
                      help = 'path to the SAA definition file')
    parser.add_option('-i', '--interactive', dest = 'i',
                      default = False, action = 'store_true',
                      help = 'run interactively.')
    parser.add_option('-t', '--time-step', dest = 't',
                      default = 10.0, type = float,
                      help = 'time step (in min) for labels')
    parser.add_option('-p', '--time-padding', dest = 'p',
                      default = 10.0, type = float,
                      help = 'time padding (in min) for SAA POCAs')
    parser.add_option('-z', '--zoom-time-padding', dest = 'z',
                      default = None, type = float,
                      help = 'time padding (in min) for SAA POCAs')
    parser.add_option('-d', '--max-poca-distance', dest = 'd',
                      default = 750.0, type = float,
                      help = 'max distance (in km) for SAA POCAs')
    parser.add_option('-w', '--canvas-width', dest = 'w',
                      default = 1000, type = int,
                      help = 'canvas width')
    (opts, args) = parser.parse_args()

    if not opts.i:
        ROOT.gROOT.SetBatch(True)
    viewer = pOrbitViewer(args[0], opts.s)
    viewer.run(opts.t, opts.p, opts.d)
    viewer.createImage(opts.i, opts.w, opts.z)
    if opts.o is not None:
        viewer.saveImage(opts.o)
