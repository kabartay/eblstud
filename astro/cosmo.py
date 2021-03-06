import math
from eblstud.misc.constants import *
import numpy as np
import scipy.integrate
from scipy.integrate import simps
cosmo = [h, OmegaM, OmegaL]

def nphotCMB(eps):
    """
    return differential number density of CMB in 1/eV/cm^3, eps is in eV
    See Unsoeld & Baschek p. 107
    """
    if np.isscalar(eps):
	scalar = True
	eps = np.array([eps])
    else: 
	scalar = False


    kx = eps/8.617e-5/T_CMB
    result = 1.32e13 * eps **2.

    den = np.ones(eps.shape[0]) * 1e-40
    den[kx < 1e-10] = kx[kx < 1e-10] + kx[kx < 1e-10] **2. / 2.
    den[(kx >= 1e-10) & (kx < 100.)] = np.exp(kx[(kx >= 1e-10) & (kx < 100.)]) - 1.
    result /= den

    if scalar:
	return result[0]
    else:
	return result

from numpy import ma
def nphotCMBarray(eps):
    """
    return differential number density of CMB in 1/eV/cm^3, eps is in eV
    See Unsoeld & Baschek p. 107
    """
    kx = eps/8.617e-5/T_CMB
    result = 1.32e13 * eps **2.
    kx = kx * (kx <= 100.) + np.ones(kx.shape) * 1e-40 * (kx > 100.)
    return result / (np.exp(kx) - 1.)

def PropTime2Redshift(h = h, OmegaM = OmegaM, OmegaL = OmegaL):
    """
    returns the Jacobian dt_prop / dz in Gyr for a flat universe
    """
    return lambda z: 1./ ( h / 9.777752 ) / ( (1. + z) * math.sqrt((1.+ z)**3. * OmegaM
    									+ OmegaL) )
def LumiDistanceSimps(z,cosmo=[h, OmegaM, OmegaL],steps = 30):
    """
    Return luminosity distance for redshift z and cosmological parameters [h, OmegaM, OmegaL]
    from simps integration

    Paramters
    ---------
    z:	n-dim array, redshift values
    cosmo:	list with parameter values for h, Omega_M and Omeaga_L
    steps:	int, number of integration steps

    Returns
    -------
    D:	n-dim array luminosity distance for each redshift in cm

    Notes
    -----
    See Dermer & Menon (2009) Eq. 4.37 p. 44
    """
    if np.isscalar(z): 
	z = np.array([z])
    z_array = np.zeros((z.shape[0],steps))
    for i,z0 in enumerate(z):
	z_array[i] = np.linspace(0.,z0,steps)

    kernel = 1./ ( np.sqrt((1.+ z_array)**3. * OmegaM + OmegaL) )

    return 1e9 * yr2sec * CGS_c / ( h / 9.777752 ) * (1. + z) * simps(kernel,z_array,axis = 1)

def arcsec2Mpc(z,cosmo=cosmo,steps = 30):
    """
    Compute conversion factor for a distance given arcsec to Mpc at redshift z 
    from simps integration

    Paramters
    ---------
    z:		n-dim array, redshift values
    cosmo:	list with parameter values for h, Omega_M and Omeaga_L
    steps:	int, number of integration steps

    Returns
    -------
    x:	n-dim array with conversion factor arcsec2Mpc

    Notes
    -----
    see http://en.wikipedia.org/wiki/Distance_measures_%28cosmology%29
    """
    if np.isscalar(z): 
	z = np.array([z])
    da = LumiDistanceSimps(z,cosmo,steps) / Mpc2cm / (1. + z) ** 2.	# ang dist in Mpc
    return da * np.pi / 180. / 3600.			# return conversion factor arcsec2Mpc assuming tan(x) ~ x

def LumiDistanceKern(h = h, OmegaM = OmegaM, OmegaL = OmegaL):
    """
    returns Kernel for Luminosity distance Integrateion
    """
    return lambda z: 1./ ( math.sqrt((1.+ z)**3. * OmegaM + OmegaL) )


def LumiDistance(z, cosmo=[h, OmegaM, OmegaL]):
    """
    Returns Luminosity Distance, calculated full integral, in cm
    See Dermer (2009) Eq. 4.37 p. 44
    """
    kernel = LumiDistanceKern(*cosmo)
   # resutlt of integration in Gyr
    result = scipy.integrate.quad(kernel, 0. , z)[0]
   # convert to cm by multiplying with c
    return result * 1e9 * yr2sec * CGS_c / ( h / 9.777752 ) * (1. + z)

def LumiDistApprox(z):
    """
    Returns Approximation for Luminosity Distance in cm
    accuracy is better than 2% for z < 0.25
    See Dermer (2009) p. 45
    """
    return 4160. * z * (1. + 0.8*z) * Mpc2cm

def LumiDist2z(d_L_Mpc):
    """
    returns redshift for distance in Mpc. Based on Approximation, valid for redshifts < 0.25
    within 2%
    """
    return np.sqrt(3e-4*d_L_Mpc + 1.5625) - 1.25
