from ij import IJ
from ij.plugin import ZProjector

def Zproj(stackimp,method,z_ind,z_range):
	# Gets a stack and max project it.
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

imp = IJ.getImage()

outimp = Zproj(imp,"SUM",imp.getZ(),10)
outimp.show()

#print "dim:", imp.getDimensions()
#print "title:", imp.title
#print "current z", imp.getZ() # get current z
#print "current index",imp.getCurrentSlice()
#
#print "position", imp.convertIndexToPosition(imp.getCurrentSlice())