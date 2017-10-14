from direct.directbase import DirectStart
from direct.gui.DirectGui import *
from panda3d.core import *

b1 = DirectButton(text=("Button1", "click!", "roll", "disabled"),
                  text_scale=0.1, borderWidth=(0.01, 0.01),
                  relief=1)


from direct.gui.DirectGui import DirectFrame

myFrame = DirectFrame(frameColor=(0, 0, 0, 0.1),
                      frameSize=(-.2,.2,-0.2,.2))
myFrame.setPos(-0.5, 0, -0.5)
b1.reparentTo(myFrame)

b1=myFrame
def t(task):
    mn = base.mouseWatcherNode
    if not mn.hasMouse():
        return task.cont
    # Get from/to points from mouse click
    pMouse = mn.getMouse()
    b1.setPos(pMouse.getX(), 0, pMouse.getY())
    b1['frameSize'] = (-0.1,.1,-.1,.1)
    return task.cont



taskMgr.add(t, "abc")
run()