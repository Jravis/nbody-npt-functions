from MultiDark import *
import sys
import glob
import os
import astropy.io.fits as fits

sf = fits.open(os.path.join(os.environ["MD10"], "hlists_MD_1.0Gpc.fits"))[1].data
snList= n.array(glob.glob(os.path.join(os.environ["MD10"], "hlists", "hlist_*.list")))

box = MultiDarkSimulation(Lbox=1000.0 * u.Mpc, boxDir = "MD_1Gpc",snl =snList   ,zsl = None,zArray = n.arange(0.2,2.4,1e-1),Hbox = 67.77 * u.km / (u.s * u.Mpc))

t0=time.time()


for el in sf:
	rho_crit = cosmoMD.critical_density(el['redshift']).to(u.solMass/u.kpc**3)*cosmoMD.h**2.
	path_2_snap = os.path.join(os.environ["MD10"], "hlists", "hlist_"+ str(el['snap_name']).ljust(7,'0')+".list")
	box.writeEMERGEcatalog_gawk(path_2_snap, rho_crit.value, el['delta_vir'], mmin=100*box.Melement)

print time.time()-t0

