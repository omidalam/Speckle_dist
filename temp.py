from java.awt.event import KeyEvent, KeyAdapter
from os.path import basename, splitext
from ij import IJ
from ij.text import TextWindow
 
path = "/Users/tarang/Downloads/test.tsv"
filename = splitext(basename(path))[0]
 
# imp will be something like a global variable. accessible from 
# funcitons. 
imp = IJ.getImage()
 
def doSomething(imp, keyEvent):
   """ A function to react to key being pressed on an image canvas. """
   IJ.log("clicked keyCode " + str(keyEvent.getKeyCode()) + " on image " +
str(imp.getTitle()))
   # Prevent further propagation of the key event:
   keyEvent.consume()
 
class ListenToKey(KeyAdapter):
   def keyPressed(this, event):
      eventSrc = event.getSource()
      tp = eventSrc.getParent() #panel is the parent, canvas being component. 
      print eventSrc
      print tp
      print "selected line:", tp.getSelectionEnd()
      print "...", tp.getLine(tp.getSelectionEnd()) 
      
      #imp = event.getSource()
      doSomething(imp, event)
 
# - - - M A I N - - -
 
listener = ListenToKey()
 
txtfile = open(path)
tw = TextWindow("Results_" + filename, txtfile.readlines(1)[0], "", 300,
700)
 
for line in txtfile.readlines():
   frame, dist, volChI, volChII = line.split("\t")
   tw.append(str(frame) + "\t" + str(dist) + "\t" + str(volChI) + "\t" +
str(volChII))
 
tw.getTextPanel().addKeyListener(listener)