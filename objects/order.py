class Order(object):
    """A message order to send"""
    def __init__(self, target, content, msgclass, backend=None, qos=0):
        """
        An order needs at least target and content. 
        backend and qos can be calculate automatically from config
        file
        """

        self.msgclass = msgclass    #: Class of backend to execute on
        self.backend = backend  #: Particular OXM to execute it on
        self.target = target    #: Address to send message to, OXM-dependent
        self.content = content  #: Message content. type -> unicode
        self.qos = qos          #: Priority. The bigger, the more important.
                                # type -> integer