# encoding: utf8

__author__ = 'Leon'

from objects import lights
from variable.global_vars import G
from panda3d.core import NodePath
from panda3d.core import Thread
from util import log
from panda3d.core import loadPrcFileData
loadPrcFileData("", "want-directtools #t")
loadPrcFileData("", "want-tk #t")

import random
r = 20
def v():
    return (random.random() - .5) * 2 * r

roots = []
idx2ori_nps = {}
for k in range(50):
    root = NodePath("flatten_root:%s" % k)
    root.reparent_to(G.render)
    nps = []
    for i in range(50):
        model = G.loader.loadModel('../assets/blender/twig.egg')
        # one trap here.
        # getChildren() at first, flatten() won't touch any geoms under model node path.
        new_np = root.attach_new_node('child_%s_%s' % (k, i))
        model.get_children().reparentTo(new_np)
        new_np.set_pos(v(), v(), v())

        #nps.append(new_np)
    roots.append(root)
    idx2ori_nps[k] = nps

var={
    'ts': 0
}
def flatten(idx=0):
    if idx >= len(roots):
        return
    import time
    var['ts'] = time.time()
    next_idx = idx+1
    def cb(x):
        log.debug('x: %s', x)
        log.debug("time consumed: %s", time.time() - var['ts'])
        roots[idx].remove_node()
        roots[idx] = x
        x.reparent_to(G.render)
        flatten(next_idx)
    G.loader.asyncFlattenStrong(roots[idx], False, cb)

def stat():
    G.render.analyze()
lights.create()
G.accept('v', flatten)
G.accept('b', stat)
G.enableMouse()
G.cam.set_pos(0, 0, 100)
G.cam.look_at(0, 0, 0)
G.run()
