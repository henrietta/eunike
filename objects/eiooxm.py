class EIOOXM(object):
    """
    Eunike Interface Object/Order Execution Module

    An interface instance given to OXMs.

    """
    def __init__(self, handle, rl, bm):
        """@param rl: RoutingLayer
        @param bm: BackendManager"""
        self.handle = handle
        self.ready = False
        self.rl = rl
        self.bm = bm

        self.returned_messages = []

    def on_order_failed(self, order):
        """Called by OAM. Order has failed to be executed"""
        self.returned_messages.append(order)
        self.bm.on_interesting_shit()

    def order_passback(self, order):
        """Called by OAM. Order is passed back to routing layer
        due to some circumstances (ie. termination ordered)"""
        self.returned_messages.append(order)
        self.bm.on_interesting_shit()

    def on_ready(self):
        """Called by OXM when it is ready to process next message.
        Also, needs to be called on startup complete"""
        self.ready = True
        self.bm.on_interesting_shit()

    def pop_messages(self):
        """
        Returns all messages held internally. Clears queue
        To be called by Routing Layer
        """
        msge = self.returned_messages
        self.returned_messages = []
        return msge