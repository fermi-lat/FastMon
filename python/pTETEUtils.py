
from math import pi, sin, cos
import numpy

D2R = pi/180.


# Ref "The Astronomical Almanac", QB8.U5, 2003, p. B18,B20.
# TEME to TETE rotation from Montenbruck adn Gill (TL1080.M66)
# And of course: Eric Siskind, private communications :-)


def getJ2000toTETERotationMatrix(JD):
    # Initialize the matrices.
    # Consider doing this outside for optimization, though dealing with
    # global variables passed around in the code sometimes has interesting
    # side effects.
    N = numpy.zeros((3, 3), 'd')
    P = numpy.zeros((3, 3), 'd')
    C_TETE_J2000 = numpy.zeros((3, 3), 'd')
    
    # TETE to MEME (Nutation)
    d = JD - 2452639.5
    arg1 = (67.1 - 0.053*d)*D2R
    arg2 = (198.5 + 1.971*d)*D2R
    dpsi = (-0.0048*sin(arg1)-0.0004*sin(arg2))*D2R
    deps = (0.0026*cos(arg1)+0.0002*cos(arg2))*D2R
    eps = 23.44*D2R
    
    N[0][0] = 1.0
    N[1][1] = 1.0
    N[2][2] = 1.0
    N[2][1] = deps
    N[2][0] = dpsi*sin(eps)
    N[1][0] = dpsi*cos(eps)
    N[1][2] = -N[2][1]
    N[0][2] = -N[2][0]
    N[0][1] = -N[1][0]
    
    # MEME to J2000 (Precession)
    T = (JD - 2451545.0)/36525.0
    z =     D2R*((0.6406161+(3.041E-4+5.10E-6*T)*T)*T)
    theta = D2R*((0.5567530-(1.185E-4+1.16E-5*T)*T)*T)
    zeta =  D2R*((0.6406161+(8.390E-5+5.00E-6*T)*T)*T)
    
    c1=cos(-zeta)
    s1=sin(-zeta)
    c2=cos(theta)
    s2=sin(theta)
    c3=cos(-z)
    s3=sin(-z)
    P[0][0] =  c1*c2*c3-s3*s1
    P[1][0] = -c1*c2*s3-c3*s1
    P[2][0] =  c1*s2
    P[0][1] =  s1*c2*c3+s3*c1
    P[1][1] = -s1*c2*s3+c3*c1
    P[2][1] =  s1*s2
    P[0][2] = -s2*c3
    P[1][2] =  s2*s3
    P[2][2] =  c2
    
    # TETE to J2000 (Precession, then Nutation)
    C_TETE_J2000[0][0] = N[0][0]*P[0][0]+N[0][1]*P[1][0]+N[0][2]*P[2][0]
    C_TETE_J2000[0][1] = N[0][0]*P[0][1]+N[0][1]*P[1][1]+N[0][2]*P[2][1]
    C_TETE_J2000[0][2] = N[0][0]*P[0][2]+N[0][1]*P[1][2]+N[0][2]*P[2][2]
    C_TETE_J2000[1][0] = N[1][0]*P[0][0]+N[1][1]*P[1][0]+N[1][2]*P[2][0]
    C_TETE_J2000[1][1] = N[1][0]*P[0][1]+N[1][1]*P[1][1]+N[1][2]*P[2][1]
    C_TETE_J2000[1][2] = N[1][0]*P[0][2]+N[1][1]*P[1][2]+N[1][2]*P[2][2]
    C_TETE_J2000[2][0] = N[2][0]*P[0][0]+N[2][1]*P[1][0]+N[2][2]*P[2][0]
    C_TETE_J2000[2][1] = N[2][0]*P[0][1]+N[2][1]*P[1][1]+N[2][2]*P[2][1]
    C_TETE_J2000[2][2] = N[2][0]*P[0][2]+N[2][1]*P[1][2]+N[2][2]*P[2][2]

    # We're interested in the tranformation matrix from J2000 to TETE,
    # so return the transpose.
    return C_TETE_J2000.transpose()


if __name__ == '__main__':

    # Dummy test program.
    # The Julian date for CE  2009 July 10 00:00:00.0 UT is
    # JD 2455022.50000

    print getJ2000toTETERotationMatrix(2455022.50000)

    # And the answer is:
    # [[  9.99997129e-01   2.19880291e-03   9.55416778e-04]
    # [ -2.19882177e-03   9.99997585e-01   1.93416142e-05]
    # [ -9.55373363e-04  -2.14402423e-05   9.99999544e-01]]

