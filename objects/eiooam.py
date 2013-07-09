from collections import deque

class EIOOAM(object):
    """
    Eunike Interface Object/Order Acquisition Module

    An interface instance given to OAMs
    """

    def __init__(self, oamhandle, rl, bm):
        """@param oamhandle: handle of OAM this object will be passed to
        @param rl: RoutingLayer
        @param bm: BackendManager"""
        self.handle = oamhandle
        self.received_messages = []
        self.rl = rl
        self.bm = bm

    def on_received(self, order):
        """
        Called by OAM if order is received.
        """
        self.received_messages.append(order)
        self.bm.on_interesting_shit()

    def pop_messages(self):
        """
        Returns all messages held internally. Clears queue
        To be called by Routing Layer
        """
        msge = self.received_messages
        self.received_messages = []
        return msge
