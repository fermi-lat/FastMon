
from math import pi, sin, cos
import numpy

D2R = pi/180.


# Ref "The Astronomical Almanac", QB8.U5, 2003, p. B18,B20.
# TEME to TETE rotation from Montenbruck adn Gill (TL1080.M66)
# And of course: Eric Siskind, private communications :-)

def getPrecessionMatrix(julianDate):
    P = numpy.matrix([[0., 0., 0.], [0., 0., 0.], [0., 0., 0.]], 'd')
    T = (julianDate - 2451545.0)/36525.0
    z =     D2R*((0.6406161+(3.041E-4+5.10E-6*T)*T)*T)
    theta = D2R*((0.5567530-(1.185E-4+1.16E-5*T)*T)*T)
    zeta =  D2R*((0.6406161+(8.390E-5+5.00E-6*T)*T)*T)
    c1=cos(-zeta)
    s1=sin(-zeta)
    c2=cos(theta)
    s2=sin(theta)
    c3=cos(-z)
    s3=sin(-z)
    P[0, 0] =  c1*c2*c3-s3*s1
    P[1, 0] = -c1*c2*s3-c3*s1
    P[2, 0] =  c1*s2
    P[0, 1] =  s1*c2*c3+s3*c1
    P[1, 1] = -s1*c2*s3+c3*c1
    P[2, 1] =  s1*s2
    P[0, 2] = -s2*c3
    P[1, 2] =  s2*s3
    P[2, 2] =  c2
    return P

def getNutationMatrix(julianDate):
    N = numpy.matrix([[0., 0., 0.], [0., 0., 0.], [0., 0., 0.]], 'd')
    d = julianDate - 2452639.5
    arg1 = (67.1 - 0.053*d)*D2R
    arg2 = (198.5 + 1.971*d)*D2R
    dpsi = (-0.0048*sin(arg1)-0.0004*sin(arg2))*D2R
    deps = (0.0026*cos(arg1)+0.0002*cos(arg2))*D2R
    eps = 23.44*D2R
    N[0, 0] = 1.0
    N[1, 1] = 1.0
    N[2, 2] = 1.0
    N[2, 1] = deps
    N[2, 0] = dpsi*sin(eps)
    N[1, 0] = dpsi*cos(eps)
    N[1, 2] = -N[2, 1]
    N[0, 2] = -N[2, 0]
    N[0, 1] = -N[1, 0]
    return N

def getTETEtoJ2000Matrix(julianDate):
    return getPrecessionMatrix(julianDate)*getNutationMatrix(julianDate)

def getJ2000toTETEMatrix(julianDate):
    return getTETEtoJ2000Matrix(julianDate).transpose()



if __name__ == '__main__':

    # Dummy test program.
    # The Julian date for CE  2009 July 10 00:00:00.0 UT is
    # JD 2455022.50000
    #
    # The Julian date for CE  2008 October 30 00:00:00.0 UT is
    # JD 2454769.50000

    jd = 2454769.50000
    print 'Test program for julian date %f' % jd
    p = getPrecessionMatrix(jd)
    n = getNutationMatrix(jd)
    t2j = getTETEtoJ2000Matrix(jd)
    j2t = getJ2000toTETEMatrix(jd)
    print '* Precession   :\n %s\n' % p
    print '* Nutation     :\n %s\n' % n
    print '* TETE to J2000:\n %s\n' % t2j
    print '* J2000 to TETE:\n %s\n' % j2t

    # Test program for julian date 2454769.500000
    # * Precession   :
    # [[  9.99997683e-01  -1.97418862e-03  -8.57834669e-04]
    #  [  1.97418862e-03   9.99998051e-01  -8.46777550e-07]
    #  [  8.57834669e-04  -8.46751855e-07   9.99999632e-01]]
    #
    # * Nutation     :
    # [[  1.00000000e+00  -4.88599312e-05  -2.11840908e-05]
    #  [  4.88599312e-05   1.00000000e+00  -3.24432726e-05]
    #  [  2.11840908e-05   3.24432726e-05   1.00000000e+00]]
    #
    # * TETE to J2000:
    # [[  9.99997569e-01  -2.02307627e-03  -8.78954662e-04]
    #  [  2.02304844e-03   9.99997955e-01  -3.33318083e-05]
    #  [  8.79018711e-04   3.15545951e-05   9.99999614e-01]]
    #
    # * J2000 to TETE:
    # [[  9.99997569e-01   2.02304844e-03   8.79018711e-04]
    #  [ -2.02307627e-03   9.99997955e-01   3.15545951e-05]
    #  [ -8.78954662e-04  -3.33318083e-05   9.99999614e-01]]
