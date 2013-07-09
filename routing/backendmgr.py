import re
from threading import Lock

class BackendDefinition(object):
    """Either OAM or OXM"""
    def __init__(self, handle, obj, eio, sec):
        """@param sec: part of configuration tree for that backend"""
        self.handle = handle
        self.obj = obj
        self.eio = eio
        self.sec = sec

        self.started = False
        self.stopping = False
        self.faulty = False


class OXMBackendDefinition(BackendDefinition):
    def __init__(self, handle, obj, eio, sec):
        BackendDefinition.__init__(self, handle, obj, eio, sec)

        # Default regex is an all-matching regex
        self.regexes = [re.compile(x) for x in sec['regexes']]

        self.msgclass = sec['msgclass']
        self.priority = sec['priority']
        self.backup = sec['backup']


class BackendManager(object):
    def __init__(self):
        self.oam = {}   # dict(handle => BackendDefinition)
        self.oxm = {}   # dict(handle => BackendDefinition)


        self.interesting_shit = Lock()  # to be unlocked by EIO when
                                        # something interesting happens
        self.interesting_shit.acquire()

    def on_interesting_shit(self):
        """Something of interest happened."""
        try:
            self.interesting_shit.release()
        except:
            pass

    def dispatch(self, message, dispatch):
        """Dispatches message using dispatch
        @type dispatch: L{BackendDefinition}"""
        assert dispatch.eio.ready

        dispatch.eio.ready = False
        dispatch.obj.on_message(message)

    def get_dispatch(self, order):
        """Checks whether a message can be offloaded to a OXM right now.
        Will return a BackendDefinition if possible, None otherwise"""
        oxms = [x for x in self.oxm.values() if x.started and 
                                                not x.stopping and 
                                                not x.faulty and
                                                x.msgclass == order.msgclass and
                                                x.eio.ready
                                                ]
        # Perform regex check
        matching = []
        for oxm in oxms:
            for rx in oxm.regexes:
                if rx.match(order.target):
                    matching.append(oxm)
                    break
        oxms = matching

        # Do precedence ordering
        oxms.sort(key=lambda x: x.priority, reverse=True)

        # Check - are there any non-backups left?
        non_backups_left = len([x for x in oxms if not x.backup]) > 0

        if non_backups_left:
            # Remove all backups
            oxms = [x for x in oxms if not x.backup]

        if len(oxms) > 0:
            # yes, can dispatch
            return oxms[0]
        else:
            # no, cannot dispatch
            return None

    def wait_for_interesting_shit(self):
        self.interesting_shit.acquire() # wait for somebody unlocking
        self.interesting_shit.acquire() # immediately relock

    def get_in_messages(self):
        """Returns messages that should be returned to routing layer"""
        msgs = []
        for eoxm in [x.eio for x in self.oxm.itervalues() 
                                 if len(x.eio.returned_messages) > 0]:
            msgs.extend(eoxm.pop_messages())
        for eoam in [x.eio for x in self.oam.itervalues() 
                                 if len(x.eio.received_messages) > 0]:
            msgs.extend(eoam.pop_messages())
        return msgs

    def add_backends(self, oamd, oxmd):
        """@param oamd: dict(handle => tuple(OAM object, EIO))
        @param oxmd: dict(handle => tuple(OXM object, EIO))"""
        for handle, eioo in oamd.iteritems():
            obj, eio, sec = eioo
            self.oam[handle] = BackendDefinition(handle, obj, eio, sec)

        for handle, eioo in oxmd.iteritems():
            obj, eio, sec = eioo
            self.oxm[handle] = OXMBackendDefinition(handle, obj, eio, sec)

    def start(self):
        """Starts those backends who are not started"""
        for backend in self.oam.itervalues():
            if not backend.started:
                backend.obj.i_start()
                backend.started = True
        for backend in self.oxm.itervalues():
            if not backend.started:
                backend.obj.i_start()
                backend.started = True

    def stop(self):
        """Stop those backends who are started"""
        for backend in self.oam.itervalues():
            if backend.started and not backend.stopping:
                backend.obj.i_stop()
                backend.stopping = True
        for backend in self.oxm.itervalues():
            if backend.started and not backend.stopping:
                backend.obj.i_stop()   
                backend.stopping = True     

    def join(self):
        """Join all backends"""
        for backend in self.oam.itervalues():
                if backend.started and backend.stopping:
                    backend.obj.i_join()
                    backend.started = False
                    backend.stopping = False
        for backend in self.oxm.itervalues():
            if backend.started and backend.stopping:
                backend.obj.i_join()        
                backend.started = False
                backend.stopping = False

