import xspec
import numpy as n
import sys

nh_vals = 10**n.arange(-2,4,0.05)
z_vals = 10**n.arange(-3,0.68,0.025)

nh_val = 1000.# nh_vals[0]
redshift = 2. # z_vals[0]
def get_fraction_obs(nh_val, redshift, kev_min_erosita = 0.5, kev_max_erosita = 2.0):
    print(nh_val, redshift)
    kev_min_erosita_RF = kev_min_erosita*(1+redshift)
    kev_max_erosita_RF = kev_max_erosita*(1+redshift)
    m1 = xspec.Model("atable{torus1006.fits} + zpowerlw")
    m1.torus.nH = nh_val
    m1.torus.Theta_tor = 45.
    m1.torus.Theta_inc = 87.
    m1.torus.z = redshift
    m1.torus.norm = 1.
    m1.zpowerlw.PhoIndex=2.
    m1.zpowerlw.Redshift=redshift
    m1.zpowerlw.norm=0.01
    # observed frame attenuated flux
    xspec.AllModels.calcFlux(str(kev_min_erosita)+" "+str(kev_max_erosita))
    flux_obs = m1.flux[0]
    # rest frame intrinsic flux
    m1.torus.nH = 0.01
    xspec.AllModels.calcFlux(str(kev_min_erosita_RF)+" "+str(kev_max_erosita_RF))
    flux_intrinsic = m1.flux[0]
    fraction_observed = flux_obs / flux_intrinsic
    return fraction_observed

frac = n.array([n.array([get_fraction_obs(nh_val, redshift) for nh_val in nh_vals]) for redshift in z_vals ])

z_all = n.array([n.array([ redshift for nh_val in nh_vals]) for redshift in z_vals ])
nh_all = n.array([n.array([ nh_val for nh_val in nh_vals]) for redshift in z_vals ])

n.savetxt("fraction_observed.txt", n.transpose([n.hstack((z_all)), 22 + n.log10(n.hstack((nh_all))), n.hstack((frac))]), header='z log_nh fraction_observed')

