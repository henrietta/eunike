from eunike.routing.prepare import register_objects
from satella.threads import BaseThread
import heapq
from satella.instrumentation.counters import CallbackCounter
import pickle

class RoutingLayer(BaseThread):
    def terminate(self):
        BaseThread.terminate(self)
        self.bm.on_interesting_shit()

    def __init__(self, confobj, oams, oxms, insmgr, osm):
        """
        @type confobj: L{eunike.config.ConfigurationObject}
        @type oams: dict(handle::str => OAMInterface)
        @type oxms: dict(handle::str => OXMInterface)
        @param insmgr: Instrumentation manager
        @type insmgr: satella.instrumentation.CounterCollection
        @param osm: OSM instance
        """
        BaseThread.__init__(self)

        self.config = confobj
        self.osm = osm
        self.bm = None  #: public, BackendManager

        register_objects(self, confobj, oams, oxms, insmgr)

        self.messages = []  # heap with messages

        insmgr.add(CallbackCounter('messages_in_queue',
                        lambda: len(self.messages),
                        None, u'Messages waiting to be sent'))

        try:
            with open(self.config['serialization_storage_path'], 'rb') as msgfin:
                messages = pickle.load(msgfin)
                self.messages.extend(messages)
                heapq.heapify(self.messages)
        except:
            pass

    def run(self):
        self.bm.start()

        while not self._terminating:
            self.bm.wait_for_interesting_shit()
            # ------------------------- Any messages inbound?
            for msg in self.bm.get_in_messages():
                heapq.heappush(self.messages, 
                               (-msg.qos, msg)) # bigger QoS the better,
                                                # but first element of heap is
                                                # the smallest element

            # Run thru messages in order. Perhaps any are dispatchable right now?
            for elem in self.messages[:]:
                qos, msg = elem
                dispatch = self.bm.get_dispatch(msg)
                if dispatch:
                    # item is dispatchable!
                    self.bm.dispatch(msg, dispatch)
                    self.messages.remove(elem)
                    continue

            heapq.heapify(self.messages)


        self.bm.stop()
        self.bm.join()
        for msg in self.bm.get_in_messages():
            heapq.heappush(self.messages, (-msg.qos, msg))

        with open(self.config['serialization_storage_path'], 'wb') as msgfout:
            pickle.dump(self.messages, msgfout, pickle.HIGHEST_PROTOCOL)
