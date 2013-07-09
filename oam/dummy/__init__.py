from eunike.objects import BackendInterface, Order
from satella.threads import BaseThread
from time import sleep

class Dupa(BaseThread):
    def __init__(self, eio):
        BaseThread.__init__(self)
        self.eio = eio

    def run(self):
        while not self._terminating:
            sleep(0.09)
            m = Order('600000000', 'Hello', 'sms')
            self.eio.on_received(m)

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

    def i_start(self):
        self.mthrd = Dupa(self.eio).start()

    def i_stop(self):
        self.mthrd.terminate()

    def i_join(self):
        self.mthrd.join()