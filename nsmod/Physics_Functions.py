#!/usr/bin/python

import numpy as np
import pylab as py
from math import pi
from numpy import cos, sin, tan
import scipy as sc

from scipy.integrate import cumtrapz



def Cartesian_2_Spherical(x, y, z, Angle_Type="Degrees", fix_varphi=False):
    """ Transform x,y,z to radial,polar and azimuthal vectors"""

    N = len(x)

    radial = [(x[i] * x[i] + y[i] * y[i] + z[i] * z[i]) ** 0.5
                for i in range(N)]
    polar = [py.arccos(z[i] / radial[i]) for i in range(N)]
    azimuth = [py.arctan(y[i] / x[i]) for i in range(N)]

    if "Degrees" in Angle_Type:

        polar_degrees = [p * 180 / pi for p in polar]
        azimuth_degrees = [a * 180 / pi for a in azimuth]

        if fix_varphi:
            azimuth_degrees = Fix_Varphi(azimuth_degrees, Angle_Type="Degrees")

        return (radial, polar_degrees, azimuth_degrees)

    elif Angle_Type in ["Radians", "Radian", "Rads"]:

        if fix_varphi:
            azimuth = Fix_Varphi(azimuth, Angle_Type="Radians")

        return (radial, polar, azimuth)


def Cartesian_2_EBF(x, y, z, beta):
    """Functions to rotate x,z system by angle beta about the y axis"""

    N = len(x)
    Cb = py.cos(beta)
    Sb = py.sin(beta)
    x_prime = [x[i] * Cb - z[i] * Sb for i in xrange(N)]
    z_prime = [z[i] * Cb + x[i] * Sb for i in xrange(N)]
    y_prime = y
    return (x_prime, y_prime, z_prime)

def epsA(Bs, R=1e6, I0=1e45, c=1e10):
    ''' Return epsA from standard equations '''
    return np.power(Bs, 2) * np.power(R, 5) / (4 * I0 * np.power(c, 2))

def Rotational_Kinetic_Energy(Ix, Iy, Iz, omega_x, omega_y, omega_z):
    en_2 = (Ix * pow(omega_x, 2) + Iy * pow(omega_y, 2) + Iz * pow(omega_z, 2))
    return 0.5 * en_2


def Fix_Varphi(varphi, epsilon=170.0, Angle_Type="Degrees"):
    """

    Takes a list of varrphi values and looks for jumps greater than epsilon,
    assuming these reflect a full rotation (2pi-0) it adds a correction
    factor to the subsequent data

    """

    if Angle_Type == "Degrees":
        varphi_fix = []
        fix = 0.0
        varphi_fix.append(varphi[0])
        for i in range(1, len(varphi)):
            if abs(varphi[i] - varphi[i - 1]) > epsilon:
                fix += -1 * py.sign(varphi[i] - varphi[i - 1]) * 180.0
            varphi_fix.append(varphi[i] + fix)
        varphi = varphi_fix
        return varphi

    elif Angle_Type in ["Radians", "Radian", "Rads"]:
        if epsilon == 170.0:
            epsilon = 1.0

        varphi_fix = []
        fix = 0.0
        varphi_fix.append(varphi[0])
        for i in range(1, len(varphi)):
            if abs(varphi[i] - varphi[i - 1]) > epsilon:
                fix += -1 * py.sign(varphi[i] - varphi[i - 1]) * pi
            varphi_fix.append(varphi[i] + fix)
        varphi = varphi_fix
        return varphi


def Beta_Function(epsI, epsA, chi):
    """ Returns beta the rotation of the effective MOI tensor """
    if chi > 2 * pi:
        print "Assuming chi has been given in degrees rather than radians"
        chi = chi * pi / 180

    a = epsA * epsA + epsI * epsI - 2 * epsA * epsI * py.cos(2 * chi)
    beta = (py.arctan((epsI - epsA * py.cos(2 * chi) - py.sqrt(a)) /
                        (2 * epsA * py.sin(chi) * py.cos(chi))))
    return beta


def Inertial_Frame(time, omega, epsI3):
    """ Return the Euler angles at the timesteps of omega """

    def equations(omega, theta, phi, psi):
        theta_dot = omega[0] * py.cos(psi) - omega[1] * py.sin(psi)
        phi_dot = ((omega[0] * py.sin(psi) + omega[1] * py.cos(psi))
                                                      / py.sin(theta))
        psi_dot = omega[2] - phi_dot * py.cos(theta)
        return theta_dot, phi_dot, psi_dot

    # Initial conditions
    #theta = [py.arccos((pow(epsI1, 0.5) * omega[0, 0] * (1 + epsI1)
                      #+ pow(epsI3, 0.5) * omega[2, 0] * (1 + epsI3))
                        #/ (pow(epsI1 + epsI3, 0.5)
                        #* py.norm([omega[0, 0] * (1 + epsI1),
                                   #omega[1, 0],
                                   #omega[2, 0] * (1 + epsI3)])))]
    theta = [np.arccos(omega[2, 0] * (1 + epsI3) /
            (py.norm([omega[0, 0], omega[1, 0], omega[2, 0] * (1. + epsI3)])))]
    phi = [0.0]
    psi = [np.pi / 2]  # Unfinished

    for i in xrange(len(time)-1):
        dt = time[i + 1] - time[i]
        theta_dot, phi_dot, psi_dot = equations(omega[:, i], theta[i],
                                                phi[i], psi[i])
        theta.append(theta[i] + dt * theta_dot)
        phi.append(phi[i] + dt * phi_dot)
        psi.append(psi[i] + dt * psi_dot)

    return theta, phi, psi

# Equations for the Euler angles 

def equations(omega, theta, phi, psi):
    theta_dot = omega[0] * cos(psi) - omega[1] * sin(psi)
    phi_dot = ((omega[0] * sin(psi) + omega[1] * cos(psi))
                                                  / sin(theta))
    psi_dot = omega[2] - phi_dot * cos(theta)
    return theta_dot, phi_dot, psi_dot

def Phi_dot(omega, theta, phi, psi, chi):
    """ """
    theta_dot, phi_dot, psi_dot = equations(omega, theta, phi, psi)
    return phi_dot +  sin(chi) * ( 
            (psi_dot * (cos(theta) * sin(chi) - sin(psi) * sin(theta) * cos(chi)) +
             theta_dot * cos(psi) * (sin(psi) * sin(chi) * sin(theta) - cos(chi) * cos(theta))) /
	    (pow(sin(theta) * cos(chi) - cos(theta) * sin(psi) * sin(chi), 2) + pow(cos(psi) * sin(chi), 2)))
    
def Phi(theta, phi, psi, chi):
    """ See equation (42) of Jones 2001 """
    return phi - .5 * np.pi + np.arctan(
                (cos(psi) * tan(chi)) / 
                (sin(theta) - cos(theta) * sin(psi) * tan(chi)))

def Theta(theta, psi, chi):  
    """ See equation (52) of Jones 2001 """
    return np.arccos(sin(theta) * sin(psi) * sin(chi) + cos(theta) * cos(chi))  

def timing_residual(time, w1, w2, w3, theta, phi, psi, chi, order=2, full=False):
    """ 

    Calculate the timing residuals in the inertial frame using Phi_dot the 
    instantaneous electromagnetic frequency. To understand the process it is 
    best to follow the source code.

    Parameters
    ----------
    file_name : str
               hdf5 file to use as source data.
    order : int
            Order of polynomial to fit to the exact phase, options are 2 or 3
    full : bool
           If true return the coefficients of the fit as w;;

    Returns
    -------
    r : tuple
        if full = True : time, T_res, coeffs
        else time, T_res

    """

    if order not in [2, 3]:
        print "ERROR: order must be either 2 or 3 other values are not used"
        return

    # Calculate Phi_dot the instantaneous electromagnetic frequency
    Phi_dot_list = Phi_dot(np.array([w1, w2, w3]), theta, phi, psi, chi)

    # Numerically intergrate Phi_dot to get a phase (initial conditon is Phi=0
    #Phi_list = cumtrapz(y=Phi_dot_list, x=time, initial=0)

    Phi_list = Phi(theta, phi, psi, chi)
    
    # Fit polynomial to Phi or order order
    coefs = np.polyfit(time, Phi_list, order)
    # poly1d returns the polynomial we then evaluate this at time giving the fitted phi
    Phi_fit = np.poly1d(coefs)(time)

    # Subtract the two to get a residual
    T_res = Phi_list - Phi_fit

    if full:
        return T_res, coeffs
    else:
        return T_res

def nu_dot(time, w1, w2, w3, theta, phi, psi, chi, tauP, divisor=5):
    """
    
    Calculate the spin down rate using the method precesribed by by Lyne 2010 
    
    Parameters:
    -----------
    data: The usual (expand)
    divisor: The fraction of the precession period to use as a segmentation time for calculating 
             the nu_dot values. 

    Returns:
    out: Array of the values of the time and nu_dot

    """



    # Calculate Phi_dot the instantaneous electromagnetic frequency
    Phi_dot_list = Phi_dot(np.array([w1, w2, w3]), theta, phi, psi, chi)

    # Numerically intergrate Phi_dot to get a phase (initial conditon is Phi=0
    Phi_list = cumtrapz(y=Phi_dot_list, x=time, initial=0)


    # Convert T into an index range of time, note all time intervals should be uniform
    T = tauP / divisor
    dt = time[1] - time[0]
    T_index_range = int(T / dt)

    dT = int(0.25 * T_index_range)

    nu_dot_list = []
    time_list = []
    i=0
    while i < len(time)-T_index_range:
        coefs = np.polyfit(time[i:i + T_index_range], Phi_list[i:i + T_index_range], 2)
        nu_dot_list.append(coefs[0])
        time_list.append(0.5*(time[i] + time[i+T_index_range])) 
    
        i += dT

    return np.array([time_list, nu_dot_list])

# Below is to be replaced by the Euler method

#def Inertial_Frame(omega, chi, epsI1, epsI3, epsA,
                   #Io=1e45, JI_norm=np.array([.0, .0, 1.0])):
    #"""
    #Transformation from rotating coordinate system to inertial frame

    #:param omega: Spin vector in the rotating body frame `omega=[w1, w2, w3]`
    #:type omega:list
    #:param chi: Inclination angle of the magnetic dipole to the z axis
    #:type chi:float in degrees
    #:param epsI1: Deformation along the x axis of the body frame
    #:type epsI1: float
    #:param epsI3: Deformation along the z axis of the body frame
    #:type epsI3: float
    #:param epsA: Magnetic deformation
    #:type epsA: float
    #:param J_In: Fixed angular momentum in the inertial frame
    #:type J_In:numpy.ndarray
    #:default J_In: np.array([.0, .0, 1]


    #"""

    #omega = np.array(omega)
    #N = max(omega.shape)
    #JR = Io * np.array([omega[0] * (1 + epsI1),
                        #omega[1],
                        #omega[2] * (1 + epsI3)])

    #JR_norm = JR / py.norm(JR)

    #def Axis_Angle_Extraction(x, y):
        #""" Calculate rotation angle and axis of rotation for x onto y """
        #phi = np.arccos(np.dot(x, y) / (py.norm(x) * py.norm(y)))
        #n = np.cross(x, y)
        #n_hat = n / py.norm(n)
        #return (phi, n_hat)

    #def Axis_Angle_Rotation(x, phi, n_hat):
        #""" Rotate vector x about axis n by phi"""

        #r_1 = x * np.cos(phi)
        #r_2 = np.cross(n_hat, x) * np.sin(phi)
        #r_3 = n_hat * np.dot(n_hat, x) * (1 - np.cos(phi))
        #return r_1 + r_2 + r_3

    #omega_I = np.empty((3, N))
    #m_I = np.empty((3, N))

    #m = np.array([np.sin(np.radians(chi)), 0.0, np.cos(np.radians(chi))])

    #for i in xrange(N):
        #(phi, n_hat) = Axis_Angle_Extraction(JR_norm[:, i], JI_norm)
        #omega_I[:, i] = Axis_Angle_Rotation(omega[:, i], phi, n_hat)
        #m_I[:, i] = Axis_Angle_Rotation(m, phi, n_hat)

    #return omega_I, m_I


#def T_residual(time, w1, w2, w3):
    #"""

    #Calculate the timing residuals from cartesian components of omega

    #"""

    #def fit(t, phi0, nu0, nu_dot0, nu_ddot0, t0):
        #a = phi0
        #b = nu0 * (t - t0)
        #c = 0.5 * nu_dot0 * pow(t - t0, 2)
        #d = pow(6, -1) * nu_ddot0 * pow(t - t0, 3)
        #return a + b + c + d

    #N = len(time)

    ## Calculate the frequency from |omega|
    #nu = [2 * pi * py.norm([w1[i], w2[i], w3[i]]) for i in xrange(N)]

    ## Integrate
    #phi_exact = cumtrapz(nu, time, initial=0)

    ## Fit to taylor series
    #popt, pcov = curve_fit(fit, time, phi_exact)

    #phi_fit = [fit(t, *popt) for t in time]

    #T_res = [phi_exact[i] - varphi_fit[i] for i in xrange(len(varphi_exact))]

    #return T_res

