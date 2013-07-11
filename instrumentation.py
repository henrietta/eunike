from satella.threads import BaseThread
from satella.contrib.instrumentation_as_json import export
import time

class InstrumentationSaverThread(BaseThread):
    def __init__(self, insmgr, confsection):
        BaseThread.__init__(self)
        self.interval = confsection['save_interval']
        self.savetarget = confsection['save_json_to']
        self.insmgr = insmgr

    def run(self):
        while not self._terminating:
            time.sleep(self.interval)
            with open(self.savetarget, 'wb') as x:
                x.write(export(self.insmgr))