#@ File(label='Choose a directory containg D3D.dv files:', style='directory') src_dir
#@ Short(label='Compartment Channel', value=1, min=0, max=3, stepSize=1, style="slider") comp_ch
#@ Short(label='Loci Channel', value=2, min=0, max=3, stepSize=1, style="slider") loci_ch
#@ Integer(label='Number of slices around loci to consider',value=7, min=1, max=15) z_range
#@ Float(label='Comartment Thresholding', value=0.4, min=0.1, max=1.0, stepSize=0.1, style="slider") comp_T
#@ String(label="Measure compartment's boundary to:",choices={"locus center", "locus boundary"}, style="radioButtonHorizontal") loci_method
#@ Float(label='Locus Thresholding (only for "locus boundary" mode)', value=0.5, min=0.1, max=1.0, stepSize=0.1, style="slider") loci_T

"""
Copyright (c) 2019; Omid Gholamalamdari, Belmont Lab, UIUC
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the Belmont Lab nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL OMID GHOLAMALAMDARI, BELMONT LAB OR UIUC BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."""

pars={"comp_ch":comp_ch,"loci_ch":loci_ch,"z_range":z_range,"comp_T":comp_T,"loci_T":loci_T,"loci_method":loci_method}
from ij import IJ
from ij import IJ, WindowManager
from java.awt.event import KeyEvent, KeyAdapter
from ij.gui import NonBlockingGenericDialog

def Zproj(stackimp,method,z_ind,z_range):
	"""
	Gets a single channel z-stack as imp and max project it using the provided method.
	stackimp(ImagePlus): a single channel z-stack as ImagePlus object
	z_index(int): The central stack number
	z_range(int): The total number of stacks surrounding the z_index to indclude
	"""
	from ij.plugin import ZProjector
#	imp= stackimp.duplicate()
	zp = ZProjector(stackimp)
	if method=="MAX":
		print "MAX"
		zp.setMethod(ZProjector.MAX_METHOD)
	elif method=="SUM":
		zp.setMethod(ZProjector.MAX_METHOD)
	zp.setStartSlice(z_ind-int(z_range/2))
	zp.setStopSlice(z_ind+int(z_range/2))
	zp.doProjection()
	zpimp = zp.getProjection()
	return zpimp
def roi_mode(stack,roi):
	"""
	Gets a single channel Z-projected image and calculates the mode inside a given ROI.
	stack(ImagePlus): a single channel Z-projected ImagePlus object
	ROI(roi): Region of interest to calculate the mode.
	"""
	imp=stack.duplicate() #copy the array as float
	imp.setRoi (roi)
	stats = imp.getStatistics()
#	print "mode", stats.dmode
	return stats.dmode

def mode_subtract(prj,roi):
	"""
	Subtract the mode (calculated over a given ROI) from the image.
	prj(ImagePlus): a single channel Z-projected ImagePlus object.
	z_index(int): The central stack number
	ROI(roi): Region of interest to calculate the mode.
	"""
	# Finds mode of a signle stack return the mode
	from ij.process import FloatProcessor
	from ij import ImagePlus
	# Find the mode
	dmode=roi_mode(prj,roi)
	imp=prj.duplicate()
	ip=imp.getProcessor()
	pix=ip.getPixels()
	minus_mode= map(lambda x: x - dmode, pix)
	ip= FloatProcessor(ip.width, ip.height, minus_mode, None)
	no_noise = ImagePlus(prj.title+"_no-noise", ip)
	return no_noise

def max_pix(prj,roi):
	"""
	Return the intensity of the brightest pixel in a single channel Z-projected ImagePlus object,
	over a given ROI.
	prj(ImagePlus): a single channel Z-projected ImagePlus object.
	z_index(int): The central stack number
	ROI(roi): Region of interest to calculate the mode. 
	"""
#	Get sum_prj image and an roi as input and output max signal in roi
	imp=prj.duplicate() #copy the array as float
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
	from ij.text import TextWindow
	active_z=imp.getZ()
	imps = ChannelSplitter.split(imp)
	imp.setZ(active_z)
	roi_int = imp.getRoi()


	comp_imp=Zproj(imps[options["comp_ch"]],
		"SUM",
		active_z,
		options["z_range"])
	comp_imp=mode_subtract(comp_imp,roi_int)

	loci_imp=Zproj(imps[options["loci_ch"]],
		"SUM",
		imp.getZ(),
		options["z_range"])
	loci_imp=mode_subtract(loci_imp,roi_int)

	#Finding the boundaries of compartment and loci
	comp_roi=thresh(sum_prj=comp_imp,thresh=options["comp_T"],roi=roi_int,method="boundary")
	print "ok"
	if (options["loci_method"]== "locus center"):
		loci_roi=thresh(sum_prj=loci_imp,
			thresh=options["loci_T"],
			roi=roi_int,
			method="point")
	elif options["loci_method"]== "locus boundary":
		loci_roi=thresh(sum_prj=loci_imp,
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

	rt_exist = WindowManager.getWindow("Loci distance to compartment")
	
	if rt_exist==None or not isinstance(rt_exist, TextWindow):
		table= ResultsTable()
	else:
		table = rt_exist.getTextPanel().getOrCreateResultsTable()
	table.incrementCounter()
	table.addValue("Label", imp.title)
	table.addValue("Distance(micron)", dist)
	table.show("Loci distance to compartment")


def measure_key(imp, keyEvent):
	""" A function to react to z key being pressed on an image canvas. """
#	print keyEvent.getKeyCode()
	if keyEvent.getKeyCode()== 48:
		global pars
		main(imp,pars)
#		print "Measured!"
  # Prevent further propagation of the key event:
	keyEvent.consume()
 
class ListenToKey(KeyAdapter):
  def keyPressed(this, event):
    imp = event.getSource().getImage()
    measure_key(imp, event)

def get_files(mypath,ext="*.*"):
	import glob
	mypath=str(mypath)
	files = glob.glob(mypath+"/"+ext)
	return files

def load_next_image(event):
	global counter
	global images_path
#	global imp
	print images_path[counter]
	print counter
	if counter <=len(images_path):
		IJ.log("opening image:"+images_path[counter])
		IJ.openImage(images_path[counter])
		imp1=IJ.getImage()
		listener = ListenToKey()
		win=imp1.getWindow()
		canvas=win.getCanvas()
		kls = canvas.getKeyListeners()
		canvas.addKeyListener(listener)
	else:
		IJ.log("Analysis Done!")
	counter+=1

def measure_gd(src_folder,file_names):
	from javax.swing import JButton
	gd = NonBlockingGenericDialog("Loci to compartment")
	gd.setResizable(True)
	gd.pack()
	gd.addMessage("Draw a freehand ROI aound loci and closest \n compartment(e.g. speckle) and press 0 on keyboard.")
	gd.addMessage("To load next image press Next Image button.")
	next_imp_bt = JButton('Next Image', actionPerformed=load_next_image)
	gd.add(next_imp_bt)
	gd.setLocation(10,10)
	gd.setAlwaysOnTop(True)
	gd.hideCancelButton()
	gd.showDialog()  
	#  
	if gd.wasOKed():  
		IJ.log( "Measurement done! You're welcome!")

##MAIN
counter=0
images_path=get_files(src_dir,ext="*D3D.dv")
if len(images_path)==0:
	IJ.log("There are no images in the specified folder")
else:
	measure_gd(src_dir,images_path)


