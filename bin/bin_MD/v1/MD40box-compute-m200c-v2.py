from MultiDark import *
box = MultiDarkSimulation(Lbox=4000.0 * uu.Mpc,wdir="/data2/DATA/eBOSS/Multidark-lightcones", boxDir = "MD_4Gpc",snl =  n.array(glob.glob(join("/data2/DATA/eBOSS/Multidark-lightcones" , "MD_4Gpc", "snapshots", "hlist_*.list"))) ,zsl = None,zArray = n.arange(0.,4.,1e-1),Hbox = 67.77 * uu.km / (uu.s * uu.Mpc),Melement = 96000000000.0)


for ii in n.arange(len(box.snl)):
	fileList = glob.glob(box.snl[ii][:-5]+"*VmaxM200c*.fits")
	rootname = box.snl[ii][:-5].split('/')[-1]
	box.computeSingleDistributionFunctionV2( fileList, rootname, "M200c", n.arange(8,16,0.01))

