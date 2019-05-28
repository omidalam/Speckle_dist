from ij.gui import GenericDialog 
from ij import IJ, WindowManager
from java.awt.event import KeyEvent, KeyAdapter 
  
def getOptions():  
  gd = GenericDialog("Loci Distance to compartment option")  
 
  gd.addChoice("Compartment Channel", ["1","2","3","4"], "1")
  gd.addNumericField("Compartment Threshold",0.60,2)
  gd.addChoice("Loci Channel", ["1","2","3","4"], "2")
  gd.addNumericField("Compartment Threshold",0.60,2)
  gd.showDialog()  
  #  
  if gd.wasCanceled():  
    print "User canceled dialog!"  
    return  
#  # Read out the options  
 
  speck_ch= int(gd.getNextChoice())
  speck_th = gd.getNextNumber() 
  loci_ch= int(gd.getNextChoice())
  loci_th = gd.getNextNumber()
  
  return speck_ch,speck_th, loci_ch, loci_th


	

def doSomething(imp, keyEvent):
  """ A function to react to key being pressed on an image canvas. """
  IJ.log("clicked keyCode " + str(keyEvent.getKeyCode()) + " on image " + str(imp))
  # Prevent further propagation of the key event:
  keyEvent.consume()
 
class ListenToKey(KeyAdapter):
  def keyPressed(this, event):
    imp = event.getSource().getImage()
    doSomething(imp, event)
  
#def listen():
#	listener = ListenToKey()
#	for imp in map(WindowManager.getImage, WindowManager.getIDList()):
#	win = imp.getWindow()
#	if win is None:
#    	continue
#	canvas = win.getCanvas()
#  # Remove existing key listeners
#	kls = canvas.getKeyListeners()
##  map(canvas.removeKeyListener, kls)
#  # Add our key listener
#	canvas.addKeyListener(listener)

options = getOptions()
print(options)

gd = GenericDialog("Measure distance")
gd.addMessage("""Draw a freehand selection around loci and closest speckle.\n
Then prress the specified key.\n 
click next when done with the image. Click Cancel when done.""")
gd.showDialog()
while (!gd.wasCanceled):
	if 
if 
listener = ListenToKey()
imp= IJ.getImage()
win=imp.getWindow()
canvas=win.getCanvas()
kls = canvas.getKeyListeners()
canvas.addKeyListener(listener)

		