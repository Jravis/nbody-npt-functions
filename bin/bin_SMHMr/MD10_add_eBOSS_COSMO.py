from astropy.cosmology import FlatLambdaCDM
import astropy.units as u
cosmoMD = FlatLambdaCDM(H0=67.77*u.km/u.s/u.Mpc, Om0=0.307115, Ob0=0.048206)

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
import random

summ = fits.open(os.path.join(os.environ["MD10"], 'output_MD_1.0Gpc.fits'))[1].data	
volume = (1000/0.6777)**3.

# the eBOSS ELG z distribution 
zmin ,zmax ,SDSS_uri_gri, SDSS_Fisher, DECam190, DECam240 = n.loadtxt(os.path.join(os.environ['GIT_NBODY_NPT'], "data/NZ/eBOSS-ELG.txt"), unpack=True)
dV_per_pixel = (cosmoMD.comoving_volume(zmax[2:]) - cosmoMD.comoving_volume(zmin[2:]))*n.pi/129600.
dN_dV_elg_data = DECam240[2:]/dV_per_pixel
dN_dV_elg = interp1d(n.hstack((-1., zmin[2], (zmax[2:]+zmin[2:])*0.5, zmax[-1], 3.)), n.hstack((0., 0., dN_dV_elg_data, 0., 0.)) )

# the QSO as observed in eBOSS
zmin ,zmax ,CMASS, LRG1, LRG2, QSO1, QSO2, LyaQSO, PTFQSO = n.loadtxt(os.path.join(os.environ['GIT_NBODY_NPT'], "data/NZ/eBOSS-LRG-QSO.txt"), unpack=True)
dV_per_pixel = (cosmoMD.comoving_volume(zmax[3:]) - cosmoMD.comoving_volume(zmin[3:]))*n.pi/129600.
all_QSO = QSO1 + QSO2 + LyaQSO + PTFQSO
dN_dV_qso_data =  all_QSO[3:] /dV_per_pixel
dN_dV_qso = interp1d(n.hstack((-1., zmin[3], (zmax[3:]+zmin[3:])*0.5, zmax[-1], 5.)), n.hstack((0., 0., dN_dV_qso_data, 0., 0.)) )

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as p

from hmf import MassFunction
def get_hf(sigma_val=0.8228, boxRedshift=0., delta_wrt='mean'):
    """
    Halo mass function model for the MultiDark simulation.
    """
    #hf0 = MassFunction(cosmo_model=cosmo, sigma_8=sigma_val, z=boxRedshift)
    omega = lambda zz: cosmoMD.Om0*(1+zz)**3. / cosmoMD.efunc(zz)**2
    DeltaVir_bn98 = lambda zz : (18.*n.pi**2. + 82.*(omega(zz)-1)- 39.*(omega(zz)-1)**2.)/omega(zz)
    print "DeltaVir", DeltaVir_bn98(boxRedshift), " at z",boxRedshift
    hf1 = MassFunction(cosmo_model=cosmoMD, sigma_8=sigma_val, z=boxRedshift, delta_h=DeltaVir_bn98(boxRedshift), delta_wrt=delta_wrt, Mmin=7, Mmax=16.5)
    return hf1

hmfs = n.array([get_hf(boxRedshift=z) for z in dN_dV_qso.x[1:]])
z_pk = dN_dV_qso.x[1:]
pk_m1_k02=n.array([1./hmf.power[n.searchsorted(hmf.k,0.2)] for hmf in hmfs ])
pk_m1_k006=n.array([1./hmf.power[n.searchsorted(hmf.k,0.06)] for hmf in hmfs ])


p.figure(1, (5,5))
p.axes([0.17,0.17,0.75,0.75])
p.plot(dN_dV_qso.x, dN_dV_qso.y, label='qso')
p.plot(dN_dV_elg.x, dN_dV_elg.y, label='elg')
p.plot(z_pk, pk_m1_k02, label=r'$1/P(0.2)$', ls='dashed')
p.plot(z_pk, pk_m1_k006, label=r'$1/P(0.06)$', ls='dashed')
p.plot(z_pk, 0.25*pk_m1_k02, label=r'$1/2^2 P(0.2)$', ls='dotted')
p.plot(z_pk, 0.25*pk_m1_k006, label=r'$1/2^2 P(0.06)$', ls='dotted')
p.xlabel('redshift')
p.ylabel(r'$N\, h^3\, Mpc^{-3}$')
p.xlim((0.01,4))
p.ylim((8*10**(-7), 2*10**(-3)))
p.xscale('log')
p.yscale('log')
p.legend(loc=0, frameon=False)
p.savefig(os.path.join(os.environ['HOME'], 'wwwDir/eRoMok/nz_plots', 'nz-eboss-cosmo.png'))
p.clf()




p.figure(1, (5,5))
p.axes([0.17,0.17,0.75,0.75])
p.plot(dN_dV_qso.x, dN_dV_qso.y, label='qso')
p.plot(dN_dV_elg.x, dN_dV_elg.y, label='elg')
p.plot(z_pk, pk_m1_k02, label=r'$1/P(0.2)$', ls='dashed')
p.plot(z_pk, pk_m1_k006, label=r'$1/P(0.06)$', ls='dashed')
p.plot(z_pk, 0.25*pk_m1_k02, label=r'$1/2^2 P(0.2)$', ls='dotted')
p.plot(z_pk, 0.25*pk_m1_k006, label=r'$1/2^2 P(0.06)$', ls='dotted')
p.xlabel('redshift')
p.ylabel(r'$N\, h^3\, Mpc^{-3}$')
p.xlim((0.01,4))
p.ylim((8*10**(-7), 2*10**(-3)))
#p.xscale('log')
p.yscale('log')
p.legend(loc=0, frameon=False)
p.savefig(os.path.join(os.environ['HOME'], 'wwwDir/eRoMok/nz_plots', 'nz-eboss-cosmo-xLin.png'))
p.clf()

# number of tracer per snapshot (complete volume)
z_snap = summ['redshift']

N_elg_per_snap = (volume * dN_dV_elg(z_snap) ).astype('int')
N_qso_per_snap = (volume * dN_dV_qso(z_snap) ).astype('int')

# determine dz
#z_middle = (summ['redshift'][1:]+summ['redshift'][:-1])*0.5
#z_mins = n.hstack((summ['redshift'][0], z_middle))
#z_maxs = n.hstack((z_middle, summ['redshift'][-1]))
#dz = z_maxs - z_mins

for ii, el in enumerate(summ):
	N_elg, N_qso = N_elg_per_snap[ii], N_qso_per_snap[ii]

	fileList_snap = n.array(glob.glob(os.path.join(os.environ["MD10"], 'work_agn', 'out_'+el['snap_name']+'_SAM_Nb_?.fits')))
	fileList_snap.sort()
	fileList_snap_MS = n.array(glob.glob(os.path.join(os.environ["MD10"], 'work_agn', 'out_'+el['snap_name']+'_SAM_Nb_?_Ms.fits')))
	fileList_snap_MS.sort()

	if N_elg > 10 or N_qso > 10  :
		MH = n.array([fits.open(file)[1].data['mvir'] for file in fileList_snap])

		if N_elg > 10 :
			# ELG select on Mvir
			#p_elg=[10**(12.2),0.25]
			mh_mean, mh_scatter = 12.2, 0.25
			mh_bins = n.arange(mh_mean -2*mh_scatter, mh_mean +2*mh_scatter+0.1, 0.1)
			mh_bins_pos = 0.5*(mh_bins[1:]+mh_bins[:-1])
			proba = lambda x : norm.pdf(x, loc=mh_mean,scale=mh_scatter)
			proba_norm = proba(mh_bins_pos).sum()
			N_2_select_per_bin = (N_elg*proba(mh_bins_pos)/proba_norm).astype('int')

			id_0 = []
			id_1 = []
			for id_bin in range(len(mh_bins)-1):
				id_superset = n.where( (MH > mh_bins[id_bin]) &( MH < mh_bins[id_bin+1]) )
				N_avail = id_superset[0].shape[0]
				rds = n.random.rand(len(id_superset[0]))
				bin_selection = (rds < N_2_select_per_bin[id_bin]*1./N_avail)
				id_0.append(id_superset[0][bin_selection])
				id_1.append(id_superset[1][bin_selection])

			id_0 = n.hstack((id_0))
			id_1 = n.hstack((id_1))

			for num in list(set(id_0)):
				file_out = os.path.join(os.environ["MD10"], 'work_agn', 'out_'+el['snap_name']+'_SAM_Nb_'+str(num)+'_EBOSS_ELG.fits')
				elgs = id_1[ (id_0==num) ]
				print( file_out, elgs)
				hdu_cols  = fits.ColDefs([
				fits.Column(name='line_number',format='K', array= elgs )])
				tb_hdu = fits.BinTableHDU.from_columns( hdu_cols )
				prihdr = fits.Header()
				prihdr['HIERARCH nameSnapshot'] = el['snap_name']
				prihdr['batchN'] = num
				prihdr['tracer'] = 'ELG'
				prihdr['author'] = 'JC'
				prihdu = fits.PrimaryHDU(header=prihdr)
				#writes the file
				thdulist = fits.HDUList([prihdu, tb_hdu])
				if os.path.isfile(file_out):
					os.system("rm "+file_out)
				thdulist.writeto(file_out)

		if N_qso > 10 :
			# QSO select on Mvir
			#p_qso=[10**(12.7),0.25]
			mh_mean, mh_scatter = 12.7, 0.25
			mh_bins = n.arange(mh_mean -2*mh_scatter, mh_mean +2*mh_scatter+0.1, 0.1)
			mh_bins_pos = 0.5*(mh_bins[1:]+mh_bins[:-1])
			proba = lambda x : norm.pdf(x, loc=mh_mean,scale=mh_scatter)
			proba_norm = proba(mh_bins_pos).sum()
			N_2_select_per_bin = (N_qso*proba(mh_bins_pos)/proba_norm).astype('int')

			id_0 = []
			id_1 = []
			for id_bin in range(len(mh_bins)-1):
				id_superset = n.where( (MH > mh_bins[id_bin]) &( MH < mh_bins[id_bin+1]) )
				N_avail = id_superset[0].shape[0]
				rds = n.random.rand(len(id_superset[0]))
				bin_selection = (rds < N_2_select_per_bin[id_bin]*1./N_avail)
				id_0.append(id_superset[0][bin_selection])
				id_1.append(id_superset[1][bin_selection])

			id_0 = n.hstack((id_0))
			id_1 = n.hstack((id_1))

			for num in list(set(id_0)):
				file_out = os.path.join(os.environ["MD10"], 'work_agn', 'out_'+el['snap_name']+'_SAM_Nb_'+str(num)+'_EBOSS_QSO.fits')
				qsos = id_1[ (id_0==num) ]
				print( file_out, qsos)
				hdu_cols  = fits.ColDefs([
				fits.Column(name='line_number',format='K', array= qsos )])
				tb_hdu = fits.BinTableHDU.from_columns( hdu_cols )
				prihdr = fits.Header()
				prihdr['HIERARCH nameSnapshot'] = el['snap_name']
				prihdr['batchN'] = num
				prihdr['tracer'] = 'QSO'
				prihdr['author'] = 'JC'
				prihdu = fits.PrimaryHDU(header=prihdr)
				#writes the file
				thdulist = fits.HDUList([prihdu, tb_hdu])
				if os.path.isfile(file_out):
					os.system("rm "+file_out)
				thdulist.writeto(file_out)


