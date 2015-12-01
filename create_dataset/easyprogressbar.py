# This is a simple wrapper of the progressbar module, instead of using fixed
# 0-100 this module can set the start progress, end progress and current
# progress which makes it easier to control

from progressbar import *


class EasyProgressBar():
    def __init__(self):
        self.pb = ProgressBar()
        self.startval = 0
        self.endval = 100
        self.length = self.endval - self.startval

    def start(self):
        self.pb.start()

    def finish(self):
        self.pb.finish()

    def set_start(self, startval):
        self.startval = float(startval)
        self.length = self.endval - self.startval

    def set_end(self, endval):
        self.endval = float(endval)
        self.length = self.endval - self.startval

    def update(self, currval):
        percent = float(currval - self.startval) / self.length
        val = percent * 100
        if val > 100:
            val = 100.0
        elif val < 0:
            val = 0.0
        print val
        self.pb.update(val)
