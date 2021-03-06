#  cd pySU/pyMultidark/trunk/bin/fortranfile-0.2.1/
import sys
import numpy as n
import os
from os.path import join
from astropy.io import fits
import time
import cPickle
from scipy.interpolate import interp1d
from scipy.optimize import curve_fit
from scipy.stats import scoreatpercentile as sc
from scipy.stats import norm
from scipy.stats import lognorm
import matplotlib.pyplot as p
from matplotlib.ticker import NullFormatter
nullfmt = NullFormatter()         # no labels
from scipy.optimize import curve_fit
import astropy.cosmology as co
import astropy.units as uu

DFdir = join("/data2", "users", "gustavo", "BigMD", "1Gpc_3840_Planck1_New", "DENSFIELDS")
# mockDir = "/data1/DATA/eBOSS/Multidark-box-mocks/parts/"
mockDir = join("..","MD_1Gpc","density_field")


#################################################
#################################################
# DM ALL FIELD
#################################################
#################################################


Mp = 1.51 * 10**9. * uu.solMass
CELL =1000./2048.*uu.megaparsec

DFdir = join("/data2", "users", "gustavo", "BigMD", "1Gpc_3840_Planck1_New", "DENSFIELDS")
# mockDir = "/data1/DATA/eBOSS/Multidark-box-mocks/parts/"
mockDir = join("..","MD_1Gpc","density_field")

def getNN0_sim(inSim):
	f=open(join(mockDir, inSim))
	bins, HDF0 = cPickle.load(f)
	f.close()
	#bins = n.hstack((0,n.logspace(-3, 4, 1000)))
	xb = (bins[1:]+bins[:-1])/2.
	dx = bins[1:] - bins[:-1]
	X, Y = n.meshgrid(xb,xb)
	N0 = HDF0 /dx  / 1000.**3.
	return N0, bins

cd = lambda z:  co.Planck13.Om(z) * co.Planck13.critical_density(z).to(uu.solMass/uu.megaparsec**3) * CELL**3./ (Mp * (co.Planck13.H(z)/100.)**2.)

n.log10(189619641793.83)

inFiles = n.array(["dmdens_cic_104_DFhist_linearBins.dat", "dmdens_cic_101_DFhist_linearBins.dat", "dmdens_cic_097_DFhist_linearBins.dat", "dmdens_cic_087_DFhist_linearBins.dat"])

N0z07, binsz07 = getNN0_sim(inFiles[0])
bins = binsz07
xb07 = (bins[1:]+bins[:-1])/2. #* 100

N0z08, binsz08 = getNN0_sim(inFiles[1])
bins = binsz08
xb08 = (bins[1:]+bins[:-1])/2. #* 100

N0z15, binsz15 = getNN0_sim(inFiles[3])
bins = binsz15
xb15 = (bins[1:]+bins[:-1])/2.#* 100

dx = bins[1:] - bins[:-1]

dfn = lambda DF, DFs, a, A : n.log10( A * (10**DF/10**DFs)**(-a) *n.e**(-10**DF/10**DFs) )
ok = (N0z07[2:]>0)
xfit = n.log10(xb07[2:][ok])
yfit = n.log10( N0z07[2:][ok] )
out07, cov07 = curve_fit(dfn, xfit, yfit, p0=(3, 2, 1e-6 ), maxfev=80000000)

ok = (N0z15[2:]>0)
xfit = n.log10(xb15[2:][ok])
yfit = n.log10( N0z15[2:][ok])
out15, cov15 = curve_fit(dfn, xfit, yfit, p0=(3, 2, 1e-6 ), maxfev=80000000)

#################################################
#################################################
# delta - probability to have a galaxy relation
#################################################
#################################################


def getNN0_gal(inGalFile, bins):
	hd = fits.open(inGalFile)[1].data
	HDF0, bins = n.histogram(hd['DF'], bins= bins) #n.logspace(-1.5,4,80))
	dx = bins[1:] - bins[:-1]
	N0 = HDF0 /dx / 1000.**3.
	return N0, HDF0

bins = n.hstack((-1,n.arange(0,10,0.1),n.arange(10,100,10),n.arange(100,1000,100),n.arange(1000,10000,1000)))
dx = bins[1:] - bins[:-1]
xb = (bins[1:]+bins[:-1])/2.

inGal = n.array([   "Box_HAM_z0.701838_nbar1.350000e-05_QSO.DF.fits.gz","Box_HAM_z0.818843_nbar1.680000e-05_QSO.DF.fits.gz", "Box_HAM_z1.480160_nbar1.930000e-05_QSO.DF.fits.gz" ])

N0qsoz07, N0qsoz07T = getNN0_gal(join( mockDir,inGal[0]), bins)
N0qsoz08, N0qsoz08T = getNN0_gal(join( mockDir,inGal[1]), bins)
N0qsoz15, N0qsoz15T = getNN0_gal(join( mockDir,inGal[2]), bins)

n.savetxt("DF-MDPL-z07.data", n.transpose([xb07, N0z07]))
n.savetxt("DF-MDPL-z08.data", n.transpose([xb08, N0z08]))
n.savetxt("DF-MDPL-z15.data", n.transpose([xb15, N0z15]))

sys.exit()
p.figure(0)
p.title('QSO')
p.plot(xb07[2:], N0z07[2:],'k', lw=2, rasterized=True, label='z=0.7 all')
p.plot(xb08[2:], N0z08[2:],'b', lw=2, rasterized=True, label='z=0.8 all')
p.plot(xb15[2:], N0z15[2:],'r',lw=2, rasterized=True, label='z=1.5 all')
p.plot(xb, N0qsoz07,'k--', rasterized=True, label='z=0.7 qso')
p.plot(xb, N0qsoz08,'b--', rasterized=True, label='z=0.8 qso')
p.plot(xb, N0qsoz15,'r--', rasterized=True, label='z=1.5 qso')
p.axvline(1/ cd(0.701838).value,label='1 particle per cell',c='m')
p.xlabel(r'density field value')
p.ylabel(r'N[in bin]/bin width/volume')
p.xscale('log')
p.yscale('log')
p.ylim((1e-10, 1e2))
p.xlim((1/ cd(0.701838).value/3., 1e4))
gl = p.legend(loc=1)
gl.set_frame_on(False)
p.grid()
p.savefig(join(mockDir,"plots-lin","evolution-QSO-delta-HDF0_linear.png"))
p.clf()

from scipy.special import erf

hod = lambda logdf, logdfcut, sigmadf, ntot,logdfsat, aa : ntot * (1+erf((logdf-logdfcut)/sigmadf))/2. 
pl = lambda logdf,logdfsat, aa : (10**(logdf-logdfsat))**aa
yfitA = N0qsoz07/N0z07
ok=(yfitA>0)&(xb>60)
yfit=yfitA[ok]
xfit = n.log10(xb[ok])
hod07, cov = curve_fit(pl, xfit, yfit, p0=( 2, 4 ), maxfev=80000000)

p.figure(0)
p.title('QSO')
p.plot(xb, N0qsoz07/N0z07,'k--', rasterized=True, label='z=0.7 qso')
ok=(yfitA>0)&(xb>40)
yfit=yfitA[ok]
xfit = n.log10(xb[ok])
hod07, cov = curve_fit(pl, xfit, yfit, p0=( 2, 4 ), maxfev=80000000)
print hod07
p.plot(10**xfit,pl(xfit, hod07[0], hod07[1]),'m', lw=2,label='z=0.7, DF>40, slope '+str(n.round(hod07[1],2)))
ok=(yfitA>0)&(xb<40)&(xb>2)
yfit=yfitA[ok]
xfit = n.log10(xb[ok])
hod07, cov = curve_fit(pl, xfit, yfit, p0=( 2, 4 ), maxfev=80000000)
print hod07
p.plot(10**xfit,pl(xfit, hod07[0], hod07[1]),'c', lw=2,label='z=0.7, 2<DF<40, slope '+str(n.round(hod07[1],2)))
p.plot(xb, N0qsoz08/N0z08,'b--', rasterized=True, label='z=0.8 qso')
p.plot(xb, N0qsoz15/N0z15,'r--', rasterized=True, label='z=1.5 qso')
p.axvline(1/ cd(0.701838).value,label='1 particle per cell',c='m')
p.xlabel(r'density field value')
p.ylabel(r'Proba to have NQSO in cell')
p.xscale('log')
p.yscale('log')
#p.ylim((1e-10, 1e2))
p.xlim((1/ cd(0.701838).value/3., 1e4))
gl = p.legend(loc=0)
gl.set_frame_on(False)
p.grid()
p.savefig(join(mockDir,"plots-lin","evolution-QSO-delta-HDF0-ratio_linear.png"))
p.clf()

n.savetxt(join(mockDir,"plots-lin","evolution-QSO-delta-HDF0-ratio_linear.DATA"), n.transpose([xb, N0qsoz07/N0z07, N0qsoz08/N0z08, N0qsoz15/N0z15]), header="DFvalue Pqso_z07 Pqso_z08 Pqso_z15")

sys.exit()

p.figure(0)
p.title('QSO')
p.plot(xb, N0qsoz07/N0z07,'kx', rasterized=True, label='z=0.7')
p.plot(xb, N0qsoz08/N0z08,'bx', rasterized=True, label='z=0.8')
p.plot(xb, N0qsoz15/N0z15,'rx', rasterized=True, label='z=1.5')
p.axvline(0.4,label='0.4',c='r')
p.axvline(100,label='100', color='m')
p.xlabel(r'$\delta_0$')
p.ylabel(r'N/ N total')
p.xscale('log')
p.yscale('log')
p.ylim((1e-10 , 1e1))
p.xlim((0.1, 1e4))
gl = p.legend(loc=2)
gl.set_frame_on(False)
p.grid()
p.savefig(join(mockDir,"plots","evolution-QSO-delta-HDF0-ratio.png"))
p.clf()


inGal = n.array([ "Box_HAM_z0.701838_nbar1.000000e-04_LRG.DF.fits.gz", "Box_HAM_z0.818843_nbar1.000000e-04_LRG.DF.fits.gz"])


N0lrgz07, N0lrgz07T = getNN0(join( mockDir,inGal[0]), bins)
N0lrgz08, N0lrgz08T = getNN0(join( mockDir,inGal[1]), bins)

p.figure(0)
p.title('LRG')
p.plot(xb, N0lrgz07/N0z07,'kx', rasterized=True, label='z=0.7')
p.plot(xb, N0lrgz08/N0z08,'bx', rasterized=True, label='z=0.8')
p.axvline(0.4,label='0.4',c='r')
p.axvline(100,label='100', color='m')
p.xlabel(r'$\delta_0$')
p.ylabel(r'N/ N total')
p.xscale('log')
p.yscale('log')
p.ylim((1e-10, 1e1))
p.xlim((0.1, 1e4))
gl = p.legend(loc=2)
gl.set_frame_on(False)
p.grid()
p.savefig(join(mockDir,"plots","evolution-LRG-delta-HDF0-ratio.png"))
p.clf()


p.figure(0)
p.title('LRG')
p.plot(xb, N0z07,'kx', rasterized=True, label='z=0.7 all')
p.plot(xb, N0z08,'bx', rasterized=True, label='z=0.8 all')
p.plot(xb, N0lrgz07,'ko', rasterized=True, label='z=0.7 lrg')
p.plot(xb, N0lrgz08,'bo', rasterized=True, label='z=0.8 lrg')
p.axvline(0.4,label='0.4',c='r')
p.axvline(100,label='100', color='m')
p.xlabel(r'$\delta_0$')
p.ylabel(r'N')
p.xscale('log')
p.yscale('log')
p.ylim((1e-10, 1e1))
p.xlim((0.1, 1e4))
gl = p.legend(loc=2)
gl.set_frame_on(False)
p.grid()
p.savefig(join(mockDir,"plots","evolution-LRG-delta-HDF0.png"))
p.clf()


inGal = n.array([ "Box_HAM_z0.701838_nbar2.400000e-04_ELG.DF.fits.gz" , "Box_HAM_z0.818843_nbar3.200000e-04_ELG.DF.fits.gz" ])

N0elgz07, N0elgz07T = getNN0(join( mockDir,inGal[0]), bins)
N0elgz08, N0elgz08T = getNN0(join( mockDir,inGal[1]), bins)


p.figure(0)
p.title('ELG')
p.plot(xb, N0elgz07/N0z07,'kx', rasterized=True, label='z=0.7')
#p.plot(xb, N0elgz08/N0z08,'bx', rasterized=True, label='z=0.8')
#p.plot(xb[xb>1e2], 10**fun(n.log10(xb[xb>1e2]), prs[0],prs[1],prs[2]), 'r--', lw = 2, label='')
#p.plot(xb[xb<10**1.2], 10**fun(n.log10(xb[xb<10**1.2]), prsL[0],prsL[1],prsL[2]), 'r--', lw = 2)
#p.plot(xb, 10**n.polyval(ps, n.log10(xb)), 'm--', lw=2)
p.xlabel(r'$\delta_0$')
p.ylabel(r'N / N total')
p.xscale('log')
p.yscale('log')
p.ylim((1e-10, 1e1))
p.xlim((0.1, 1e4))
gl = p.legend(loc=2)
gl.set_frame_on(False)
p.grid()
p.savefig(join(mockDir,"plots","evolution-ELG-delta-HDF0-ratio.png"))
p.clf()


p.figure(0)
p.title('ELG')
p.plot(xb, N0elgz07,'ko', rasterized=True, label='z=0.7 elg')
p.plot(xb, N0elgz08,'bo', rasterized=True, label='z=0.8 elg')
p.plot(xb, N0z07,'kx', rasterized=True, label='z=0.7 all')
p.plot(xb, N0z08,'bx', rasterized=True, label='z=0.8 all')
p.axvline(0.4,label='0.4',c='r')
p.axvline(100,label='100', color='m')
p.xlabel(r'$\delta_0$')
p.ylabel(r'N')
p.xscale('log')
p.yscale('log')
p.ylim((1e-10, 1e1))
p.xlim((0.1, 1e4))
gl = p.legend(loc=2)
gl.set_frame_on(False)
p.grid()
p.savefig(join(mockDir,"plots","evolution-ELG-delta-HDF0.png"))
p.clf()


########## FIT z=1.5 QSO

NR = 5
N0z15R = n.array([N0z15[ii::NR] for ii in range(NR)]).sum(axis=0)
binsz15R = binsz15[::NR]

N0qsoz15R = n.array([N0qsoz15[ii::NR] for ii in range(NR)]).sum(axis=0)
N0qsoz15R_sig = n.array([N0qsoz15[ii::NR] for ii in range(NR)]).std(axis=0)

xbR = (binsz15R[1:]+binsz15R[:-1])/2.
dxR = binsz15R[1:] - binsz15R[:-1]

# relative error on y in percentage
errPoisson = N0qsoz15T**(-0.5)
errorsP = interp1d(xb, errPoisson) 
# absolute error on y 
errPoissonA = N0qsoz15T**(0.5)
errorsPA = interp1d(xb, errPoissonA) 

errors = interp1d(xbR, N0qsoz15R_sig)

ok = (N0qsoz15>0)&(N0z15>0)&(N0qsoz15/N0z15>-6)#&(xb>10**2)
y = n.log10(N0qsoz15[ok]/N0z15[ok])
yplus = n.log10((N0qsoz15[ok] + errorsP(xb[ok])*N0qsoz15[ok] )/N0z15[ok])
yminus = n.log10((N0qsoz15[ok] - errorsP(xb[ok])*N0qsoz15[ok] )/N0z15[ok])
x = n.log10(xb[ok])
yerr = errorsP(10**x)  * y
ps = n.polyfit(x, y, 11, w = 1./(errPoisson[ok]))

p.figure(0)
p.title('QSO ')#+str(ps))
p.plot(xb, N0qsoz15/N0z15,'kx', rasterized=True, label='z=1.5')
p.plot(xb, 10**n.polyval(ps, n.log10(xb)), 'm--', lw=2,label='fit')
p.xlabel(r'$\delta_0$')
p.ylabel(r'N / N total')
p.xscale('log')
p.yscale('log')
p.ylim((1e-10, 1e1))
p.xlim((0.1, 1e4))
gl = p.legend(loc=2)
gl.set_frame_on(False)
p.grid()
p.savefig(join(mockDir,"plots","fit-QSO-z15-delta-HDF0-model.png"))
p.clf()


p.figure(0)
p.title('QSO')#+str(n.round(ps,5)))
p.plot(xb, (N0qsoz15/N0z15)/(10**n.polyval(ps, n.log10(xb))),'kx', rasterized=True, label='z=1.5')
p.plot(xb,1+errPoisson, 'r--')
p.plot(xb,1-errPoisson, 'r--')
p.plot(10**x, 10**(yplus-y), 'r--')
p.plot(10**x, 10**(-yminus+y), 'r--',label='poisson error')
p.xlabel(r'$\delta_0$')
p.ylabel(r'N / N model')
p.xscale('log')
p.ylim((0.5, 1.5))
p.xlim((0.1, 1e4))
gl = p.legend(loc=2)
gl.set_frame_on(False)
p.grid()
p.savefig(join(mockDir,"plots","fit-QSO-z15-delta-HDF0-ratio.png"))
p.clf()

n.savetxt("fit-polynomial-QSO-z15.data",ps)


########## FIT z=0.8 LRG

NR = 5
N0z08R = n.array([N0z08[ii::NR] for ii in range(NR)]).sum(axis=0)
binsz08R = binsz08[::NR]

N0lrgz08R = n.array([N0lrgz08[ii::NR] for ii in range(NR)]).sum(axis=0)
N0lrgz08R_sig = n.array([N0lrgz08[ii::NR] for ii in range(NR)]).std(axis=0)

xbR = (binsz08R[1:]+binsz08R[:-1])/2.
dxR = binsz08R[1:] - binsz08R[:-1]

# relative error on y in percentage
errPoisson = N0lrgz08T**(-0.5)
errorsP = interp1d(xb, errPoisson) 
# absolute error on y 
errPoissonA = N0lrgz08T**(0.5)
errorsPA = interp1d(xb, errPoissonA) 

errors = interp1d(xbR, N0lrgz08R_sig)

ok = (N0lrgz08>0)&(N0z08>0)&(N0lrgz08/N0z08>-6)#&(xb>10**2)
y = n.log10(N0lrgz08[ok]/N0z08[ok])
yplus = n.log10((N0lrgz08[ok] + errorsP(xb[ok])*N0lrgz08[ok] )/N0z08[ok])
yminus = n.log10((N0lrgz08[ok] - errorsP(xb[ok])*N0lrgz08[ok] )/N0z08[ok])
x = n.log10(xb[ok])
yerr = errorsP(10**x)  * y
ps = n.polyfit(x, y, 11, w = 1./(errPoisson[ok]))

p.figure(0)
p.title('LRG ')#+str(ps))
p.plot(xb, N0lrgz08/N0z08,'kx', rasterized=True, label='z=0.8')
p.plot(xb, 10**n.polyval(ps, n.log10(xb)), 'm--', lw=2, label='fit')
p.xlabel(r'$\delta_0$')
p.ylabel(r'N / N total')
p.xscale('log')
p.yscale('log')
p.ylim((1e-10, 1e1))
p.xlim((0.1, 1e4))
gl = p.legend(loc=2)
gl.set_frame_on(False)
p.grid()
p.savefig(join(mockDir,"plots","fit-LRG-z08-delta-HDF0-model.png"))
p.clf()


p.figure(0)
p.title('LRG')#+str(n.round(ps,5)))
p.plot(xb, (N0lrgz08/N0z08)/(10**n.polyval(ps, n.log10(xb))),'kx', rasterized=True, label='z=0.8')
p.plot(xb,1+errPoisson, 'r--')
p.plot(xb,1-errPoisson, 'r--')
p.plot(10**x, 10**(yplus-y), 'r--')
p.plot(10**x, 10**(-yminus+y), 'r--',label='poisson error')
p.xlabel(r'$\delta_0$')
p.ylabel(r'N / N model')
p.xscale('log')
p.ylim((0.5, 1.5))
p.xlim((0.1, 1e4))
gl = p.legend(loc=2)
gl.set_frame_on(False)
p.grid()
p.savefig(join(mockDir,"plots","fit-LRG-z08-delta-HDF0-ratio.png"))
p.clf()

n.savetxt("fit-polynomial-LRG-z08.data",ps)

########## FIT z=0.8 QSO

NR = 5
N0z08R = n.array([N0z08[ii::NR] for ii in range(NR)]).sum(axis=0)
binsz08R = binsz08[::NR]

N0qsoz08R = n.array([N0qsoz08[ii::NR] for ii in range(NR)]).sum(axis=0)
N0qsoz08R_sig = n.array([N0qsoz08[ii::NR] for ii in range(NR)]).std(axis=0)

xbR = (binsz08R[1:]+binsz08R[:-1])/2.
dxR = binsz08R[1:] - binsz08R[:-1]

# relative error on y in percentage
errPoisson = N0qsoz08T**(-0.5)
errorsP = interp1d(xb, errPoisson) 
# absolute error on y 
errPoissonA = N0qsoz08T**(0.5)
errorsPA = interp1d(xb, errPoissonA) 

errors = interp1d(xbR, N0qsoz08R_sig)

ok = (N0qsoz08>0)&(N0z08>0)&(N0qsoz08/N0z08>-6)#&(xb>10**2)
y = n.log10(N0qsoz08[ok]/N0z08[ok])
yplus = n.log10((N0qsoz08[ok] + errorsP(xb[ok])*N0qsoz08[ok] )/N0z08[ok])
yminus = n.log10((N0qsoz08[ok] - errorsP(xb[ok])*N0qsoz08[ok] )/N0z08[ok])
x = n.log10(xb[ok])
yerr = errorsP(10**x)  * y
ps = n.polyfit(x, y, 11, w = 1./(errPoisson[ok]))

p.figure(0)
p.title('QSO ')#+str(ps))
p.plot(xb, N0qsoz08/N0z08,'kx', rasterized=True, label='z=0.8')
p.plot(xb, 10**n.polyval(ps, n.log10(xb)), 'm--', lw=2,label='fit')
p.xlabel(r'$\delta_0$')
p.ylabel(r'N / N total')
p.xscale('log')
p.yscale('log')
p.ylim((1e-10, 1e1))
p.xlim((0.1, 1e4))
gl = p.legend(loc=2)
gl.set_frame_on(False)
p.grid()
p.savefig(join(mockDir,"plots","fit-QSO-z08-delta-HDF0-model.png"))
p.clf()


p.figure(0)
p.title('QSO')#+str(n.round(ps,5)))
p.plot(xb, (N0qsoz08/N0z08)/(10**n.polyval(ps, n.log10(xb))),'kx', rasterized=True, label='z=0.8')
p.plot(xb,1+errPoisson, 'r--')
p.plot(xb,1-errPoisson, 'r--')
p.plot(10**x, 10**(yplus-y), 'r--')
p.plot(10**x, 10**(-yminus+y), 'r--',label='poisson error')
p.xlabel(r'$\delta_0$')
p.ylabel(r'N / N model')
p.xscale('log')
p.ylim((0.5, 1.5))
p.xlim((0.1, 1e4))
gl = p.legend(loc=2)
gl.set_frame_on(False)
p.grid()
p.savefig(join(mockDir,"plots","fit-QSO-z08-delta-HDF0-ratio.png"))
p.clf()

n.savetxt("fit-polynomial-QSO-z08.data",ps)


########## FIT z=0.8 ELG

NR = 5
N0z08R = n.array([N0z08[ii::NR] for ii in range(NR)]).sum(axis=0)
binsz08R = binsz08[::NR]

N0elgz08R = n.array([N0elgz08[ii::NR] for ii in range(NR)]).sum(axis=0)
N0elgz08R_sig = n.array([N0elgz08[ii::NR] for ii in range(NR)]).std(axis=0)

xbR = (binsz08R[1:]+binsz08R[:-1])/2.
dxR = binsz08R[1:] - binsz08R[:-1]

# relative error on y in percentage
errPoisson = N0elgz08T**(-0.5)
errorsP = interp1d(xb, errPoisson) 
# absolute error on y 
errPoissonA = N0elgz08T**(0.5)
errorsPA = interp1d(xb, errPoissonA) 

errors = interp1d(xbR, N0elgz08R_sig)

ok = (N0elgz08>0)&(N0z08>0)&(N0elgz08/N0z08>-6)#&(xb>10**2)
y = n.log10(N0elgz08[ok]/N0z08[ok])
yplus = n.log10((N0elgz08[ok] + errorsP(xb[ok])*N0elgz08[ok] )/N0z08[ok])
yminus = n.log10((N0elgz08[ok] - errorsP(xb[ok])*N0elgz08[ok] )/N0z08[ok])
x = n.log10(xb[ok])
yerr = errorsP(10**x)  * y
ps = n.polyfit(x, y, 11, w = 1./(errPoisson[ok]))

p.figure(0)
p.title('ELG ')#+str(ps))
p.plot(xb, N0elgz08/N0z08,'kx', rasterized=True, label='z=0.8')
p.plot(xb, 10**n.polyval(ps, n.log10(xb)), 'm--', lw=2,label='fit')
p.xlabel(r'$\delta_0$')
p.ylabel(r'N / N total')
p.xscale('log')
p.yscale('log')
p.ylim((1e-10, 1e1))
p.xlim((0.1, 1e4))
gl = p.legend(loc=2)
gl.set_frame_on(False)
p.grid()
p.savefig(join(mockDir,"plots","fit-ELG-z08-delta-HDF0-model.png"))
p.clf()


p.figure(0)
p.title('ELG')#+str(n.round(ps,5)))
p.plot(xb, (N0elgz08/N0z08)/(10**n.polyval(ps, n.log10(xb))),'kx', rasterized=True, label='z=0.8')
p.plot(xb,1+errPoisson, 'r--')
p.plot(xb,1-errPoisson, 'r--')
p.plot(10**x, 10**(yplus-y), 'r--')
p.plot(10**x, 10**(-yminus+y), 'r--',label='poisson error')
p.xlabel(r'$\delta_0$')
p.ylabel(r'N / N model')
p.xscale('log')
p.ylim((0.5, 1.5))
p.xlim((0.1, 1e4))
gl = p.legend(loc=2)
gl.set_frame_on(False)
p.grid()
p.savefig(join(mockDir,"plots","fit-ELG-z08-delta-HDF0-ratio.png"))
p.clf()

n.savetxt("fit-polynomial-ELG-z08.data",ps)

sys.exit()

########## FIT z=0.7 LRG

NR = 5
N0z07R = n.array([N0z07[ii::NR] for ii in range(NR)]).sum(axis=0)
binsz07R = binsz07[::NR]

N0lrgz07R = n.array([N0lrgz07[ii::NR] for ii in range(NR)]).sum(axis=0)
N0lrgz07R_sig = n.array([N0lrgz07[ii::NR] for ii in range(NR)]).std(axis=0)

xbR = (binsz07R[1:]+binsz07R[:-1])/2.
dxR = binsz07R[1:] - binsz07R[:-1]

# relative error on y in percentage
errPoisson = N0lrgz07T**(-0.5)
errorsP = interp1d(xb, errPoisson) 
# absolute error on y 
errPoissonA = N0lrgz07T**(0.5)
errorsPA = interp1d(xb, errPoissonA) 

errors = interp1d(xbR, N0lrgz07R_sig)

ok = (N0lrgz07>0)&(N0z07>0)&(N0lrgz07/N0z07>-6)#&(xb>10**2)
y = n.log10(N0lrgz07[ok]/N0z07[ok])
yplus = n.log10((N0lrgz07[ok] + errorsP(xb[ok])*N0lrgz07[ok] )/N0z07[ok])
yminus = n.log10((N0lrgz07[ok] - errorsP(xb[ok])*N0lrgz07[ok] )/N0z07[ok])
x = n.log10(xb[ok])
yerr = errorsP(10**x)  * y
ps = n.polyfit(x, y, 11, w = 1./(errPoisson[ok]))

p.figure(0)
p.title('LRG ')#+str(ps))
p.plot(xb, N0lrgz07/N0z07,'kx', rasterized=True, label='z=0.7')
p.plot(xb, 10**n.polyval(ps, n.log10(xb)), 'm--', lw=2, label='fit')
p.xlabel(r'$\delta_0$')
p.ylabel(r'N / N total')
p.xscale('log')
p.yscale('log')
p.ylim((1e-10, 1e1))
p.xlim((0.1, 1e4))
gl = p.legend(loc=2)
gl.set_frame_on(False)
p.grid()
p.savefig(join(mockDir,"plots","fit-LRG-z07-delta-HDF0-model.png"))
p.clf()


p.figure(0)
p.title('LRG')#+str(n.round(ps,5)))
p.plot(xb, (N0lrgz07/N0z07)/(10**n.polyval(ps, n.log10(xb))),'kx', rasterized=True, label='z=0.7')
p.plot(xb,1+errPoisson, 'r--')
p.plot(xb,1-errPoisson, 'r--')
p.plot(10**x, 10**(yplus-y), 'r--')
p.plot(10**x, 10**(-yminus+y), 'r--',label='poisson error')
p.xlabel(r'$\delta_0$')
p.ylabel(r'N / N model')
p.xscale('log')
p.ylim((0.5, 1.5))
p.xlim((0.1, 1e4))
gl = p.legend(loc=2)
gl.set_frame_on(False)
p.grid()
p.savefig(join(mockDir,"plots","fit-LRG-z07-delta-HDF0-ratio.png"))
p.clf()

n.savetxt("fit-polynomial-LRG-z07.data",ps)

########## FIT z=0.7 QSO

NR = 5
N0z07R = n.array([N0z07[ii::NR] for ii in range(NR)]).sum(axis=0)
binsz07R = binsz07[::NR]

N0qsoz07R = n.array([N0qsoz07[ii::NR] for ii in range(NR)]).sum(axis=0)
N0qsoz07R_sig = n.array([N0qsoz07[ii::NR] for ii in range(NR)]).std(axis=0)

xbR = (binsz07R[1:]+binsz07R[:-1])/2.
dxR = binsz07R[1:] - binsz07R[:-1]

# relative error on y in percentage
errPoisson = N0qsoz07T**(-0.5)
errorsP = interp1d(xb, errPoisson) 
# absolute error on y 
errPoissonA = N0qsoz07T**(0.5)
errorsPA = interp1d(xb, errPoissonA) 

errors = interp1d(xbR, N0qsoz07R_sig)

ok = (N0qsoz07>0)&(N0z07>0)&(N0qsoz07/N0z07>-6)#&(xb>10**2)
y = n.log10(N0qsoz07[ok]/N0z07[ok])
yplus = n.log10((N0qsoz07[ok] + errorsP(xb[ok])*N0qsoz07[ok] )/N0z07[ok])
yminus = n.log10((N0qsoz07[ok] - errorsP(xb[ok])*N0qsoz07[ok] )/N0z07[ok])
x = n.log10(xb[ok])
yerr = errorsP(10**x)  * y
ps = n.polyfit(x, y, 11, w = 1./(errPoisson[ok]))

p.figure(0)
p.title('QSO ')#+str(ps))
p.plot(xb, N0qsoz07/N0z07,'kx', rasterized=True, label='z=0.7')
p.plot(xb, 10**n.polyval(ps, n.log10(xb)), 'm--', lw=2,label='fit')
p.xlabel(r'$\delta_0$')
p.ylabel(r'N / N total')
p.xscale('log')
p.yscale('log')
p.ylim((1e-10, 1e1))
p.xlim((0.1, 1e4))
gl = p.legend(loc=2)
gl.set_frame_on(False)
p.grid()
p.savefig(join(mockDir,"plots","fit-QSO-z07-delta-HDF0-model.png"))
p.clf()


p.figure(0)
p.title('QSO')#+str(n.round(ps,5)))
p.plot(xb, (N0qsoz07/N0z07)/(10**n.polyval(ps, n.log10(xb))),'kx', rasterized=True, label='z=0.7')
p.plot(xb,1+errPoisson, 'r--')
p.plot(xb,1-errPoisson, 'r--')
p.plot(10**x, 10**(yplus-y), 'r--')
p.plot(10**x, 10**(-yminus+y), 'r--',label='poisson error')
p.xlabel(r'$\delta_0$')
p.ylabel(r'N / N model')
p.xscale('log')
p.ylim((0.5, 1.5))
p.xlim((0.1, 1e4))
gl = p.legend(loc=2)
gl.set_frame_on(False)
p.grid()
p.savefig(join(mockDir,"plots","fit-QSO-z07-delta-HDF0-ratio.png"))
p.clf()

n.savetxt("fit-polynomial-QSO-z07.data",ps)


########## FIT z=0.7 ELG

NR = 5
N0z07R = n.array([N0z07[ii::NR] for ii in range(NR)]).sum(axis=0)
binsz07R = binsz07[::NR]

N0elgz07R = n.array([N0elgz07[ii::NR] for ii in range(NR)]).sum(axis=0)
N0elgz07R_sig = n.array([N0elgz07[ii::NR] for ii in range(NR)]).std(axis=0)

xbR = (binsz07R[1:]+binsz07R[:-1])/2.
dxR = binsz07R[1:] - binsz07R[:-1]

# relative error on y in percentage
errPoisson = N0elgz07T**(-0.5)
errorsP = interp1d(xb, errPoisson) 
# absolute error on y 
errPoissonA = N0elgz07T**(0.5)
errorsPA = interp1d(xb, errPoissonA) 

errors = interp1d(xbR, N0elgz07R_sig)

ok = (N0elgz07>0)&(N0z07>0)&(N0elgz07/N0z07>-6)#&(xb>10**2)
y = n.log10(N0elgz07[ok]/N0z07[ok])
yplus = n.log10((N0elgz07[ok] + errorsP(xb[ok])*N0elgz07[ok] )/N0z07[ok])
yminus = n.log10((N0elgz07[ok] - errorsP(xb[ok])*N0elgz07[ok] )/N0z07[ok])
x = n.log10(xb[ok])
yerr = errorsP(10**x)  * y
ps = n.polyfit(x, y, 11, w = 1./(errPoisson[ok]))

p.figure(0)
p.title('ELG ')#+str(ps))
p.plot(xb, N0elgz07/N0z07,'kx', rasterized=True, label='z=0.7')
p.plot(xb, 10**n.polyval(ps, n.log10(xb)), 'm--', lw=2,label='fit')
p.xlabel(r'$\delta_0$')
p.ylabel(r'N / N total')
p.xscale('log')
p.yscale('log')
p.ylim((1e-10, 1e1))
p.xlim((0.1, 1e4))
gl = p.legend(loc=2)
gl.set_frame_on(False)
p.grid()
p.savefig(join(mockDir,"plots","fit-ELG-z07-delta-HDF0-model.png"))
p.clf()


p.figure(0)
p.title('ELG')#+str(n.round(ps,5)))
p.plot(xb, (N0elgz07/N0z07)/(10**n.polyval(ps, n.log10(xb))),'kx', rasterized=True, label='z=0.7')
p.plot(xb,1+errPoisson, 'r--')
p.plot(xb,1-errPoisson, 'r--')
p.plot(10**x, 10**(yplus-y), 'r--')
p.plot(10**x, 10**(-yminus+y), 'r--',label='poisson error')
p.xlabel(r'$\delta_0$')
p.ylabel(r'N / N model')
p.xscale('log')
p.ylim((0.5, 1.5))
p.xlim((0.1, 1e4))
gl = p.legend(loc=2)
gl.set_frame_on(False)
p.grid()
p.savefig(join(mockDir,"plots","fit-ELG-z07-delta-HDF0-ratio.png"))
p.clf()

n.savetxt("fit-polynomial-ELG-z07.data",ps)

sys.exit()

















































































#########################################
#########################################
#########################################
#Z=0.8
#########################################
#########################################
#########################################


#########################################
#########################################
#########################################
#Z=0.8
#########################################
#########################################
#########################################

inGal = n.array([  "Box_HAM_z1.480160_nbar1.930000e-05_QSO.DF.fits.gz" ])

inGal = n.array([  "Box_HAM_z0.818843_nbar1.680000e-05_QSO.DF.fits.gz", "Box_HAM_z0.818843_nbar3.200000e-04_ELG.DF.fits.gz" ])

Hqso, N0qso, N1qso = getNN(join( mockDir,inGal[0]))
Helg, N0elg, N1elg = getNN(join( mockDir,inGal[1]))

xs, Hs = smooth(H)		
xs, Hselg = smooth(Helg)		
xs, Hsqso = smooth(Hqso)		
X, Y = n.meshgrid(xb[::4], xb[::4]) #xs,xs)
n.savetxt(join(mockDir,"grid-x-z08.data"), X)
n.savetxt(join(mockDir,"grid-y-z08.data"), Y)

Z = Hsqso.astype('float')/Hs
bad = (Z<0)|(n.isnan(Z))|(Z==n.inf)
Z[bad]=n.zeros_like(Z)[bad]
n.savetxt(join(mockDir,"qso-z08.data"), Z)

Z = Hselg.astype('float')/Hs
bad = (Z<0)|(n.isnan(Z))|(Z==n.inf)
Z[bad]=n.zeros_like(Z)[bad]
n.savetxt(join(mockDir,"elg-z08.data"), Z)

Z=n.log10(Hsqso.astype('float')/Hs)
p.figure(1, figsize=(8, 8))
p.contourf(X, Y, Z)#, levels=n.arange(-3,0.26,0.25))
cb = p.colorbar()
cb.set_label(r'log(N(QSO)/N(all))')
p.xlabel(r'$\delta_1$')
p.ylabel(r'$\delta_0$')
p.ylim((0.1, 5000))
p.xlim((0.1, 5000))
p.xscale('log')
p.yscale('log')
p.grid()
p.savefig(join(mockDir,"plots","delta-HDF0-HDF1-z08-qso.png"))
p.clf()

Z=n.log10(Hselg.astype('float')/Hs)
p.figure(1, figsize=(8, 8))
p.contourf(X, Y, Z)#, levels=n.arange(-3,0.26,0.25))
cb = p.colorbar()
cb.set_label(r'log(N(ELG)/N(all)')
p.xlabel(r'$\delta_1$')
p.ylabel(r'$\delta_0$')
p.ylim((0.1, 5000))
p.xlim((0.1, 5000))
p.xscale('log')
p.yscale('log')
p.grid()
p.savefig(join(mockDir,"plots","delta-HDF0-HDF1-z08-elg.png"))
p.clf()

p.figure(0)
p.title('z=0.7')
p.plot(xb, N0qso/N0,'gx', rasterized=True, label='QSO ')
p.plot(xb, N0elg/N0,'bx', rasterized=True, label='ELG ')
p.plot(xb, 5e-6 * xb**(2.1), 'k--' , label=r'$5\times10^{-6}\delta_0^2.1$')
p.axvline(0.4,label='0.4',c='r')
p.axvline(100,label='100', color='m')
p.xlabel(r'$\delta_0$')
p.ylabel(r'N/ N total')
p.xscale('log')
p.yscale('log')
p.ylim((1e-8, 1e1))
p.xlim((0.01, 1e4))
gl = p.legend(loc=2)
gl.set_frame_on(False)
p.grid()
p.savefig(join(mockDir,"plots","delta-HDF0-z08-ratio.png"))
p.clf()

p.figure(0)
p.title('z=0.7')
p.plot(xb, N1qso/N1,'gx', rasterized=True, label='QSO ')
p.plot(xb, N1elg/N1,'bx', rasterized=True, label='ELG ')
p.plot(xb, 5e-6 * xb**(2.1), 'k--' , label=r'$5\times10^{-6}\delta_0^2.1$')
p.axvline(0.4,label='0.4',c='r')
p.axvline(100,label='100', color='m')
p.xlabel(r'$\delta_1$')
p.ylabel(r'N/ N total')
p.xscale('log')
p.yscale('log')
p.ylim((1e-8, 1e1))
p.xlim((0.01, 1e4))
gl = p.legend(loc=2)
gl.set_frame_on(False)
p.grid()
p.savefig(join(mockDir,"plots","delta-HDF1-z08-ratio.png"))
p.clf()


p.figure(0)
p.title('z=0.7')
p.plot(xb, N0,'kx', rasterized=True, label=r'MDPL 2048$^3$')
p.plot(xb, N0qso,'gx', rasterized=True, label='QSO ')
p.plot(xb, N0elg,'bx', rasterized=True, label='ELG ')
p.axvline(0.4,label='0.4',c='r')
p.axvline(100,label='100', color='m')
p.xlabel(r'$\delta_0$')
p.ylabel(r'$N/Mpc3/d\delta$')
p.xscale('log')
p.yscale('log')
p.ylim((1e-11, 1e2))
p.xlim((0.01, 1e4))
gl = p.legend()
gl.set_frame_on(False)
p.grid()
p.savefig(join(mockDir,"plots","delta-HDF0-z08.png"))
p.clf()

p.figure(0)
p.title('z=0.7')
p.plot(xb, N1,'kx', rasterized=True, label=r'MDPL 2048$^3$')
p.plot(xb, N1qso,'gx', rasterized=True, label='QSO ')
p.plot(xb, N1elg,'bx', rasterized=True, label='ELG ')
p.axvline(0.4,label='0.4',c='r')
p.axvline(100,label='100', color='m')
p.xlabel(r'$\delta_1$')
p.ylabel(r'$N/Mpc3/d\delta$')
p.xscale('log')
p.yscale('log')
p.ylim((1e-11, 1e2))
p.xlim((0.01, 1e4))
gl = p.legend()
gl.set_frame_on(False)
p.grid()
p.savefig(join(mockDir,"plots","delta-HDF1-z08.png"))
p.clf()

#########################################
#########################################
#########################################
#Z=0.7
#########################################
#########################################
#########################################
inGal = n.array([ "Box_HAM_z0.818843_nbar1.000000e-04_LRG.DF.fits.gz", "Box_HAM_z0.818843_nbar1.680000e-05_QSO.DF.fits.gz", "Box_HAM_z0.818843_nbar3.200000e-04_ELG.DF.fits.gz" ])

Hlrg, N0lrg, N1lrg = getNN(join( mockDir,inGal[0]))
Hqso, N0qso, N1qso = getNN(join( mockDir,inGal[1]))
Helg, N0elg, N1elg = getNN(join( mockDir,inGal[2]))

xs, Hs = smooth(H)		
xs, Hslrg = smooth(Hlrg)		
xs, Hselg = smooth(Helg)		
xs, Hsqso = smooth(Hqso)		
X, Y = n.meshgrid(xb[::4], xb[::4]) #xs,xs)
n.savetxt(join(mockDir,"grid-x-z07.data"), X)
n.savetxt(join(mockDir,"grid-y-z07.data"), Y)

Z = Hsqso.astype('float')/Hs
bad = (Z<0)|(n.isnan(Z))|(Z==n.inf)
Z[bad]=n.zeros_like(Z)[bad]
n.savetxt(join(mockDir,"qso-z07.data"), Z)

Z = Hslrg.astype('float')/Hs
bad = (Z<0)|(n.isnan(Z))|(Z==n.inf)
Z[bad]=n.zeros_like(Z)[bad]
n.savetxt(join(mockDir,"lrg-z07.data"), Z)

Z = Hselg.astype('float')/Hs
bad = (Z<0)|(n.isnan(Z))|(Z==n.inf)
Z[bad]=n.zeros_like(Z)[bad]
n.savetxt(join(mockDir,"elg-z07.data"), Z)

Z=n.log10(Hsqso.astype('float')/Hs)
p.figure(1, figsize=(8, 8))
p.contourf(X, Y, Z)#, levels=n.arange(-3,0.26,0.25))
cb = p.colorbar()
cb.set_label(r'log(N(QSO)/N(all))')
p.xlabel(r'$\delta_1$')
p.ylabel(r'$\delta_0$')
p.ylim((0.1, 5000))
p.xlim((0.1, 5000))
p.xscale('log')
p.yscale('log')
p.grid()
p.savefig(join(mockDir,"plots","delta-HDF0-HDF1-z07-qso.png"))
p.clf()

Z=n.log10(Hselg.astype('float')/Hs)
p.figure(1, figsize=(8, 8))
p.contourf(X, Y, Z)#, levels=n.arange(-3,0.26,0.25))
cb = p.colorbar()
cb.set_label(r'log(N(ELG)/N(all)')
p.xlabel(r'$\delta_1$')
p.ylabel(r'$\delta_0$')
p.ylim((0.1, 5000))
p.xlim((0.1, 5000))
p.xscale('log')
p.yscale('log')
p.grid()
p.savefig(join(mockDir,"plots","delta-HDF0-HDF1-z07-elg.png"))
p.clf()

Z=n.log10(Hslrg.astype('float')/Hs)
p.figure(1, figsize=(8, 8))
p.contourf(X, Y, Z)#, levels=n.arange(-3,0.26,0.25))
cb = p.colorbar()
cb.set_label(r'log(N(LRG)/N(all)')
p.xlabel(r'$\delta_1$')
p.ylabel(r'$\delta_0$')
p.ylim((0.1, 5000))
p.xlim((0.1, 5000))
p.xscale('log')
p.yscale('log')
p.grid()
p.savefig(join(mockDir,"plots","delta-HDF0-HDF1-z07-lrg.png"))
p.clf()

p.figure(0)
p.title('z=0.7')
p.plot(xb, N0qso/N0,'gx', rasterized=True, label='QSO ')
p.plot(xb, N0lrg/N0,'rx', rasterized=True, label='LRG ')
p.plot(xb, N0elg/N0,'bx', rasterized=True, label='ELG ')
p.plot(xb, 5e-6 * xb**(2.1), 'k--' , label=r'$5\times10^{-6}\delta_0^2.1$')
p.axvline(0.4,label='0.4',c='r')
p.axvline(100,label='100', color='m')
p.xlabel(r'$\delta_0$')
p.ylabel(r'N/ N total')
p.xscale('log')
p.yscale('log')
p.ylim((1e-8, 1e1))
p.xlim((0.01, 1e4))
gl = p.legend(loc=2)
gl.set_frame_on(False)
p.grid()
p.savefig(join(mockDir,"plots","delta-HDF0-z07-ratio.png"))
p.clf()

p.figure(0)
p.title('z=0.7')
p.plot(xb, N1qso/N1,'gx', rasterized=True, label='QSO ')
p.plot(xb, N1lrg/N1,'rx', rasterized=True, label='LRG ')
p.plot(xb, N1elg/N1,'bx', rasterized=True, label='ELG ')
p.plot(xb, 5e-6 * xb**(2.1), 'k--' , label=r'$5\times10^{-6}\delta_0^2.1$')
p.axvline(0.4,label='0.4',c='r')
p.axvline(100,label='100', color='m')
p.xlabel(r'$\delta_1$')
p.ylabel(r'N/ N total')
p.xscale('log')
p.yscale('log')
p.ylim((1e-8, 1e1))
p.xlim((0.01, 1e4))
gl = p.legend(loc=2)
gl.set_frame_on(False)
p.grid()
p.savefig(join(mockDir,"plots","delta-HDF1-z07-ratio.png"))
p.clf()


p.figure(0)
p.title('z=0.7')
p.plot(xb, N0,'kx', rasterized=True, label=r'MDPL 2048$^3$')
p.plot(xb, N0qso,'gx', rasterized=True, label='QSO ')
p.plot(xb, N0lrg,'rx', rasterized=True, label='LRG ')
p.plot(xb, N0elg,'bx', rasterized=True, label='ELG ')
p.axvline(0.4,label='0.4',c='r')
p.axvline(100,label='100', color='m')
p.xlabel(r'$\delta_0$')
p.ylabel(r'$N/Mpc3/d\delta$')
p.xscale('log')
p.yscale('log')
p.ylim((1e-11, 1e2))
p.xlim((0.01, 1e4))
gl = p.legend()
gl.set_frame_on(False)
p.grid()
p.savefig(join(mockDir,"plots","delta-HDF0-z07.png"))
p.clf()

p.figure(0)
p.title('z=0.7')
p.plot(xb, N1,'kx', rasterized=True, label=r'MDPL 2048$^3$')
p.plot(xb, N1qso,'gx', rasterized=True, label='QSO ')
p.plot(xb, N1lrg,'rx', rasterized=True, label='LRG ')
p.plot(xb, N1elg,'bx', rasterized=True, label='ELG ')
p.axvline(0.4,label='0.4',c='r')
p.axvline(100,label='100', color='m')
p.xlabel(r'$\delta_1$')
p.ylabel(r'$N/Mpc3/d\delta$')
p.xscale('log')
p.yscale('log')
p.ylim((1e-11, 1e2))
p.xlim((0.01, 1e4))
gl = p.legend()
gl.set_frame_on(False)
p.grid()
p.savefig(join(mockDir,"plots","delta-HDF1-z07.png"))
p.clf()

sys.exit()














# definitions for the axes
left, width = 0.1, 0.65
bottom, height = 0.1, 0.65
bottom_h = left_h = left + width + 0.02

rect_scatter = [left, bottom, width, height]
rect_histx = [left, bottom_h, width, 0.2]
rect_histy = [left_h, bottom, 0.2, height]

# start with a rectangular Figure
p.figure(1, figsize=(8, 8))
p.contourf(X, Y, proba)
p.xlabel('DF N1')
p.ylabel('DF')
p.xscale('log')
p.yscale('log')
p.show()

p.figure(1, figsize=(8, 8))
axScatter = p.axes(rect_scatter)
axScatter.set_yscale('log')
axScatter.set_xscale('log')
extent = [yedges[0], yedges[-1], xedges[0], xedges[-1]]
levels = (0.01, 0.1, 0.5, 1)
cset = p.contour(X, Y, proba, levels, origin='lower',colors=['black','green','blue','red'],linewidths=(1.9, 1.6, 1.5, 1.4),extent=extent)
p.clabel(cset, inline=1, fontsize=10, fmt='%1.0i')
for c in cset.collections:
	c.set_linestyle('solid')

p.xlabel('DF N1')
p.ylabel('DF')

axHistx = p.axes(rect_histx)
axHisty = p.axes(rect_histy)
# no labels
axHistx.xaxis.set_major_formatter(nullfmt)
axHisty.yaxis.set_major_formatter(nullfmt)

# the scatter plot:


axHistx.plot(xb, HDF1, 'k')
axHistx.plot(xb, HDF1qso, 'b')
axHistx.set_yscale('log')
axHistx.set_xscale('log')

axHisty.plot(xb, HDF0, 'r', orientation='horizontal')
axHisty.plot(xb, HDF0qso, 'g',  orientation='horizontal')
axHisty.set_yscale('log')


p.show()

p.imshow(n.log10(proba))
p.colorbar()
p.show()

dxAll = binsAll[1:] - binsAll[:-1]
xAll = (binsAll[1:]*binsAll[:-1])**0.5
NAll = result /dxAll / 1000**3.

nqso, binQSO = n.histogram(hd['DF'], bins= n.logspace(-1.5,4,80))
dxQso = binQSO[1:] - binQSO[:-1]
xQSO = (binQSO[1:]*binQSO[:-1])**0.5
NQSO = nqso /dxQso / 1000**3.

p.figure(0)
p.title('z=0.7')
p.plot(xAll, NAll,'kx', rasterized=True, label='MD Planck 1Gpc mesh 2048 cube')
p.plot(xQSO, NQSO,'bx', rasterized=True, label='QSO ')
p.axvline(0.4,label='0.4',c='r')
p.axvline(100,label='100', color='m')
p.xlabel(r'$\delta$')
p.ylabel(r'$N/Mpc3/d\delta$')
p.xscale('log')
p.yscale('log')
p.legend(loc= 3)
p.grid()
p.savefig(join(mockDir,"plots","delta-numberdensity-z07-fit.png"))
p.clf()

#################################################
#################################################
# delta - vmax relation
#################################################
#################################################

# for each bin in delta compute vmax mean and its std
pcs = [0, 1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 99, 100]
bins = n.hstack((0,n.logspace(-3, 4, 60)))
vmaxBar = n.empty(len(bins)-1)
vmaxStd = n.empty(len(bins)-1)
distrib = n.empty((len(bins)-1, len(pcs)))
Nbins = 10
bbs = n.empty((len(bins)-1, Nbins+1))
N = n.empty((len(bins)-1, Nbins))
for ii in range(len(bins)-1):
	sel = (hd['DF']>bins[ii]) & (hd['DF']<bins[ii+1])
	y = hd['Vmax'][sel]
	vmaxBar[ii], vmaxStd[ii], distrib[ii] = n.mean(y), n.std(y), sc(y,pcs)
	N[ii],bbs[ii] = n.histogram(y, bins= Nbins )
	
ok = (vmaxBar>0)&(vmaxStd>0)&(bins[1:]>0.4)&(bins[:-1]<100)&(N.sum(axis=1)>100)
x = n.log10(1.+(bins[1:]*bins[:-1])**0.5)[ok]
y = n.log10(vmaxBar)[ok]
yerr = vmaxStd[ok] / vmaxBar[ok]

f= lambda x,a,b : a*x+b
out, cov = curve_fit(f, x, y, (1,0), yerr )

p.figure(0)
p.plot(n.log10(1+hd['DF']), n.log10(hd['Vmax']),'r.',alpha=0.1, label='QSO z=0.7',rasterized = True)
p.errorbar(x,y,yerr=yerr/2.,label='mean - std')
p.plot(x, f(x,out[0],out[1]),'k--',lw=2,label='fit y='+str(n.round(out[0],3))+'x+'+str(n.round(out[1],3)))
p.xlabel(r'$log_{10}(1+\delta)$')
p.ylabel(r'$log_{10}(V_{max})$')
p.legend(loc= 2)
p.grid()
p.savefig(join(mockDir,"plots","delta-vmax-qso-z07-fit.png"))
p.clf()

#log10(vmax) = 0.0973259*log10(1+delta) + 2.254723554

params = n.empty((len(bins[ok])-1,3))
paramsErr = n.empty((len(bins[ok])-1,3))
histBins = n.arange(-0.7, 0.71, 0.05)

p.figure(0, (12,8))
for jj in range(len(bins[ok])-1):
	sel = (hd['DF']>bins[ok][jj]) & (hd['DF']<bins[ok][jj+1])
	yDat= hd['Vmax'][sel]
	#print jj, yDat
	x1 = n.log10(yDat) - n.log10(n.mean(yDat))
	counts, bs = n.histogram(x1, bins=histBins)
	#print counts, bs
	xx=(bs[1:]+bs[:-1])/2.
	p.errorbar(xx,counts,yerr = counts**0.5 , label=r'$\delta\in$'+str(n.round(bins[ok][jj],2))+', '+str(n.round(bins[ok][jj+1],2)))


p.ylabel(r'counts')
p.xlabel(r'$log_{10}(V_{max})/\bar{V}$')
p.grid
p.xlim((-1, 1.3))
p.legend(fontsize=8)
p.savefig(join(mockDir,"plots","delta-vmaxHistPerDelta-qso-z07.png"))
p.clf()

xs = n.empty((len(bins[ok])-1, len(histBins)))
ys = n.empty((len(bins[ok])-1, len(histBins)-1))

p.figure(0, (12,8))
for jj in range(len(bins[ok])-1):
	sel = (hd['DF']>bins[ok][jj]) & (hd['DF']<bins[ok][jj+1])
	yDat= hd['Vmax'][sel]
	#print jj, yDat
	x1 = n.log10(yDat) - n.log10(n.mean(yDat))
	counts, bs = n.histogram(x1, normed = True, bins = histBins)
	#print counts, bs
	xx=(bs[1:]+bs[:-1])/2.
	p.plot(xx,counts, ls='--',lw=0.5, label=r'$\delta\in$'+str(n.round(bins[ok][jj],2))+', '+str(n.round(bins[ok][jj+1],2)))
	ys[jj] = counts
	xs[jj] = bs


Xbin=bs # n.mean(xs,axis=0)
X=(Xbin[1:]+Xbin[:-1])/2.
Y=n.mean(ys,axis=0)
YERR=n.std(ys,axis=0)

p.errorbar(X,Y, yerr = YERR, lw=2)
p.ylabel(r'counts')
p.xlabel(r'$log_{10}(V_{max})/\bar{V}$')
p.grid()
p.xlim((-1, 1.3))
p.legend(fontsize=8)
p.savefig(join(mockDir,"plots","delta-vmaxHistPerDeltaNormed-qso-z07.png"))
p.clf()

g = lambda var, sig, A, mu : A *n.e**(- (var- mu)**2./ (2*sig**2.))
positive= (Y>0)&(YERR>0)
out2, cov2 = curve_fit(g, X[positive], Y[positive], (0.12, n.max(Y), -0.025), YERR[positive])# , maxfev = 5000)

#g = lambda var, sig, A : A *n.e**(- (var+0.025)**2./ (2*sig**2.))
#out2, cov2 = curve_fit(g, X[:-2], Y[:-2], (0.13, n.max(Y)), YERR[:-2])# , maxfev = 5000)
#print out2

p.figure(0)
p.errorbar(X,Y, yerr = YERR, label='DATA')

xpl = n.arange(X.min(),X.max(),0.001)
#p.plot(xpl, g(xpl, out2[0],out2[1]), label='gaussian fit')
p.plot(xpl, g(xpl, out2[0],out2[1],out2[2]), label='gaussian fit')

p.ylabel(r'counts')
p.xlabel(r'$log_{10}(V_{max})/\bar{V}$')
p.grid()
p.xlim((-1, 1.3))
p.legend()
p.title(r'$\sigma=$'+str(n.round(out2[0],3))+r', $\mu=$'+str(n.round(out2[2],3))+r', $A=$'+str(n.round(out2[2],3)))
p.savefig(join(mockDir,"plots","delta-vmaxHistPerDeltaNormed-FIT-qso-z07.png"))
p.clf()

"""
g = lambda var, sig, A, mu : A *n.e**(- (var- mu)**2./ (2*sig**2.))
out2, cov2 = curve_fit(g, xx, counts, (0.1, n.max(counts), 0.), 2*counts**0.5 , maxfev = 500000000)
chi2 = n.sum((g(xx,out2[0], out2[1],out2[2]) - counts)**2. * counts**(-0.5) / (len(counts) - len(out2)))
params[jj]=out2
paramsErr[jj] = [cov2[0][0], cov2[1][1], cov2[2][2]]




p.errorbar(xx,counts,yerr = counts**0.5 , label=r'$\delta\in$'+str(n.round(bins[ok][jj],2))+', '+str(n.round(bins[ok][jj+1],2)))
xpl = n.arange(xx.min(),xx.max(),0.001)
p.plot(xpl, g(xpl, out2[0],out2[1],out2[2]), label='gaussian')
p.ylabel(r'counts')
p.xlabel(r'$log_{10}(V_{max})/\bar{V}$')
p.grid()
p.title(r'$\sigma=$'+str(n.round(out2[0],3))+r', $\mu=$'+str(n.round(out2[2],3))+r', $A=$'+str(n.round(out2[2],3)))
p.legend()
p.show()

hd = fits.open(join( mockDir,"Box_HAM_z0.701838_nbar1.000000e-04_LRG.DF.fits.gz"))
hd = fits.open(join( mockDir,"Box_HAM_z0.701838_nbar2.400000e-04_ELG.DF.fits.gz"))
"""