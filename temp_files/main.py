#@ File(label='Choose a directory containg D3D.dv files:', style='directory') src_dir
#@ Short(label='Compartment Channel', value=1, min=0, max=3, stepSize=1, style="slider") comp_ch
#@ Short(label='Loci Channel', value=1, min=0, max=3, stepSize=1, style="slider") loci_ch
#@ Integer(label='Number of slices around loci to consider',value=7, min=1, max=15) z_range
#@ Float(label='Comartment Thresholding', value=0.4, min=0.1, max=1.0, stepSize=0.1, style="slider") comp_T
#@ String(label="Measure compartment's boundary to:",choices={"locus center", "locus boundary"}, style="radioButtonHorizontal") loci_method
#@ Float(label='Locus Thresholding (only for "locus boundary" mode)', value=0.5, min=0.1, max=1.0, stepSize=0.1, style="slider") loci_T

pars={"src_dir":src_dir,"comp_ch":comp_ch,
"loci_ch":loci_ch,"z_range":z_range,
"comp_T":comp_T,"loci_T":loci_T,
"loci_method":loci_method}

def Zproj(stackimp,method,z_ind,z_range):
	# Gets a stack and max project it.
	from ij.plugin import ZProjector
#	imp= stackimp.duplicate()
	zp = ZProjector(stackimp)
	if method=="MAX":
		print "MAX"
		zp.setMethod(ZProjector.MAX_METHOD)
	elif method=="SUM":
		print "SUM"
		zp.setMethod(ZProjector.MAX_METHOD)
	print "+/-",int(z_range/2),"of z-index",z_ind
	zp.setStartSlice(z_ind-int(z_range/2))
	zp.setStopSlice(z_ind+int(z_range/2))
	zp.doProjection()
	zpimp = zp.getProjection()
	return zpimp
def roi_mode(stack,roi):
	imp=stack.duplicate() #copy the array as float
	imp.setRoi (roi)
	stats = imp.getStatistics()
	print "mode", stats.dmode
	return stats.dmode

def mode_subtract(sum_prj,roi):
	# Finds mode of a signle stack return the mode
	from ij.process import FloatProcessor
	from ij import ImagePlus
	dmode=roi_mode(sum_prj,roi)
	imp=sum_prj.duplicate()
	ip=imp.getProcessor()
	pix=ip.getPixels()
	minus_mode= map(lambda x: x - dmode, pix)
	ip= FloatProcessor(ip.width, ip.height, minus_mode, None)
	no_noise = ImagePlus(sum_prj.title+"_no-noise", ip)
	return no_noise

def max_pix(sum_prj,roi):
#	Get sum_prj image and an roi as input and output max signal in roi
	imp=sum_prj.duplicate() #copy the array as float
	imp.setRoi(roi)
	stats = imp.getStatistics()
#	print "mode", stats.max
	return stats.max	

def thresh(sum_prj,thresh,roi,method):
#	threshold signal based percent of max_pixel and returns ROI
#	If you use thresh=1 it returns the brightest pixel.
	from ij import ImagePlus
	from ij.measure import Measurements as mm
	from ij.process import ImageProcessor
	from ij.plugin.filter import ThresholdToSelection
	from ij.gui import Roi,PointRoi
	def max_pix(sum_prj,roi):
	#	Get sum_prj image and an roi as input and output max signal in roi
		imp=sum_prj.duplicate() #copy the array as float
		imp.setRoi(roi)
		stats = imp.getStatistics()
		return stats.max
	imp=sum_prj.duplicate()
	max_pix=max_pix(imp,roi)
	
	ip=imp.getProcessor()
	ip.setValue(0)
	ip.fillOutside(roi)
	
	if method=="boundary":
		ip.setThreshold(max_pix*thresh,max_pix,ImageProcessor.NO_LUT_UPDATE)
		bndry_roi= ThresholdToSelection.run(imp)
		return bndry_roi
	elif method=="point":
		ip.setThreshold(max_pix,max_pix,ImageProcessor.NO_LUT_UPDATE)
		bndry_roi= ThresholdToSelection.run(imp)
		bounds = bndry_roi.getBounds()
		mask =bndry_roi.getMask()
		mask.invert()
		impt =ImagePlus("d",mask)
		stats = impt.getStatistics( mm.CENTROID)
	 	xl, yl = stats.xCentroid+bounds.x,stats.yCentroid+bounds.y
		return {"x":xl,"y":yl}
		
def get_center_edge_dist(imp,speckle, spot):
####	Gets a compartment roi and a point roi. estimate the compartment with a polygon. 
#		And measures the shortest line from the point to the boundary
	# get a polygon of the Roi
	import math
	fp1  = speckle.getInterpolatedPolygon(1.,False)
	x1 = fp1.xpoints
	y1 = fp1.ypoints


#	Replace these pointROI
	#Find centroid of the spot
#	bounds = spot.getBounds()
#	mask =spot.getMask()
#	mask.invert()
#	impt =ImagePlus("d",mask)
#	stats = impt.getStatistics( mm.CENTROID)
 	xc, yc = spot["x"],spot["y"]
	
	min1 = -1
	min2 = -1
	dist_min = 1e10
	for i1 in range(len(x1)):
		dist =  (x1[i1]-xc)*(x1[i1]-xc) \
		       +(y1[i1]-yc)*(y1[i1]-yc)
		if(dist<dist_min ):
			dist_min=dist
			min1 = i1
	cal_dist=math.sqrt(dist_min)*imp.getCalibration().pixelWidth #distance in micron
	return [cal_dist,x1[min1],y1[min1],xc,yc]	
def get_closest_points(imp,roi1, roi2 ):
	# get a polygon of the Roi
	import math
	fp1  = roi1.getInterpolatedPolygon(1.,False)
	x1 = fp1.xpoints
	y1 = fp1.ypoints
	fp2 = roi2.getInterpolatedPolygon(1.,False)
	x2 = fp2.xpoints
	y2 = fp2.ypoints	
	
	min1 = -1
	min2 = -1
	dist_min = 1e10
	for i1 in range(len(x1)):
		for i2 in range(len(x2)):
			dist =  (x1[i1]-x2[i2])*(x1[i1]-x2[i2]) \
			       +(y1[i1]-y2[i2])*(y1[i1]-y2[i2])
			if(dist<dist_min ):
				dist_min=dist
				min1 = i1
				min2 = i2
	cal_dist=math.sqrt(dist_min)*imp.getCalibration().pixelWidth
	return [cal_dist,x1[min1],y1[min1], x2[min2],y2[min2]]

def main(imp,options):
	from ij.plugin import ChannelSplitter
	from ij.gui import Roi,PointRoi, PolygonRoi, Overlay, Line
	from java.awt import Color
	from ij import WindowManager
	from ij.measure import ResultsTable
	imps = ChannelSplitter.split(imp)
	roi_int = imp.getRoi()


	comp_ch=Zproj(imps[options["comp_ch"]],
		"SUM",
		imp.getZ(),
		options["z_range"])
	comp_ch=mode_subtract(comp_ch,roi_int)

	loci_ch=Zproj(imps[options["loci_ch"]],
		"SUM",
		imp.getZ(),
		options["z_range"])
	loci_ch=mode_subtract(loci_ch,roi_int)

	#Finding the boundaries of compartment and loci
	comp_roi=thresh(sum_prj=comp_ch,thresh=options["comp_T"],roi=roi_int,method="boundary")
	if options["loci_method"]== "locus center":
		loci_roi=thresh(sum_prj=loci_ch,
			thresh=options["loci_T"],
			roi=roi_int,
			method="point")
	elif options["loci_method"]== "locus boundary":
		loci_roi=thresh(sum_prj=loci_ch,
			thresh=options["loci_T"],
			roi=roi_int,
			method="boundary")
	
	if options["loci_method"]== "locus center":
		dist,xc,yc,xl,yl=get_center_edge_dist(imp,comp_roi, loci_roi)
	elif options["loci_method"]== "locus boundary":
		dist,xc,yc,xl,yl=get_closest_points(imp,comp_roi,loci_roi)
	ov=imp.getOverlay()
	if ov==None:
		ov=Overlay()
	line = Line(xc,yc, xl,yl)
	line.setStrokeWidth(0.2)
	line.setStrokeColor(Color.PINK)
	ov.add(line)

	## Adding loci overlay
	if options["loci_method"]== "locus center":
		ov.add(PointRoi(loci_roi["x"],loci_roi["y"]))
	elif options["loci_method"]== "locus boundary":
		ov.add(loci_roi)
	
	ov.add(comp_roi)
	imp.setOverlay(ov)

	rt_exist = WindowManager.getWindow("Speckle_Dist")
	
	if rt_exist==None or not isinstance(rt_exist, TextWindow):
		table= ResultsTable()
	else:
		table = rt_exist.getTextPanel().getOrCreateResultsTable()
	table.incrementCounter()
	table.addValue("Label", imp.title)
	table.addValue("Distance(micron)", dist)
	table.show("Speckle_Dist")
	
pars={"src_dir":src_dir,"comp_ch":comp_ch,
"loci_ch":loci_ch,"z_range":z_range,
"comp_T":comp_T,"loci_T":loci_T,
"loci_method":loci_method}
from ij import IJ

imp = IJ.getImage()
main(imp,pars)


