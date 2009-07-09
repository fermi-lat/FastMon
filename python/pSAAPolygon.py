

import pSafeLogger
logger = pSafeLogger.getLogger('pSAAPolygon')

from pSafeROOT import ROOT

import sys
import os
import time

from math import sqrt, cos, sin, acos, pi, atan2

from pXmlBaseParser  import pXmlBaseParser
from pXmlBaseElement import pXmlBaseElement

EARTH_RADIUS = 6378145

DEG_TO_RAD = pi/180.
RAD_TO_DEG = 1./DEG_TO_RAD

MAX_LATITUDE  = 25.5652
MIN_LATITUDE  = - MAX_LATITUDE
MAX_LONGITUDE = 180.0
MIN_LONGITUDE = - MAX_LONGITUDE

EARTH_GRID = ROOT.TH2F('grid', 'grid', 1000, -180, 180, 1000, -180, 180)
EARTH_GRID.GetXaxis().SetTitle('Longitude (degrees)')
EARTH_GRID.GetYaxis().SetTitle('Latitude (degrees)')

def getDistanceOnSphere(v1, v2):
    b = DEG_TO_RAD*(90 - v1.Lat)
    c = DEG_TO_RAD*(90 - v2.Lat)
    A = DEG_TO_RAD*(v1.Lon - v2.Lon)
    return EARTH_RADIUS/1000.*acos(cos(b)*cos(c) + sin(b)*sin(c)*cos(A))


class pVertex:

    def __init__(self, lon, lat, label = None, color = ROOT.kBlue, style = 20):
        self.Lon = lon
        self.Lat = lat
        self.Label = label
        self.RootMarker = ROOT.TMarker(self.Lon, self.Lat, style)
        self.setColor(color)
        if self.Label is not None:
            self.RootLabel = ROOT.TLatex(self.Lon, self.Lat, self.Label)
            self.RootLabel.SetTextSize(0.03)

    def setColor(self, color):
        self.RootMarker.SetMarkerColor(color)

    def setStyle(self, style):
        self.RootMarker.SetMarkerStyle(style)

    def getDistance(self, lon, lat):
        return sqrt((lon - self.Lon)**2 + (lat - self.Lat)**2)

    def draw(self, options = ''):
        self.RootMarker.Draw(options)
        if self.Label is not None:
            self.RootLabel.Draw(options)

    def __add__(self, other):
        return pVertex(self.Lon + other.Lon, self.Lat + other.Lat, self.Label,
                       self.RootMarker.GetMarkerColor(),
                       self.RootMarker.GetMarkerStyle())

    def __div__(self, value):
        value = float(value)
        return pVertex(self.Lon/value, self.Lat/value, self.Label,
                       self.RootMarker.GetMarkerColor(),
                       self.RootMarker.GetMarkerStyle())

    def __str__(self):
        return '(%.1f, %.1f)' % (self.Lon, self.Lat)


class pSegment:

    def __init__(self, vertex1, vertex2, color = ROOT.kBlue):
        self.Vertex1  = vertex1
        self.Vertex2  = vertex2
        self.Length   = sqrt((self.Vertex2.Lon - self.Vertex1.Lon)**2 +\
                             (self.Vertex2.Lat - self.Vertex1.Lat)**2)
        self.RootLine = ROOT.TLine(vertex1.Lon, vertex1.Lat, vertex2.Lon,
                                   vertex2.Lat)
        self.setWidth(2)
        self.setColor(color)

    def setColor(self, color):
        self.RootLine.SetLineColor(color)

    def setWidth(self, width):
        self.RootLine.SetLineWidth(width)

    def draw(self, options = ''):
        self.RootLine.Draw(options)

    def __str__(self):
        return '%s--%s' % (self.Vertex1, self.Vertex2)


class pSAAPolygon:

    def __init__(self, xmlFilePath):
        self.VertexList  = []
        self.SegmentList = []
        self.AngleList   = []
        doc = pXmlBaseElement(pXmlBaseParser(xmlFilePath).XmlDoc)
        for element in doc.getElementsByTagName('vertex'):
            element = pXmlBaseElement(element)
            longitude = element.evalAttribute('longitude')
            latitude  = element.evalAttribute('latitude')
            vertex = pVertex(longitude, latitude, '%d' % len(self.VertexList))
            logger.debug('Adding vertex %s...' % vertex)
            self.VertexList.append(vertex)
        tempList = self.VertexList + [self.VertexList[0]]
        for i in range(self.getNumVertices()):
            line = pSegment(tempList[i], tempList[i + 1])
            self.SegmentList.append(line)
        self.Center = pVertex(0, 0, 'c', ROOT.kRed, 29)
        for vertex in self.VertexList:
            self.Center += vertex
        self.Center /= self.getNumVertices()
        for vertex in self.VertexList:
            self.AngleList.append(self.getAngleToCenter(vertex))

    def getNumVertices(self):
        return len(self.VertexList)

    def draw(self, options = ''):
        for vertex in self.VertexList:
            vertex.draw()
        for segment in self.SegmentList:
            segment.draw()
        self.Center.draw()

    def getDistanceToCenter(self, v):
        return getDistanceOnSphere(self.Center, v)

    def getAngleToCenter(self, v):
        return RAD_TO_DEG*atan2(v.Lon - self.Center.Lon,
                                v.Lat - self.Center.Lat)

    ## @brief Return the segment which is crossed by the straigh line
    #  conecting a generic vertex v to the center of the SAA.
    ## @param self
    #  The class instance.
    ## @param v
    #  The vertex to be connected with the center.

    def getCrossSegment(self, v):
        angle = self.getAngleToCenter(v)
        for (i, vertex) in enumerate(self.VertexList):
            if self.getAngleToCenter(vertex) > angle:
                return self.SegmentList[i-1]
        return self.SegmentList[-1]

    def getDistanceToBorder(self, v):
        crossSegment = self.getCrossSegment(v)
        (x1, y1) = (self.Center.Lon, self.Center.Lat)
        (x2, y2) = (v.Lon, v.Lat)
        (x3, y3) = (crossSegment.Vertex1.Lon, crossSegment.Vertex1.Lat)
        (x4, y4) = (crossSegment.Vertex2.Lon, crossSegment.Vertex2.Lat)
        u = ((x4-x3)*(y1-y3) - (y4-y3)*(x1-x3))/\
            ((y4-y3)*(x2-x1) - (x4-x3)*(y2-y1))
        x = x1 + u*(x2-x1) 
        y = y1 + u*(y2-y1)
        intersectionVertex = pVertex(x, y, 'i', ROOT.kBlack)
        distance = self.getDistanceToCenter(v) -\
                   self.getDistanceToCenter(intersectionVertex)
        if distance < 0:
            distance = -999
        return distance


if __name__ == '__main__':
    ROOT.gStyle.SetOptStat(0)

    v1 = pVertex(90, 20, 't1', ROOT.kBlack, 24)
    v2 = pVertex(-40, -10, 't2', ROOT.kBlack, 24)    
    polygon = pSAAPolygon('../../FastMonCfg/xml/saaDefinition.xml')
    EARTH_GRID.Draw()
    polygon.draw()
    v1.draw()
    v2.draw()
    ROOT.gPad.SetGridx(True)
    ROOT.gPad.SetGridy(True)
    print polygon.getDistanceToCenter(v1)
    print polygon.getDistanceToBorder(v1)
    print polygon.getDistanceToCenter(v2)
    print polygon.getDistanceToBorder(v2)
    ROOT.gPad.Update()
    
    def getLatitude(t):
        return MAX_LATITUDE*sin(t/911.835)

    def getLongitude(t):
        return (0.0585416*t)%360 - 180

    numDays = 1
    stepsPerSec = 1
    c = ROOT.TCanvas('Distance to SAA border')
    g = ROOT.TGraph()
    for i in xrange(3600*24*numDays*stepsPerSec):
        t = float(i)/stepsPerSec
        v = pVertex(getLongitude(t), getLatitude(t))
        d = polygon.getDistanceToBorder(v)
        g.SetPoint(i, t, d)
    g.Draw('ALP')
    g.GetXaxis().SetTitle('Time (s)')
    g.GetYaxis().SetTitle('Distance to SAA (km)')
    c.Update()
