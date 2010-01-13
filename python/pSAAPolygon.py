

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

    def draw(self, options = 'l'):
        self.RootMarker.Draw()
        if self.Label is not None and 'l' in options:
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

    def draw(self, options = 'vlc'):
        if 'v' in options:
            for vertex in self.VertexList:
                vertex.draw('l'*('l' in options))
        for segment in self.SegmentList:
            segment.draw()
        if 'c' in options:
            self.Center.draw()

    def getDistanceToCenter(self, v):
        return getDistanceOnSphere(self.Center, v)

    def getAngleToCenter(self, v):
        return RAD_TO_DEG*atan2(v.Lon - self.Center.Lon,
                                v.Lat - self.Center.Lat)

    def getCrossSegments(self, v):
        s1 = None
        s2 = None
        angle = self.getAngleToCenter(v)
        if angle > 0:
            shift = -180
        else:
            shift = 180
        for segment in self.SegmentList:
            angle1 = self.getAngleToCenter(segment.Vertex1)
            angle2 = self.getAngleToCenter(segment.Vertex2)
            if (angle > angle1 and angle < angle2):
                s1 = segment
            if (angle + shift > angle1 and angle + shift < angle2):
                s2 = segment
        if s2 is None:
            s2 = self.SegmentList[-1]
        return (s1, s2)

    def __getDistanceToBorder(self, v):
        # Get the two SAA segments crossed by the straight line joining
        # a generic point to the SAA center.
        (s1, s2) = self.getCrossSegments(v)
        (x1, y1) = (self.Center.Lon, self.Center.Lat)
        (x2, y2) = (v.Lon, v.Lat)
        # Distance of the point to the intersection point between the
        # straight line to the SAA center and the first segment crossed
        # by the line itself.
        (x3, y3) = (s1.Vertex1.Lon, s1.Vertex1.Lat)
        (x4, y4) = (s1.Vertex2.Lon, s1.Vertex2.Lat)
        u = ((x4-x3)*(y1-y3) - (y4-y3)*(x1-x3))/\
            ((y4-y3)*(x2-x1) - (x4-x3)*(y2-y1))
        x = x1 + u*(x2-x1) 
        y = y1 + u*(y2-y1)
        p1 = pVertex(x, y, 'i', ROOT.kBlack)
        d1 = getDistanceOnSphere(v, p1)
        # Distance of the point to the intersection point between the
        # straight line to the SAA center and the second segment crossed
        # by the line itself.
        (x3, y3) = (s2.Vertex1.Lon, s2.Vertex1.Lat)
        (x4, y4) = (s2.Vertex2.Lon, s2.Vertex2.Lat)
        u = ((x4-x3)*(y1-y3) - (y4-y3)*(x1-x3))/\
            ((y4-y3)*(x2-x1) - (x4-x3)*(y2-y1))
        x = x1 + u*(x2-x1) 
        y = y1 + u*(y2-y1)
        p2 = pVertex(x, y, 'i', ROOT.kBlack)
        d2 = getDistanceOnSphere(v, p2)
        d = min(d1, d2)
        # We're inside the SAA if the distance to the center is smaller than
        # the distance between any of the two intersection points
        # and the center itself: change sign.
        if self.getDistanceToCenter(v) <  self.getDistanceToCenter(p1):
            d *= -1
        return d

    def getDistanceToBorder(self, v, lonPadding = 10.0):
        # Dirty trick to get rid of discontinuities: when close to lon = 180
        # make a weighted average between the distance at lon and the one
        # at -lon.
        pad = float(abs(abs(v.Lon) - 180))
        if pad > lonPadding:
            return self.__getDistanceToBorder(v)
        d1 = self.__getDistanceToBorder(v)
        d2 = self.__getDistanceToBorder(pVertex(-v.Lon, v.Lat))
        weight = 1 - abs(lonPadding - pad)/(2*lonPadding)
        return d1*weight + d2*(1 - weight)
    


if __name__ == '__main__':
    ROOT.gStyle.SetOptStat(0)

    v1 = pVertex(90, 20, 't1', ROOT.kBlack, 24)
    v2 = pVertex(-40, -10, 't2', ROOT.kBlack, 24)
    v3 = pVertex(-150.5, 15, 't3', ROOT.kBlack, 24)
    polygon = pSAAPolygon('../../FastMonCfg/xml/saaDefinition.xml')
    EARTH_GRID.Draw()
    polygon.draw()
    v1.draw()
    v2.draw()
    v3.draw()
    ROOT.gPad.SetGridx(True)
    ROOT.gPad.SetGridy(True)
    print polygon.getDistanceToCenter(v1)
    print polygon.getDistanceToBorder(v1)
    print polygon.getDistanceToCenter(v2)
    print polygon.getDistanceToBorder(v2)
    print polygon.getDistanceToCenter(v3)
    print polygon.getDistanceToBorder(v3)
    ROOT.gPad.Update()
    
    def getLatitude(t):
        return MAX_LATITUDE*sin(t/911.835)

    def getLongitude(t):
        return (0.0585416*t)%360 - 180

    """
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
    """
