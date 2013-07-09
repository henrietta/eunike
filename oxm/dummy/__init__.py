from eunike.objects import BackendInterface
from time import sleep

class OXMInterface(BackendInterface):
    """An interface class"""

    def __init__(self, eio, confsection, cc):
        """
        @param eio: Eunike Interface Object
        @type eio: L{eunike.objects.EIOOXM}
        @param confsection: Part of configuration tree relevant to this
            OAM
        @type confsection: dict
        @param cc: Satella CounterCollection        
        """
        self.eio = eio

    def on_message(self, order):
        """
        Schedule a message to execute
        @param order: Message to send
        @type order: L{eunike.objects.Order}
        """
        print 'MSG: %s to %s' % (order.content, order.target)
        sleep(0.1)
        self.eio.on_ready()

    def i_start(self):
        self.eio.on_ready()
