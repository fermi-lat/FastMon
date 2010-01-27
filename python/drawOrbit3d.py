
import math

from drawOrbit2d import *

EARTH_SPHERE = ROOT.TGeoSphere(0, 1)
EARTH_SPHERE.Draw()


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
    if len(args) != 1:
        parser.print_help()
        parser.error('Please provide a (single) input M7 file.')
    if not opts.i:
        ROOT.gROOT.SetBatch(True)
    viewer = pOrbitViewer(args[0], opts.s)
    viewer.run(opts.t, opts.p, opts.d)

    orbit = ROOT.TPolyLine3D()
    lon = ROOT.Double()
    lat = ROOT.Double()
    for i in range(viewer.Orbit.GetN()):
        viewer.Orbit.GetPoint(i, lon, lat)
        point = ROOT.TVector3(1, 0, 0)
        point.SetMag(1.098)
        point.SetPhi((180 + lon)*math.pi/180.)
        point.SetTheta((90 - lat)*math.pi/180.)
        orbit.SetNextPoint(point.X(), point.Y(), point.Z())
    orbit.SetLineColor(ROOT.kRed)
    orbit.SetLineWidth(2)
    orbit.Draw()
    ROOT.gPad.Update()

    saa = ROOT.TPolyLine3D()
    vertexList = viewer.M7Parser.SAAPolygon.VertexList
    vertexList.append(vertexList[0])
    for vertex in vertexList:
        point = ROOT.TVector3(1, 0, 0)
        point.SetMag(1.098)
        point.SetPhi((180 + vertex.Lon)*math.pi/180.)
        point.SetTheta((90 - vertex.Lat)*math.pi/180.)
        saa.SetNextPoint(point.X(), point.Y(), point.Z())
    saa.SetLineColor(ROOT.kBlue)
    saa.SetLineWidth(2)
    saa.Draw()
    ROOT.gPad.Update()

    #if opts.o is not None:
    #    viewer.saveImage(opts.o)

