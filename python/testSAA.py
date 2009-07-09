#!/bin/env python

from pM7Parser   import *
from pSafeROOT   import *
from pSAAPolygon import *

ROOT.gStyle.SetOptStat(0)

SAA_XML_FILE_PATH =\
   '/data/work/datamon/dataMonitoring/FastMonCfg/xml/saaDefinition.xml'
EARTH_GRID.GetYaxis().SetRangeUser(-30, 30)


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    (opts, arguments) = parser.parse_args()
    if len(arguments) != 1:
        parser.error('Please provide a (single) m7 file.')
        sys.exit()
    inputFilePath = arguments[0]
    gLon = ROOT.TGraph()
    gLat = ROOT.TGraph()
    gOrb = ROOT.TGraph()
    gSAADist = ROOT.TGraph()
    gSAAFlag = ROOT.TGraph()
    for g in [gLon, gLat, gSAADist, gSAAFlag, gOrb]:
        g.SetMarkerStyle(20)
        g.SetMarkerSize(0.4)
    gSAAFlag.SetLineColor(ROOT.kRed)
    gSAAFlag.SetMarkerColor(ROOT.kRed)
    parser = pM7Parser(inputFilePath, SAA_XML_FILE_PATH)
    parser.parseIt()
    for (i, met) in enumerate(parser.TimePoints):
        pos = parser.getSCPosition((met,0))
        pos.processCoordinates()
        lon = pos.getLongitude()
        lat = pos.getLatitude()
        dsaa = pos.getDistanceToSAA()
        fsaa = float(pos.OrbInSAA)
        if (dsaa < 0 and fsaa < 0) or (dsaa > 0 and fsaa > 0):
            print 'MET %.3f s (%.3f, %.3f): SAA dist. is %.2f km (flag %d)' %\
                  (met, lon, lat, dsaa, fsaa)
        gLon.SetPoint(i, met, lon)
        gLat.SetPoint(i, met, lat)       
        gOrb.SetPoint(i, lon, lat)
        gSAADist.SetPoint(i, met, dsaa)
        gSAAFlag.SetPoint(i, met, 1000*fsaa)
    for g in [gLon, gLat, gSAADist, gSAAFlag]:
        g.GetXaxis().SetTitle('Mission elapsed Time (s)')
    canvas = ROOT.TCanvas('saa', inputFilePath)
    canvas.Divide(2, 2)
    canvas.cd(1)
    gLon.GetYaxis().SetTitle('Longitude (degrees)')
    gLon.Draw('ap')
    canvas.cd(2)
    gLat.GetYaxis().SetTitle('Latitude (degrees)')
    gLat.Draw('ap')
    canvas.cd(3)
    gSAADist.GetYaxis().SetTitle('Distance to SAA (km)')
    gSAADist.Draw('ap')
    gSAAFlag.Draw('p,same')
    canvas.cd(4)
    EARTH_GRID.Draw();
    gOrb.Draw('p,same')
    parser.SAAPolygon.draw('same')
    canvas.Update()
    raw_input('Press enter to quit.')
