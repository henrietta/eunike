from eunike.objects import BackendInterface, Order
from satella.threads import BaseThread
from time import sleep
import os, copy, json
import os.path

SMS_FILE_DEFAULTS = {
    'tag': None,
    'qos': 0,
    'backend': None
}


class FileScan(BaseThread):
    def __init__(self, eio, confsection):
        BaseThread.__init__(self)
        self.eio = eio
        self.dirscan = confsection['directory']

    def run(self):
        dupa = False
        while not self._terminating:
            sleep(5)

            for fname in os.listdir(self.dirscan):
                if not fname.endswith('.msg'): continue
                
                target = os.path.join(self.dirscan, fname)
                try:
                    with open(target, 'rb') as fin:
                        dt = copy.deepcopy(SMS_FILE_DEFAULTS)
                        dt.update(json.load(fin))

                        ord = Order(dt['target'], dt['content'], dt['msgclass'],
                                    dt['backend'], dt['qos'], dt['tag'])
                        self.eio.on_received(ord)
                except:
                    pass
                finally:
                    os.unlink(target)

class OAMInterface(BackendInterface):
    """An interface class"""

    def __init__(self, eio, confsection, cc):
        """
        @param eio: Eunike Interface Object
        @type eio: L{eunike.objects.EIOOAM}
        @param confsection: Part of configuration tree relevant to this
            OAM
        @type confsection: dict
        @param cc: Satella CounterCollection
        """
        self.eio = eio
        self.confsection = confsection

    def i_start(self):
        self.mthrd = FileScan(self.eio, self.confsection).start()

    def i_stop(self):
        self.mthrd.terminate()

    def i_join(self):
        self.mthrd.join()