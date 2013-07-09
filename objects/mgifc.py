class BackendInterface(object):
    """
    Interface definition for backend modules - both OAM and OXM
    """

    def i_start(self):
        """Facilities for this module, such as threads or connections
        are to be started"""

    def i_stop(self):
        """Facilities for this module, such as threads or connections
        are to be stopped"""

    def i_join(self):
        """Hangs until facilities are terminated. Called after i_stop()"""
