
"""
.. class:: MultiDark

.. moduleauthor:: Johan Comparat <johan.comparat__at__gmail.com>

The class MultiDark is a wrapper to handle Multidark simulations results / outputs.

"""
import cPickle
import fileinput
import astropy.io.fits as fits
import astropy.cosmology as co
c2 = co.Planck13
import astropy.units as u
import astropy.constants as cc
from scipy.interpolate import interp1d
from os.path import join
import os
import numpy as n
import glob
import scipy.spatial.ckdtree as t
import time

cc.G.to(u.km**2 * u.megaparsec /(u.solMass*u.s**2)).value

class MultiDarkSimulation :
	"""
	Loads the environement proper to the Multidark simulations. This is the fixed framework of the simulation.
			
	:param Lbox: length of the box in Mpc/h 
	:param wdir: Path to the multidark lightcone directory
	:param boxDir: box directory name
	:param snl: list of snapshots available
	:param zsl: list of redshift corresponding to the snapshots   
	:param zArray: redshift array to be considered to interpolate the redshift -- distance conversion
	:param Hbox: Hubble constant at redshift 0 of the box
	:param Melement: Mass of the resolution element in solar masses.   
	:param columnDict: dictionnary to convert column name into the index to find it in the snapshots
	"""

	def __init__(self,Lbox=2500.0, wdir="/lustre/jcomparat/Multidark/", boxDir="MD_2.5Gpc_Rockstar", snl=n.array(glob.glob("/lustre/jcomparat/Multidark/MD_2.5Gpc_Rockstar/snapshots/out_*.list.bz2")), zsl=None, zArray=n.arange(0.2,2.4,1e-1), Melement = 23593750000.0 ):
		self.Lbox = Lbox # box length
		self.wdir = wdir # working directory
		self.boxDir = boxDir # directory of the box 
		self.snl = snl # snapshot list
		self.zsl = zsl # corresponding redshift list
		self.zArray = zArray # redshift for the dC - z conversion
		self.Melement = Melement # mass of one particle in the box
		self.Hbox = 67.77 # Hubble constant at redshift 0 in the box
		self.h = 0.6777
		self.omega_lambda = 0.692885
		self.omega_matter = 0.307115
		self.omega_baryon = 0.048206
		self.ns = 0.96
		self.sigma8 = 0.8228
		self.G = cc.G.to(u.km**2 * u.megaparsec /(u.solMass*u.s**2)).value # km2 Mpc / s2 solMass
		self.Msun = 1.98892 * 10**(33.) # g
		self.force_resolution = 5. # kpc /h
		#self.columnDict = {'id': 0, 'desc_id': 1, 'mvir': 2, 'vmax': 3, 'vrms': 4, 'rvir': 5, 'rs': 6, 'Np' : 7, 'x': 8, 'y': 9, 'z': 10, 'vx': 11, 'vy': 12, 'vz': 13, 'Jx': 14, 'Jy': 15, 'Jz': 16, 'Spin': 17, 'Rs_Klypin': 18, 'Mmvir_all': 19, 'M200b': 20, 'M200c': 21, 'M500c': 22, 'M2500c': 23,'Xoff': 24, 'Voff': 25, 'Spin_Bullock': 26, 'b_to_a': 27, 'c_to_a': 28, 'Ax': 29, 'Ay': 30, 'Az': 31, 'b_to_a_500c': 32, 'c_to_a_500c': 33, 'Ax_500c': 34, 'Ay_500c': 35, 'Az_500c': 36, 'TU': 37, 'M_pe_Behroozi': 38, 'M_pe_Diemer': 39, 'pid': 40}

		if self.boxDir == "MD_0.4Gpc_Rockstar":
			self.Melement = 9.63 * 10**7 # Msun
			self.Npart = 3840
			self.vmin =  (350 * self.Melement*self.G / 1. )**0.5 
			self.columnDict = {'id': 0, 'desc_id': 1, 'mvir': 2, 'vmax': 3, 'vrms': 4, 'rvir': 5, 'rs': 6, 'Np': 7, 'x': 8, 'y': 9, 'z': 10, 'vx': 11, 'vy': 12, 'vz': 13, 'Jx': 14, 'Jy': 15, 'Jz': 16, 'Spin':17, 'Rs_Klypin': 18, 'Mmvir_all': 19, 'M200b': 20, 'M200c': 21, 'M500c': 22, 'M2500c': 23, 'Xoff': 24, 'Voff': 25, 'Spin_Bullock': 26, 'b_to_a': 27, 'c_to_a': 28, 'Ax': 29, 'Ay': 30, 'Az': 31, 'b_to_a_500c': 32, 'c_to_a_500c': 33, 'Ax_500c': 34, 'Ay_500c': 35, 'Az_500c': 36, 'TU': 37, 'M_pe_Behroozi': 38, 'M_pe_Diemer': 39, 'pid': 40}
			#self.columnDict = {'scale': 0, 'id': 1, 'desc_scale': 2, 'desc_id': 3, 'num_prog': 4, 'pid': 5, 'upid': 6, 'desc_pid': 7, 'phantom': 8, 'sam_mvir': 9, 'mvir': 10, 'rvir': 11, 'rs': 12, 'vrms': 13, 'mmp?': 14, 'scale_of_last_MM': 15, 'vmax': 16, 'x': 17, 'y': 18, 'z': 19, 'vx': 20, 'vy': 21, 'vz': 22, 'Jx': 23, 'Jy': 24, 'Jz': 25, 'Spin': 26, 'Breadth_first_ID': 27, 'Depth_first_ID': 28, 'Tree_root_ID': 29, 'Orig_halo_ID': 30, 'Snap_num': 31, 'Next_coprogenitor_depthfirst_ID': 32, 'Last_progenitor_depthfirst_ID': 33, 'Last_mainleaf_depthfirst_ID': 34, 'Rs_Klypin': 35, 'Mmvir_all': 36, 'M200b': 37, 'M200c': 38, 'M500c': 39, 'M2500c': 40, 'Xoff': 41, 'Voff': 42, 'Spin_Bullock': 43, 'b_to_a': 44, 'c_to_a': 45, 'Ax': 46, 'Ay': 47, 'Az': 48, 'b_to_a500c': 49, 'c_to_a500c': 50, 'Ax500c': 51, 'Ay500c': 52, 'Az500c': 53, 'TU': 54, 'M_pe_Behroozi': 55, 'M_pe_Diemer': 56, 'Macc': 57, 'Mpeak': 58, 'Vacc': 59, 'Vpeak': 60, 'Halfmass_Scale': 61, 'Acc_Rate_Inst': 62, 'Acc_Rate_100Myr': 63, 'Acc_Rate_1Tdyn': 64, 'Acc_Rate_2Tdyn': 65, 'Acc_Rate_Mpeak': 66, 'Mpeak_Scale': 67, 'Acc_Scale': 68, 'First_Acc_Scale': 69, 'First_Acc_Mvir': 70, 'First_Acc_Vmax': 71, 'VmaxAtMpeak': 72}
			#{'scale': 0, 'id': 1, 'desc_scale': 2, 'desc_id': 3, 'num_prog': 4, 'pid': 5, 'upid': 6, 'desc_pid': 7, 'phantom': 8, 'sam_mvir': 9, 'mvir': 10, 'rvir': 11, 'rs': 12, 'vrms': 13, 'mmp?': 14, 'scale_of_last_MM': 15, 'vmax': 16, 'x': 17, 'y': 18, 'z': 19, 'vx': 20, 'vy': 21, 'vz': 22, 'Jx': 23, 'Jy': 24, 'Jz': 25, 'Spin': 26, 'Breadth_first_ID': 27, 'Depth_first_ID': 28, 'Tree_root_ID': 29, 'Orig_halo_ID': 30, 'Snap_num': 31, 'Next_coprogenitor_depthfirst_ID': 32, 'Last_progenitor_depthfirst_ID': 33, 'Last_mainleaf_depthfirst_ID': 34, 'Rs_Klypin': 35, 'Mmvir_all': 36, 'M200b': 37, 'M200c': 38, 'M500c': 39, 'M2500c': 40, 'Xoff': 41, 'Voff': 42, 'Spin_Bullock': 43, 'b_to_a': 44, 'c_to_a': 45, 'Ax': 46, 'Ay': 47, 'Az': 48, 'b_to_a_500c': 49, 'c_to_a_500c': 50, 'Ax_500c': 51, 'Ay_500c': 52, 'Az_500c': 53, 'TU': 54, 'M_pe_Behroozi': 55, 'M_pe_Diemer': 56, 'Macc': 57, 'Mpeak': 58, 'Vacc': 59, 'Vpeak': 60, 'Halfmass_Scale': 61, 'Acc_Rate_Inst': 62, 'Acc_Rate_100Myr': 63, 'Acc_Rate_1Tdyn': 64, 'Acc_Rate_2Tdyn': 65, 'Acc_Rate_Mpeak': 66, 'Mpeak_Scale': 67, 'Acc_Scale': 68, 'First_Acc_Scale': 69, 'First_Acc_Mvir': 70, 'First_Acc_Vmax': 71, 'VmaxatMpeak': 72}

		if self.boxDir == "MD_1.0Gpc_Rockstar":
			self.Melement = 1.51 * 10**9. # Msun
			self.Npart = 3840
			self.vmin =   (350 * self.Melement*self.G / 1. )**0.5 #(350 * self.Melement*self.Msun*self.G/(self.force_resolution*u.kpc.to('cm')))**0.5 * u.cm.to('km')
			self.columnDict = {'id': 0, 'desc_id': 1, 'mvir': 2, 'vmax': 3, 'vrms': 4, 'rvir': 5, 'rs': 6, 'Np': 7, 'x': 8, 'y': 9, 'z': 10, 'vx': 11, 'vy': 12, 'vz': 13, 'Jx': 14, 'Jy': 15, 'Jz': 16, 'Spin':17, 'Rs_Klypin': 18, 'Mmvir_all': 19, 'M200b': 20, 'M200c': 21, 'M500c': 22, 'M2500c': 23, 'Xoff': 24, 'Voff': 25, 'Spin_Bullock': 26, 'b_to_a': 27, 'c_to_a': 28, 'Ax': 29, 'Ay': 30, 'Az': 31, 'b_to_a_500c': 32, 'c_to_a_500c': 33, 'Ax_500c': 34, 'Ay_500c': 35, 'Az_500c': 36, 'TU': 37, 'M_pe_Behroozi': 38, 'M_pe_Diemer': 39, 'pid': 40}
			#self.columnDict = {'scale': 0, 'id': 1, 'desc_scale': 2, 'desc_id': 3, 'num_prog': 4, 'pid': 5, 'upid': 6, 'desc_pid': 7, 'phantom': 8, 'sam_mvir': 9, 'mvir': 10, 'rvir': 11, 'rs': 12, 'vrms': 13, 'mmp?': 14, 'scale_of_last_MM': 15, 'vmax': 16, 'x': 17, 'y': 18, 'z': 19, 'vx': 20, 'vy': 21, 'vz': 22, 'Jx': 23, 'Jy': 24, 'Jz': 25, 'Spin': 26, 'Breadth_first_ID': 27, 'Depth_first_ID': 28, 'Tree_root_ID': 29, 'Orig_halo_ID': 30, 'Snap_num': 31, 'Next_coprogenitor_depthfirst_ID': 32, 'Last_progenitor_depthfirst_ID': 33, 'Last_mainleaf_depthfirst_ID': 34, 'Tidal_Force': 35, 'Tidal_ID': 36, 'Rs_Klypin': 37, 'Mmvir_all': 38, 'M200b': 39, 'M200c': 40, 'M500c': 41, 'M2500c': 42, 'Xoff': 43, 'Voff': 44, 'Spin_Bullock': 45, 'b_to_a': 46, 'c_to_a': 47, 'Ax': 48, 'Ay': 49, 'Az': 50, 'b_to_a500c' : 51, 'c_to_a500c' : 52, 'Ax500c' : 53, 'Ay500c' : 54, 'Az500c' : 55, 'TU': 56, 'M_pe_Behroozi': 57, 'M_pe_Diemer': 58, 'Macc': 59, 'Mpeak': 60, 'Vacc': 61, 'Vpeak': 62, 'Halfmass_Scale': 63, 'Acc_Rate_Inst': 64, 'Acc_Rate_100Myr': 65, 'Acc_Rate_1Tdyn': 66, 'Acc_Rate_2Tdyn': 67, 'Acc_Rate_Mpeak': 68, 'Mpeak_Scale': 69, 'Acc_Scale': 70, 'First_Acc_Scale': 71, 'First_Acc_Mvir': 72, 'First_Acc_Vmax': 73, 'VmaxAtMpeak': 74, 'Tidal_Force_Tdyn': 75 }
			#{'scale': 0, 'id': 1, 'desc_scale': 2, 'desc_id': 3, 'num_prog': 4, 'pid': 5, 'upid': 6, 'desc_pid': 7, 'phantom': 8, 'sam_mvir': 9, 'mvir': 10, 'rvir': 11, 'rs': 12, 'vrms': 13, 'mmp?': 14, 'scale_of_last_MM': 15, 'vmax': 16, 'x': 17, 'y': 18, 'z': 19, 'vx': 20, 'vy': 21, 'vz': 22, 'Jx': 23, 'Jy': 24, 'Jz': 25, 'Spin': 26, 'Breadth_first_ID': 27, 'Depth_first_ID': 28, 'Tree_root_ID': 29, 'Orig_halo_ID': 30, 'Snap_num': 31, 'Next_coprogenitor_depthfirst_ID': 32, 'Last_progenitor_depthfirst_ID': 33, 'Last_mainleaf_depthfirst_ID': 34, 'Rs_Klypin': 35, 'Mmvir_all': 36, 'M200b': 37, 'M200c': 38, 'M500c': 39, 'M2500c': 40, 'Xoff': 41, 'Voff': 42, 'Spin_Bullock': 43, 'b_to_a': 44, 'c_to_a': 45, 'Ax': 46, 'Ay': 47, 'Az': 48, 'b_to_a_500c': 49, 'c_to_a_500c': 50, 'Ax_500c': 51, 'Ay_500c': 52, 'Az_500c': 53, 'TU': 54, 'M_pe_Behroozi': 55, 'M_pe_Diemer': 56, 'Macc': 57, 'Mpeak': 58, 'Vacc': 59, 'Vpeak': 60, 'Halfmass_Scale': 61, 'Acc_Rate_Inst': 62, 'Acc_Rate_100Myr': 63, 'Acc_Rate_1Tdyn': 64, 'Acc_Rate_2Tdyn': 65, 'Acc_Rate_Mpeak': 66, 'Mpeak_Scale': 67, 'Acc_Scale': 68, 'First_Acc_Scale': 69, 'First_Acc_Mvir': 70, 'First_Acc_Vmax': 71, 'VmaxatMpeak': 72}
			#{'id': 0, 'desc_id': 1, 'mvir': 2, 'vmax': 3, 'vrms': 4, 'rvir': 5, 'rs': 6, 'Np': 7, 'x': 8, 'y': 9, 'z': 10, 'vx': 11, 'vy': 12, 'vz': 13, 'Jx': 14, 'Jy': 15, 'Jz': 16, 'Spin':17, 'Rs_Klypin': 18, 'Mmvir_all': 19, 'M200b': 20, 'M200c': 21, 'M500c': 22, 'M2500c': 23, 'Xoff': 24, 'Voff': 25, 'Spin_Bullock': 26, 'b_to_a': 27, 'c_to_a': 28, 'Ax': 29, 'Ay': 30, 'Az': 31, 'b_to_a_500c': 32, 'c_to_a_500c': 33, 'Ax_500c': 34, 'Ay_500c': 35, 'Az_500c': 36, 'TU': 37, 'M_pe_Behroozi': 38, 'M_pe_Diemer': 39, 'pid': 40}

		if self.boxDir == "MD_2.5Gpc_Rockstar":
			self.Melement = 2.359 * 10**10. # Msun
			self.Npart = 3840
			self.vmin =  (350 * self.Melement*self.G / 1. )**0.5 # (350 * self.Melement*self.Msun*self.G/(self.force_resolution*u.kpc.to('cm')))**0.5 * u.cm.to('km')
			self.columnDict = {'id': 0, 'desc_id': 1, 'mvir': 2, 'vmax': 3, 'vrms': 4, 'rvir': 5, 'rs': 6, 'Np': 7, 'x': 8, 'y': 9, 'z': 10, 'vx': 11, 'vy': 12, 'vz': 13, 'Jx': 14, 'Jy': 15, 'Jz': 16, 'Spin':17, 'Rs_Klypin': 18, 'Mmvir_all': 19, 'M200b': 20, 'M200c': 21, 'M500c': 22, 'M2500c': 23, 'Xoff': 24, 'Voff': 25, 'Spin_Bullock': 26, 'b_to_a': 27, 'c_to_a': 28, 'Ax': 29, 'Ay': 30, 'Az': 31, 'b_to_a_500c': 32, 'c_to_a_500c': 33, 'Ax_500c': 34, 'Ay_500c': 35, 'Az_500c': 36, 'TU': 37, 'M_pe_Behroozi': 38, 'M_pe_Diemer': 39, 'pid': 40}
			#{'scale': 0, 'id': 1, 'desc_scale': 2, 'desc_id': 3, 'num_prog': 4, 'pid': 5, 'upid': 6, 'desc_pid': 7, 'phantom': 8, 'sam_mvir': 9, 'mvir': 10, 'rvir': 11, 'rs': 12, 'vrms': 13, 'mmp?': 14, 'scale_of_last_MM': 15, 'vmax': 16, 'x': 17, 'y': 18, 'z': 19, 'vx': 20, 'vy': 21, 'vz': 22, 'Jx': 23, 'Jy': 24, 'Jz': 25, 'Spin': 26, 'Breadth_first_ID': 27, 'Depth_first_ID': 28, 'Tree_root_ID': 29, 'Orig_halo_ID': 30, 'Snap_num': 31, 'Next_coprogenitor_depthfirst_ID': 32, 'Last_progenitor_depthfirst_ID': 33, 'Last_mainleaf_depthfirst_ID': 34, 'Rs_Klypin': 35, 'Mmvir_all': 36, 'M200b': 37, 'M200c': 38, 'M500c': 39, 'M2500c': 40, 'Xoff': 41, 'Voff': 42, 'Spin_Bullock': 43, 'b_to_a': 44, 'c_to_a': 45, 'Ax': 46, 'Ay': 47, 'Az': 48, 'b_to_a_500c': 49, 'c_to_a_500c': 50, 'Ax_500c': 51, 'Ay_500c': 52, 'Az_500c': 53, 'TU': 54, 'M_pe_Behroozi': 55, 'M_pe_Diemer': 56, 'Halfmass_Radius': 57, 'Macc': 58, 'Mpeak': 59, 'Vacc': 60, 'Vpeak': 61, 'Halfmass_Scale': 62, 'Acc_Rate_Inst': 63, 'Acc_Rate_100Myr': 64, 'Acc_Rate_1Tdyn': 65, 'Acc_Rate_2Tdyn': 66, 'Acc_Rate_Mpeak': 67, 'Mpeak_Scale': 68, 'Acc_Scale': 69, 'First_Acc_Scale': 70, 'First_Acc_Mvir': 71, 'First_Acc_Vmax': 72, 'VmaxatMpeak': 73}

		if self.boxDir == "MD_4.0Gpc_Rockstar":
			self.Melement = 9.6 * 10**10. # Msun
			self.Npart = 4096
			self.vmin =  (350 * self.Melement*self.G / 1. )**0.5 # (350 * self.Melement*self.Msun*self.G/(self.force_resolution*u.kpc.to('cm')))**0.5 * u.cm.to('km')
			self.columnDict = {'id': 0, 'desc_id': 1, 'mvir': 2, 'vmax': 3, 'vrms': 4, 'rvir': 5, 'rs': 6, 'Np': 7, 'x': 8, 'y': 9, 'z': 10, 'vx': 11, 'vy': 12, 'vz': 13, 'Jx': 14, 'Jy': 15, 'Jz': 16, 'Spin':17, 'Rs_Klypin': 18, 'Mmvir_all': 19, 'M200b': 20, 'M200c': 21, 'M500c': 22, 'M2500c': 23, 'Xoff': 24, 'Voff': 25, 'Spin_Bullock': 26, 'b_to_a': 27, 'c_to_a': 28, 'Ax': 29, 'Ay': 30, 'Az': 31, 'b_to_a_500c': 32, 'c_to_a_500c': 33, 'Ax_500c': 34, 'Ay_500c': 35, 'Az_500c': 36, 'TU': 37, 'M_pe_Behroozi': 38, 'M_pe_Diemer': 39, 'pid': 40}

	def writePositionCatalog(self, ii, vmin=65, vmax=10000, NperBatch = 10000000):
		"""
		Extracts the positions and velocity out of a snapshot of the Multidark simulation.        
		:param ii: index of the snapshot in the list self.snl
		:param vmin: name of the quantity of interest, mass, velocity.
		:param vmax: of the quantity of interest in the snapshots.
		:param NperBatch: number of line per fits file, default: 1000000
		 """		
		print "uncompressing ", time.time()
		os.system("bzcat "+self.snl[ii] + " > " + self.snl[ii][:-4])
		print "reading file ", time.time()
		fl = fileinput.input(self.snl[ii][:-4])
		nameSnapshot = self.snl[ii].split('/')[-1][:-5]
		Nb = 0
		count = 0
		output = n.empty((NperBatch,5))
		for line in fl:
			if line[0] == "#" :
				continue

			line = line.split()
			newline =n.array([ float(line[self.columnDict['x']]), float(line[self.columnDict['y']]), float(line[self.columnDict['z']]), float(line[self.columnDict['vmax']]), float(line[self.columnDict['pid']]), float(line[self.columnDict['mvir']]), float(line[self.columnDict['M200c']]) ])
			if newline[3]>vmin and newline[3]<vmax :
				output[count] = newline
				count+=1
				
			if count == NperBatch  :
				print "count",count
				print output
				print output.shape
				print output.T[0].shape
				#define the columns
				col0 = fits.Column(name='x',format='D', array=output.T[0] )
				col1 = fits.Column(name='y',format='D', array= output.T[1] )
				col2 = fits.Column(name='z',format='D', array= output.T[2] )
				col3 = fits.Column(name='vmax',format='D', array= output.T[3] )
				col4 = fits.Column(name='mvir',format='D', array= output.T[4] )
				col5 = fits.Column(name='M200c',format='D', array= output.T[5] )
				col6 = fits.Column(name='pid',format='D', array= output.T[4] )
				#define the table hdu 
				hdu_cols  = fits.ColDefs([col0, col1, col2, col3, col4, col5, col6])
				tb_hdu = fits.BinTableHDU.from_columns( hdu_cols )
				#define the header
				prihdr = fits.Header()
				prihdr['HIERARCH nameSnapshot'] = nameSnapshot
				prihdr['count'] = count
				prihdr['batchN'] = Nb
				prihdu = fits.PrimaryHDU(header=prihdr)
				#writes the file
				thdulist = fits.HDUList([prihdu, tb_hdu])
				os.system("rm "+self.snl[ii][:-5]+"_Nb_"+str(Nb)+".fits")
				thdulist.writeto(self.snl[ii][:-5]+"_Nb_"+str(Nb)+".fits")
				Nb+=1
				count=0
				output = n.empty((NperBatch,5))

		# and for the last batch :
		col0 = fits.Column(name='x',format='D', array=output.T[0] )
		col1 = fits.Column(name='y',format='D', array= output.T[1] )
		col2 = fits.Column(name='z',format='D', array= output.T[2] )
		col3 = fits.Column(name='vmax',format='D', array= output.T[3] )
		col4 = fits.Column(name='mvir',format='D', array= output.T[4] )
		col5 = fits.Column(name='M200c',format='D', array= output.T[5] )
		col6 = fits.Column(name='pid',format='D', array= output.T[4] )
		#define the table hdu 
		hdu_cols  = fits.ColDefs([col0, col1, col2, col3, col4, col5, col6])
		tb_hdu = fits.BinTableHDU.from_columns( hdu_cols )
		#define the header
		prihdr = fits.Header()
		prihdr['HIERARCH nameSnapshot'] = nameSnapshot
		prihdr['batchN'] = Nb
		prihdr['count'] = count
		prihdu = fits.PrimaryHDU(header=prihdr)
		#writes the file
		thdulist = fits.HDUList([prihdu, tb_hdu])
		os.system("rm "+self.snl[ii][:-5]+"_Nb_"+str(Nb)+".fits")
		thdulist.writeto(self.snl[ii][:-5]+"_Nb_"+str(Nb)+".fits")
	
	def compute2PCF(self, catalogList, vmin=65, rmax=200, dlogBin=0.05, Nmax=4000000., dr = 1., name = ""):
		"""
		Extracts the 2PCF out of a catalog of halos        
		:param catalog: where the catalog is
		:param vmin: minimum circular velocity.
		:param dlogBin: bin width.
		:param rmax: maximum distance
		"""
		hdus = []
		for ii in n.arange(len(catalogList)):
			hdus.append( fits.open(catalogList[ii])[1].data )

		vbins = 10**n.arange(n.log10(vmin),4. ,dlogBin)
		for jj in range(len(vbins)-1):
			outfile = catalogList[0][:-10] + "_vmax_" +str(n.round(vbins[jj],2))+ "_" +str(n.round(vbins[jj+1],2)) + "_" + name + "_xiR.pkl"
			t0 = time.time()
			sel = n.array([ (hdu['vmax']>vbins[jj])&(hdu['vmax']<vbins[jj+1]) for hdu in hdus])
			xR = n.hstack(( n.array([ hdus[ii]['x'][sel[ii]] for ii in range(len(hdus)) ]) ))
			yR = n.hstack(( n.array([ hdus[ii]['y'][sel[ii]] for ii in range(len(hdus)) ]) ))
			zR = n.hstack(( n.array([ hdus[ii]['z'][sel[ii]] for ii in range(len(hdus)) ]) ))
			Ntotal = len(xR)
			if len(xR)>20000 and len(xR)<=Nmax:
				print vbins[jj], vbins[jj+1]
				insideSel=(xR>rmax)&(xR<self.Lbox.value-rmax)&(yR>rmax)&(yR<self.Lbox.value-rmax)&(zR>rmax)&(zR<self.Lbox.value-rmax)
				volume=(self.Lbox.value)**3
				# defines the trees
				print "creates trees"
				treeRandoms=t.cKDTree(n.transpose([xR,yR,zR]),1000.0)
				treeData=t.cKDTree(n.transpose([xR[insideSel],yR[insideSel],zR[insideSel]]),1000.0)
				nD=len(treeData.data)
				nR=len(treeRandoms.data)
				print nD, nR
				bin_xi3D=n.arange(0, rmax, dr)
				# now does the pair counts :
				pairs=treeData.count_neighbors(treeRandoms, bin_xi3D)
				t3 = time.time()
				DR=pairs[1:]-pairs[:-1]
				dV= (bin_xi3D[1:]**3 - bin_xi3D[:-1]**3 )*4*n.pi/3.
				pairCount=nD*nR#-nD*(nD-1)/2.
				xis = DR*volume/(dV * pairCount) -1.
				f=open(outfile,'w')
				cPickle.dump([bin_xi3D,xis, DR, volume, dV, pairCount, pairs, Ntotal, nD, nR, vbins[jj], vbins[jj+1]],f)
				f.close()
				t4 = time.time()
				print "total time in s, min",t4 - t0, (t4 - t0)/60.
				#return DR, volume, dV, pairCount, pairs, nD, nR

			if  len(xR)>Nmax:
				print vbins[jj], vbins[jj+1], "downsampling ..."
				downSamp = (n.random.random(len(xR))<Nmax / float(len(xR)) )
				xR = xR[downSamp]
				yR = yR[downSamp]
				zR = zR[downSamp]
				
				insideSel=(xR>rmax)&(xR<self.Lbox.value-rmax)&(yR>rmax)&(yR<self.Lbox.value-rmax)&(zR>rmax)&(zR<self.Lbox.value-rmax)
				volume=(self.Lbox.value-rmax*2)**3
				# defines the trees
				print "creates trees"
				treeRandoms=t.cKDTree(n.transpose([xR,yR,zR]),1000.0)
				treeData=t.cKDTree(n.transpose([xR[insideSel],yR[insideSel],zR[insideSel]]),1000.0)
				nD=len(treeData.data)
				nR=len(treeRandoms.data)
				print nD, nR
				bin_xi3D=n.arange(0, rmax, dr)
				# now does the pair counts :
				pairs=treeData.count_neighbors(treeRandoms, bin_xi3D)
				t3 = time.time()
				DR=pairs[1:]-pairs[:-1]
				dV=4*n.pi*(bin_xi3D[1:]**3 - bin_xi3D[:-1]**3 )/3.
				pairCount=nD*nR#-nD*(nD-1)/2.
				xis = DR*volume/(dV * pairCount) -1.
				f=open(outfile,'w')
				cPickle.dump([bin_xi3D,xis, DR, volume, dV, pairCount, pairs, Ntotal, nD, nR, vbins[jj], vbins[jj+1]],f)
				f.close()
				t4 = time.time()
				print "total time in s, min",t4 - t0, (t4 - t0)/60.
				#return DR, volume, dV, pairCount, pairs, nD, nR


	def computeSingleDistributionFunction(self, ii, name, bins, Mfactor=100. ) :
		"""
		Extracts the distribution of quantity 'name' out of all snapshots of the Multidark simulation.        
		:param ii: index of the snapshot in the list self.snl
		:param name: name of the quantity of interest, mass, velocity.
		:param index: of the quantity of interest in the snapshots.
		:param bins: binning scheme to compute the historgram.
		:param Mfactor: only halos with Mvir > Mfact* Melement are used.
		"""		
		index = self.columnDict[name]
		output_dir = join(self.wdir,self.boxDir,"properties",name)
		os.system('mkdir '+ output_dir)
		NperBatch = 10000000
		qtyCentral = n.empty(NperBatch)  # 10M array
		qtySat = n.empty(NperBatch)  # 10M array
		print name, index, output_dir

		fl = fileinput.input(self.snl[ii])
		nameSnapshot = self.snl[ii].split('/')[-1][:-5]

		countCen,countSat,countFileCen,countFileSat = 0,0,0,0
		
		for line in fl:
			if line[0] == "#" :
				continue

			line = line.split()
			sat_or_cen = float(line[self.columnDict['pid']])
			mv = float(line[self.columnDict['mvir']])
			if sat_or_cen != -1 and mv > Mfactor * self.Melement :
				countSat+= 1					
				qtySat[countSat] = float(line[index])
				
			if sat_or_cen == -1 and mv > Mfactor * self.Melement :
				countCen+= 1					
				qtyCentral[countCen] = float(line[index])
				
			if countCen == NperBatch-1 :
				nnM,bb = n.histogram(n.log10(qtyCentral),bins = bins)
				print "countCen",countCen
				f = open(join(output_dir, nameSnapshot + "_" + name + "_Central_" + str(countFileCen)+ ".pkl"),'w')
				cPickle.dump(nnM,f)
				f.close()
				countFileCen+= 1
				countCen = 0
				qtyCentral = n.empty(NperBatch)

			if countSat == NperBatch-1 :
				nnM,bb = n.histogram(n.log10(qtySat),bins = bins)
				print "countSat", countSat
				f = open(join(output_dir, nameSnapshot + "_" + name+ "_Satellite_" + str(countFileSat)+ ".pkl"),'w')
				cPickle.dump(nnM,f)
				f.close()
				countFileSat+= 1
				countSat = 0
				qtySat = n.empty(NperBatch)

		# and for the last batch :
		nnM,bb = n.histogram(n.log10(qtyCentral),bins = bins)
		f = open(join(output_dir, nameSnapshot + "_" + name +"_Central_" + str(countFileCen)+ ".pkl"),'w')
		cPickle.dump(nnM,f)
		f.close()

		nnM,bb = n.histogram(n.log10(qtySat),bins = bins)
		f = open(join(output_dir, nameSnapshot + "_" + name + "_Satellite_" + str(countFileSat)+ ".pkl"),'w')
		cPickle.dump(nnM,f)
		f.close()
		
		n.savetxt(join(output_dir,name+".bins"),n.transpose([bins]))



	def combinesSingleDistributionFunction(self, ii, name='Vpeak', bins=10**n.arange(0,3.5,0.01), type = "Central" ) :
		"""
		Coombines the outputs of computeSingleDistributionFunction.
		:param ii: index of the snapshot
		:param name: name of the quantity studies
		:param bins: bins the histogram was done with
		:param type: "Central" or "Satellite"
		"""
		output_dir = join(self.wdir,self.boxDir,"properties",name)
		nameSnapshot = self.snl[ii].split('/')[-1][:-5]
		pklList = n.array(glob.glob(join(output_dir, nameSnapshot + "_" + name +"_"+type+"_*.pkl")))

		nnM = n.empty( [len(pklList),len(bins)-1] ) 
		for jj in range(len(pklList)):
			f=open(pklList[jj],'r')
			nnMinter = cPickle.load(f)
			nnM[jj] = nnMinter
			f.close()

		n.savetxt(join(output_dir,"hist-"+type+"-"+name+"-"+nameSnapshot[6:]+".dat"),n.transpose([bins[:-1], bins[1:], nnM.sum(axis=0)]))


	def computeDoubleDistributionFunction(self, ii, nameA, nameB, binsA, binsB, Mfactor = 100. ) :
		"""
		Extracts the distributions of two quantity and their correlation 'name' out of all snapshots of the Multidark simulation.
		:param ii: index of the snapshot in the list self.snl
		:param name: name of the quantity of interest, mass, velocity.
		:param index: of the quantity of interest in the snapshots.
		:param bins: binning scheme to compute the historgram.
		:param Mfactor: only halos with Mvir > Mfact* Melement are used.
		"""		
		indexA = self.columnDict[nameA]
		indexB = self.columnDict[nameB]
		output_dir = join(self.wdir,self.boxDir,"properties",nameA+"-"+nameB)
		os.system('mkdir '+ output_dir)
		NperBatch = 10000000
		qtyCentral = n.empty((NperBatch,2))  # 10M array
		qtySat = n.empty((NperBatch,2))  # 10M array
		print nameA, nameB, indexA, indexB, output_dir

		fl = fileinput.input(self.snl[ii])
		nameSnapshot = self.snl[ii].split('/')[-1][:-5]

		countCen,countSat,countFileCen,countFileSat = 0,0,0,0
		
		for line in fl:
			if line[0] == "#" :
				continue

			line = line.split()
			sat_or_cen = float(line[self.columnDict['pid']])
			mv = float(line[self.columnDict['mvir']])
			if sat_or_cen != -1 and mv > Mfactor * self.Melement :
				countSat+= 1					
				qtySat[countSat] = float(line[indexA]),float(line[indexB])
				
			if sat_or_cen == -1 and mv > Mfactor * self.Melement :
				countCen+= 1					
				qtyCentral[countCen] = float(line[indexA]),float(line[indexB])
				
			if countCen == NperBatch-1 :
				nnA,bbA = n.histogram(n.log10(qtyCentral.T[0]),bins = binsA)
				nnB,bbB = n.histogram(n.log10(qtyCentral.T[1]),bins = binsB)
				dataAB = n.histogram2d(n.log10(qtyCentral.T[0]), n.log10(qtyCentral.T[1]) ,bins = [binsA,binsB])
				print "countCen",countCen
				f = open(join(output_dir, nameSnapshot + "_" + nameA+"-"+nameB + "_Central_" + str(countFileCen)+ ".pkl"),'w')
				cPickle.dump([nnA,nnB,dataAB],f)
				f.close()
				countFileCen+= 1
				countCen = 0
				qtyCentral = n.empty((NperBatch,2))

			if countSat == NperBatch-1 :
				nnA,bbA = n.histogram(n.log10(qtySat.T[0]),bins = binsA)
				nnB,bbB = n.histogram(n.log10(qtySat.T[1]),bins = binsB)
				dataAB = n.histogram2d(n.log10(qtySat.T[0]), n.log10(qtySat.T[1]) ,bins = [binsA,binsB])
				print "countSat", countSat
				f = open(join(output_dir, nameSnapshot + "_" + nameA+"-"+nameB+ "_Satellite_" + str(countFileSat)+ ".pkl"),'w')
				cPickle.dump([nnA,nnB,dataAB],f)
				f.close()
				countFileSat+= 1
				countSat = 0
				qtySat = n.empty((NperBatch,2))

		# and for the last batch :
		nnA,bbA = n.histogram(n.log10(qtyCentral.T[0]),bins = binsA)
		nnB,bbB = n.histogram(n.log10(qtyCentral.T[1]),bins = binsB)
		dataAB = n.histogram2d(n.log10(qtyCentral.T[0]), n.log10(qtyCentral.T[1]) ,bins = [binsA,binsB])
		print "countCen",countCen
		f = open(join(output_dir, nameSnapshot + "_" + nameA+"-"+nameB + "_Central_" + str(countFileCen)+ ".pkl"),'w')
		cPickle.dump([nnA,nnB,dataAB],f)
		f.close()

		nnA,bbA = n.histogram(n.log10(qtySat.T[0]),bins = binsA)
		nnB,bbB = n.histogram(n.log10(qtySat.T[1]),bins = binsB)
		dataAB = n.histogram2d(n.log10(qtySat.T[0]), n.log10(qtySat.T[1]) ,bins = [binsA,binsB])
		print "countSat", countSat
		f = open(join(output_dir, nameSnapshot + "_" + nameA+"-"+nameB+ "_Satellite_" + str(countFileSat)+ ".pkl"),'w')
		cPickle.dump([nnA,nnB,dataAB],f)
		f.close()
		
		n.savetxt(join(output_dir,nameA+".bins"),n.transpose([binsA]))
		n.savetxt(join(output_dir,nameB+".bins"),n.transpose([binsB]))

	def combinesDoubleDistributionFunction(self, ii, nameA, nameB, binsA, binsB, type = "Central" ) :
		"""
		Coombines the outputs of computeDoubleDistributionFunction.
		:param ii: index of the snapshot
		:param name: name of the quantity studies
		:param bins: bins the histogram was done with
		:param type: "Central" or "Satellite"
		"""
		output_dir = join(self.wdir,self.boxDir,"properties",nameA+"-"+nameB)
		nameSnapshot = self.snl[ii].split('/')[-1][:-5]
		pklList = n.array(glob.glob(join(output_dir, nameSnapshot + "_" + nameA+"-"+nameB +"_"+type+"_*.pkl")))

		nnA = n.empty( [len(pklList),len(binsA)-1] ) 
		nnB = n.empty( [len(pklList),len(binsB)-1] ) 
		dataAB = n.empty( [len(pklList),len(binsA)-1,len(binsB)-1] ) 
		for jj in range(len(pklList)):
			f=open(pklList[jj],'r')
			nnAinter, nnBinter, dataABinter = cPickle.load(f)
			nnA[jj] = nnAinter
			nnB[jj] = nnBinter
			dataAB[jj] = dataABinter[0]
			f.close()

		n.savetxt(join(output_dir,"hist-"+type+"-"+nameA+"-"+nameSnapshot[6:]+".dat"),n.transpose([binsA[:-1], binsA[1:], nnA.sum(axis=0)]))
		n.savetxt(join(output_dir,"hist-"+type+"-"+nameB+"-"+nameSnapshot[6:]+".dat"),n.transpose([binsB[:-1], binsB[1:], nnB.sum(axis=0)]))
		n.savetxt(join(output_dir, "hist2d-"+type+"-"+ nameA+"-"+nameB + "-"+ nameSnapshot[6:] + ".dat"), dataAB.sum(axis=0))


	def computeMassVelocityConcentrationFunction(self,ii) :
		"""
		DO NOT USE
		computes the mass, velocity and concentration histograms for a rockstar snapshot.
		:param ii: index of the snapshot in the list self.snl
		# does not work any more 
		DO NOT USE
		"""
		massB = n.arange(8,16,0.01)
		vcirB = n.arange(0,4.5,0.01)
		concB = n.arange(1,3,0.1)

		NperBatch = 10000000
		mvcCentralMatrix = n.empty((NperBatch,3))  # 1M matrixes
		mvcSatMatrix = n.empty((NperBatch,3))  # 1 M matrixes

		fl = fileinput.input(self.snl[ii])
		name = self.snl[ii].split('/')[-1][:-5]
		countCen,countSat,countFileCen,countFileSat = 0,0,0,0
		for line in fl:
			if line[0] == "#" :
				continue

			line = line.split()
			sat_or_cen = float(line[5])
			if sat_or_cen != -1 :
				countSat+= 1					
				mvcSatMatrix[countSat] = float(line[10]), float(line[16]), float(line[11]) 
				
			if sat_or_cen == -1 :
				countCen+= 1					
				mvcCentralMatrix[countCen] = float(line[10]), float(line[16]), float(line[11])
				
			if countCen == NperBatch-1 :
				nnM,bb = n.histogram(n.log10(mvcCentralMatrix.T[0]),bins = massB)
				nnV,bb = n.histogram(n.log10(mvcCentralMatrix.T[1]),bins =  vcirB)
				nnC,bb = n.histogram(n.log10(mvcCentralMatrix.T[2]),bins =  concB)
				dataMC = n.histogram2d(n.log10(mvcCentralMatrix.T[0]), mvcCentralMatrix.T[2] ,bins = [massB,concB])
				dataVC = n.histogram2d(n.log10(mvcCentralMatrix.T[1]), mvcCentralMatrix.T[2] , bins = [vcirB,concB])
				print "countCen",countCen
				f = open(join(self.wdir,self.boxDir,"properties", name+"_MVRmatrixCentral_" +str(countFileCen)+ ".pkl"),'w')
				cPickle.dump([nnM,nnV,nnC,dataMC,dataVC],f)
				f.close()
				countFileCen+= 1
				countCen = 0

			if countSat == NperBatch-1 :
				nnM,bb = n.histogram(n.log10(mvcSatMatrix.T[0]),bins = massB)
				nnV,bb = n.histogram(n.log10(mvcSatMatrix.T[1]),bins =  vcirB)
				nnC,bb = n.histogram(n.log10(mvcSatMatrix.T[2]),bins =  concB)
				dataMC = n.histogram2d(n.log10(mvcSatMatrix.T[0]), mvcSatMatrix.T[2] ,bins = [massB,concB])
				dataVC = n.histogram2d(n.log10(mvcSatMatrix.T[1]), mvcSatMatrix.T[2] , bins = [vcirB,concB])
				print "countSat", countSat
				f = open(join(self.wdir,self.boxDir ,"properties" , 
	name+"_MVRmatrixSatellite_" +str(countFileSat)+ ".pkl"),'w')
				cPickle.dump([nnM,nnV,nnC,dataMC,dataVC],f)
				f.close()
				countFileSat+= 1
				countSat = 0

		# and for the last batch :
		nnM,bb = n.histogram(n.log10(mvcCentralMatrix.T[0]),bins = massB)
		nnV,bb = n.histogram(n.log10(mvcCentralMatrix.T[1]),bins =  vcirB)
		nnC,bb = n.histogram(n.log10(mvcCentralMatrix.T[2]),bins =  concB)
		dataMC = n.histogram2d(n.log10(mvcCentralMatrix.T[0]), mvcCentralMatrix.T[2] ,bins = [massB,concB])
		dataVC = n.histogram2d(n.log10(mvcCentralMatrix.T[1]), mvcCentralMatrix.T[2] , bins = [vcirB,concB])
		f = open(join(self.wdir,self.boxDir,"properties",name+ "_MVRmatrixCentral_" +str(countFileCen)+ ".pkl"),'w')
		cPickle.dump([nnM,nnV,nnC,dataMC,dataVC],f)
		f.close()

		nnM,bb = n.histogram(n.log10(mvcSatMatrix.T[0]),bins = massB)
		nnV,bb = n.histogram(n.log10(mvcSatMatrix.T[1]),bins =  vcirB)
		nnC,bb = n.histogram(n.log10(mvcSatMatrix.T[2]),bins =  concB)
		dataMC = n.histogram2d(n.log10(mvcSatMatrix.T[0]), mvcSatMatrix.T[2] ,bins = [massB,concB])
		dataVC = n.histogram2d(n.log10(mvcSatMatrix.T[1]), mvcSatMatrix.T[2] , bins = [vcirB,concB])
		f = open(join(self.wdir,self.boxDir,"properties",name+ "_MVRmatrixSatellite_" +str(countFileSat)+ ".pkl"),'w')
		cPickle.dump([nnM,nnV,nnC,dataMC,dataVC],f)
		f.close()


	def computeMassVelocityPeakAccRateFunctions(self,ii) :
		"""
		DO NOT USE
		computes the mass, velocity and concentration histograms for a rockstar snapshot.
		:param ii: index of the snapshot in the list self.snl()
		DO NOT USE
		"""
		massB = n.arange(8,16,0.01)
		vcirB = n.arange(0,4.5,0.01)
		concB = n.arange(-5e4,5e4+1,1e3)

		NperBatch = 10000000
		mvcCentralMatrix = n.empty((NperBatch,3))  # 1M matrixes
		mvcSatMatrix = n.empty((NperBatch,3))  # 1 M matrixes

		fl = fileinput.input(self.snl[ii])
		name = self.snl[ii].split('/')[-1][:-5]
		countCen,countSat,countFileCen,countFileSat = 0,0,0,0
		for line in fl:
			if line[0] == "#" :
				continue

			line = line.split()
			sat_or_cen = float(line[5])
			if sat_or_cen != -1 :
				countSat+= 1					
				#print mvcSatMatrix[countSat]
				#print line[59], line[61], line[67]
				mvcSatMatrix[countSat] = float(line[59]), float(line[61]), float(line[67]) # check the right indices ... MASS velocity concentration

			if sat_or_cen == -1 :
				countCen+= 1					
				#print mvcCentralMatrix[countCen]
				#print line[59], line[61], line[67]
				mvcCentralMatrix[countCen] = float(line[59]), float(line[61]), float(line[67]) # check the right indices ... MASS velocity concentration

			if countCen == NperBatch-1 :
				nnM,bb = n.histogram(n.log10(mvcCentralMatrix.T[0]),bins = massB)
				nnV,bb = n.histogram(n.log10(mvcCentralMatrix.T[1]),bins =  vcirB)
				nnC,bb = n.histogram(n.log10(mvcCentralMatrix.T[2]),bins =  concB)
				dataMC = n.histogram2d(n.log10(mvcCentralMatrix.T[0]), mvcCentralMatrix.T[2] ,bins = [massB,concB])
				dataVC = n.histogram2d(n.log10(mvcCentralMatrix.T[1]), mvcCentralMatrix.T[2] , bins = [vcirB,concB])
				print "countCen",countCen
				f = open(join(self.wdir,self.boxDir,"properties", name+"_MVAmatrixCentral_" +str(countFileCen)+ ".pkl"),'w')
				cPickle.dump([nnM,nnV,nnC,dataMC,dataVC],f)
				f.close()
				countFileCen+= 1
				countCen = 0

			if countSat == NperBatch-1 :
				nnM,bb = n.histogram(n.log10(mvcSatMatrix.T[0]),bins = massB)
				nnV,bb = n.histogram(n.log10(mvcSatMatrix.T[1]),bins =  vcirB)
				nnC,bb = n.histogram(n.log10(mvcSatMatrix.T[2]),bins =  concB)
				dataMC = n.histogram2d(n.log10(mvcSatMatrix.T[0]), mvcSatMatrix.T[2] ,bins = [massB,concB])
				dataVC = n.histogram2d(n.log10(mvcSatMatrix.T[1]), mvcSatMatrix.T[2] , bins = [vcirB,concB])
				print "countSat", countSat
				f = open(join(self.wdir,self.boxDir ,"properties" , 
	name+"_MVAmatrixSatellite_" +str(countFileSat)+ ".pkl"),'w')
				cPickle.dump([nnM,nnV,nnC,dataMC,dataVC],f)
				f.close()
				countFileSat+= 1
				countSat = 0

		# and for the last batch :
		nnM,bb = n.histogram(n.log10(mvcCentralMatrix.T[0]),bins = massB)
		nnV,bb = n.histogram(n.log10(mvcCentralMatrix.T[1]),bins =  vcirB)
		nnC,bb = n.histogram(n.log10(mvcCentralMatrix.T[2]),bins =  concB)
		dataMC = n.histogram2d(n.log10(mvcCentralMatrix.T[0]), mvcCentralMatrix.T[2] ,bins = [massB,concB])
		dataVC = n.histogram2d(n.log10(mvcCentralMatrix.T[1]), mvcCentralMatrix.T[2] , bins = [vcirB,concB])
		f = open(join(self.wdir,self.boxDir,"properties",name+ "_MVAmatrixCentral_" +str(countFileCen)+ ".pkl"),'w')
		cPickle.dump([nnM,nnV,nnC,dataMC,dataVC],f)
		f.close()

		nnM,bb = n.histogram(n.log10(mvcSatMatrix.T[0]),bins = massB)
		nnV,bb = n.histogram(n.log10(mvcSatMatrix.T[1]),bins =  vcirB)
		nnC,bb = n.histogram(n.log10(mvcSatMatrix.T[2]),bins =  concB)
		dataMC = n.histogram2d(n.log10(mvcSatMatrix.T[0]), mvcSatMatrix.T[2] ,bins = [massB,concB])
		dataVC = n.histogram2d(n.log10(mvcSatMatrix.T[1]), mvcSatMatrix.T[2] , bins = [vcirB,concB])
		f = open(join(self.wdir,self.boxDir,"properties",name+ "_MVAmatrixSatellite_" +str(countFileSat)+ ".pkl"),'w')
		cPickle.dump([nnM,nnV,nnC,dataMC,dataVC],f)
		f.close()


