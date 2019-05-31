from javax.swing import JButton
from ij.gui import NonBlockingGenericDialog 
from ij import IJ

def get_files(mypath,ext="*.*"):
	import glob
	mypath=str(mypath)
	files = glob.glob(mypath+"/"+ext)
	return files


def measure_gd(src_folder,file_names):
	gd = NonBlockingGenericDialog("Options")
	gd.setResizable(True)
	gd.pack()
	gd.addMessage("Parameters selected are as below.")
	def load_next_image(event):
		global counter
		global images_path
		global imp
		print images_path[counter]
		print counter
		if counter <=len(images_path):
			IJ.log("opening image:"+images_path[counter])
			imp = IJ.openImage(images_path[counter])
			
		else:
			IJ.log("Analysis Done")
		counter+=1
		
	button = JButton('Next file', actionPerformed=load_next_image)
	bt2= JButton('measure', actionPerformed=load_next_image)
	gd.add(button)
	gd.add(bt2)
	gd.showDialog()  
	#  
	if gd.wasCanceled():  
		IJ.log( "User canceled dialog!")
counter=0
src_dir="/Users/tarang/Box_Sync/Andy_lab/Projects/tsa_compaction/FISH/Compaction_FISH/33o9-PRJs"
images_path=get_files(src_dir,ext="*.dv")

measure_gd(src_dir,images_path)

