import glob
import astropy.io.fits as fits
import os
import time
import numpy as n
import sys

# specific functions
from scipy.stats import norm
from scipy.integrate import quad
from scipy.interpolate import interp1d
from scipy.interpolate import interp2d
from scipy.interpolate import RectBivariateSpline
import random

summ = fits.open(os.path.join(os.environ["MD10"], 'output_MD_1.0Gpc.fits'))[1].data	
volume = (1000/0.6777)**3.

zmin, zmax, zmean, dN_dV_agn_data = n.loadtxt(os.path.join(os.environ['GIT_NBODY_NPT'], "data/NZ/nz_6.txt"), unpack=True)

obscuration_z_grid, obscuration_nh_grid, obscuration_fraction_obs_erosita = n.loadtxt( os.path.join( os.environ['GIT_NBODY_NPT'], "data", "AGN", "fraction_observed_by_erosita_due_2_obscuration.txt"), unpack=True)
nh_vals = 10**n.arange(-2,4,0.05)
z_vals = 10**n.arange(-3,0.68,0.025)
obscuration_interpolation_grid = n.array([ 
  interp1d(
    n.hstack((obscuration_nh_grid[ (obscuration_z_grid==zz) ], 26.)), 
    n.hstack((obscuration_fraction_obs_erosita[( obscuration_z_grid==zz) ], obscuration_fraction_obs_erosita[( obscuration_z_grid==zz) ][-1]))
	      ) 
  for zz in z_vals])

dN_dV_agn = interp1d(n.hstack((-1., zmin[0], zmean, zmax[-1], 3.)), n.hstack((0., 0., dN_dV_agn_data, 0., 0.)) )

# number of tracer per snapshot (complete volume)
z_snap = summ['redshift']

N_agn_per_snap = (volume * dN_dV_agn(z_snap) ).astype('int')

for ii in n.arange(len(summ)):#[::-1]:
  #ii=4
  el=summ[ii]
  print(ii,el,N_agn_per_snap[ii])
  N_agn = N_agn_per_snap[ii]

  fileList_snap_MS = n.array(glob.glob(os.path.join(os.environ["MD10"], 'work_agn', 'out_'+el['snap_name']+'_SAM_Nb_?_Ms.fits')))
  fileList_snap_MS.sort()
  fileList_snap_X = n.array(glob.glob(os.path.join(os.environ["MD10"], 'work_agn', 'out_'+el['snap_name']+'_SAM_Nb_?_Xray.fits')))
  fileList_snap_X.sort()

  index = n.searchsorted(z_vals,el['redshift'])

  if N_agn > 10 :
	# LRG: select on Ms
    MS = n.array([fits.open(file)[1].data['stellar_mass_Mo13_mvir'] for file in fileList_snap_MS])
    SAR = n.array([fits.open(file)[1].data['lambda_sar_Bo16'] for file in fileList_snap_X])
    act = n.array([fits.open(file)[1].data['activity'] for file in fileList_snap_X])
    lognh = n.array([fits.open(file)[1].data['log_NH_Buchner2017'] for file in fileList_snap_X])
    ok = (MS>0)&(act)

    percent_observed = n.array([ obscuration_interpolation_grid[index]( nh) for nh in lognh])
    LX_unabsorbed = MS + SAR
    LX = n.log10(10**LX_unabsorbed * percent_observed)

    all_LX = n.hstack((LX[ok]))
    all_LX_sort_id = n.argsort(all_LX)
    min_LX = all_LX[all_LX_sort_id[-N_agn-1]]

    id_superset = n.where(LX>min_LX)
    active = act[id_superset]
    id_superset_0 = id_superset[0][active]
    id_superset_1 = id_superset[1][active]

    for num in list(set(id_superset_0)):
      file_out = os.path.join(os.environ["MD10"], 'work_agn', 'out_'+el['snap_name']+'_SAM_Nb_'+str(num)+'_4MOST_S6_AGN.fits')
      agns = id_superset_1[ (id_superset_0==num) ]
      xray_lum = LX[num][agns]

      print( file_out, agns, len(agns))
      hdu_cols  = fits.ColDefs([
      fits.Column(name='line_number',format='K', array= agns ),
      fits.Column(name='LX_05_2_keV',format='D', array= xray_lum )])

      tb_hdu = fits.BinTableHDU.from_columns( hdu_cols )
      prihdr = fits.Header()
      prihdr['HIERARCH nameSnapshot'] = el['snap_name']
      prihdr['batchN'] = num
      prihdr['tracer'] = 'AGN'
      prihdr['author'] = 'JC'
      prihdu = fits.PrimaryHDU(header=prihdr)
      #writes the file
      thdulist = fits.HDUList([prihdu, tb_hdu])
      if os.path.isfile(file_out):
	    os.system("rm "+file_out)
      thdulist.writeto(file_out)




