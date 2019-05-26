from ij import IJ
from ij.plugin import ChannelSplitter
from ij.plugin import ZProjector
from ij import ImagePlus
from ij.process import FloatProcessor, ImageProcessor
from ij.plugin.filter import ThresholdToSelection
from ij.gui import Roi,PointRoi, PolygonRoi, Overlay, Line
from ij.plugin.frame import RoiManager
import math
from ij.measure import ResultsTable
from ij.measure import Measurements as mm
from java.awt import Color
from ij import WindowManager
from ij.text import TextWindow
from ij.gui import GenericDialog  
  
def getOptions():  
  gd = GenericDialog("Options")  
#  gd.addStringField("name", "Untitled")  
#  gd.addNumericField("alpha", 0.25, 2)  # show 2 decimals  
#  gd.addCheckbox("optimize", True)  
#  types = ["8-bit", "16-bit", "32-bit"]  
#  gd.addChoice("output as", types, types[2])  
  gd.addSlider("Speckle Channel", 1, 4, 1)
  gd.addSlider("Spot Channel", 1, 4, 2)  
  gd.showDialog()  
  #  
  if gd.wasCanceled():  
    print "User canceled dialog!"  
    return  
#  # Read out the options  
#  name = gd.getNextString()  
#  alpha = gd.getNextNumber()  
#  optimize = gd.getNextBoolean()  
#  output = gd.getNextChoice()  
  speck_ch = gd.getNextNumber() 
  spot_ch = gd.getNextNumber()
  return speck_ch, spot_ch  


#speck_ch=1 #set speckle channel
#spot_ch=2 #set spot(FISH, tetO channel)




def maxZprojection(stackimp):
	# Gets a stack and max project it.
	zp = ZProjector(stackimp)
	zp.setMethod(ZProjector.MAX_METHOD)
	zp.doProjection()
	zpimp = zp.getProjection()
	return zpimp

def speckle_bndry(speckle_imp):
	from ij import IJ
	#removing noise 
		# Get image dmode (modal gray value)
	stats = speckle_imp.getProcessor().getStatistics()
	dmode = stats.dmode
	print "original max", stats.max
	print "original mode is", dmode

	#removing noise 
	speckle_ip=speckle_imp.getProcessor().convertToFloat() #copy the array
	speck_pix= speckle_ip.getPixels() # extract pixel values

	no_noise_pix = map(lambda x: x - dmode, speck_pix) 
	

	 
	ip3 = FloatProcessor(speckle_ip.width, speckle_ip.height, no_noise_pix, None)
	ip3.setValue(0)
	ip3.fillOutside(roi_int) # fix this
	no_noise = ImagePlus(speckle_imp.title+"_no-noise", ip3)
	stats=ip3.getStatistics()
	ip3.setThreshold(stats.max*0.4,stats.max, ImageProcessor.NO_LUT_UPDATE)

	speckle_roi = ThresholdToSelection.run(no_noise)
	return speckle_roi
	


def spot_bndry(imp):
	ip= imp.getProcessor().duplicate()
	imp2=imp.createImagePlus()
	imp2.setProcessor("copy",ip)
	ip2 = imp2.getProcessor()
	ip2.setValue(0)
	ip2.fillOutside(roi_int)
	stats = ip2.getStatistics()
	max = stats.max
	ip2.setThreshold(max,max, ImageProcessor.NO_LUT_UPDATE)
	spot_roi = ThresholdToSelection.run(imp2)
	return spot_roi

def get_closest_points( roi1, roi2 ):
	# get a polygon of the Roi
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
	return [x1[min1],y1[min1], x2[min2],y2[min2]]

def get_center_edge_dist(speckle, spot):
	# get a polygon of the Roi
	fp1  = speckle.getInterpolatedPolygon(1.,False)
	x1 = fp1.xpoints
	y1 = fp1.ypoints


	#FInd centroid of the spot
	bounds = spot.getBounds()
	mask =spot.getMask()
	mask.invert()
	impt =ImagePlus("d",mask)
	stats = impt.getStatistics( mm.CENTROID)
 	xc, yc = stats.xCentroid+bounds.x,stats.yCentroid+bounds.y
	
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

#Import the active image
imp = IJ.getImage()

#Get options
options = getOptions()
print(options)
#Split Channels into a list
imps = ChannelSplitter.split(imp)
roi_int = imp.getRoi()

#Find Speckles boundary based on 40% of max signal after de noising
speckle_roi=speckle_bndry(imps[speck_ch])

#find the center of the spot max pixel
spot_roi=spot_bndry(imps[spot_ch])

#
#table = ResultsTable()
rt_exist = WindowManager.getWindow("Speckle_Dist")
if rt_exist==None or not isinstance(rt_exist, TextWindow):
    table= ResultsTable()
else:
    table = rt_exist.getTextPanel().getOrCreateResultsTable()
#find the shortest line
#x1,y1, x2,y2 = get_closest_points( speckle_roi, spot_roi )
#line = Line(x1,y1, x2,y2 )
#dist = math.sqrt((x1-x2)*(x1-x2)+(y1-y2)*(y1-y2)) * imp.getCalibration().pixelWidth

dist2,xe,ye,xc,yc= get_center_edge_dist(speckle_roi, spot_roi)
line2 = Line(xe,ye, xc,yc)

table.incrementCounter()
table.addValue("Label", imp.title)
table.addValue("Distance(micron)", dist2)

ov=imp.getOverlay()
if ov==None:
	ov=Overlay()
#ov=O verlay()
#line.setStrokeWidth(0.2)
#ov.add(line)
line2.setStrokeWidth(0.2)
line2.setStrokeColor(Color.PINK)
ov.add(line2)


#rm = RoiManager.getInstance()
#rm.runCommand('reset')

#rm.addRoi(speckle_roi)
#rm.addRoi(spot_roi)
#rm.addRoi(rm.addRoi(spot_roi))
ov.add(PointRoi(xc,yc))
ov.add(speckle_roi)

imp.setOverlay(ov)
table.show("Speckle_Dist")
