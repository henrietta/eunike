from eunike.routing.prepare import register_objects
from satella.threads import BaseThread
import heapq
from satella.instrumentation.counters import CallbackCounter

class RoutingLayer(BaseThread):
    def terminate(self):
        BaseThread.terminate(self)
        self.bm.on_interesting_shit()

    def __init__(self, confobj, oams, oxms, insmgr):
        """
        @type confobj: L{eunike.config.ConfigurationObject}
        @type oams: dict(handle::str => OAMInterface)
        @type oxms: dict(handle::str => OXMInterface)
        @param insmgr: Instrumentation manager
        @type insmgr: satella.instrumentation.CounterCollection
        """
        BaseThread.__init__(self)

        self.config = confobj

        self.bm = None  #: public, BackendManager

        register_objects(self, confobj, oams, oxms, insmgr)

        self.messages = []  # heap with messages

        insmgr.add(CallbackCounter('messages_in_queue',
                        lambda: len(self.messages_to_dispatch),
                        None, u'Messages waiting to be sent'))


    def run(self):
        self.bm.start()

        while not self._terminating:
            self.bm.wait_for_interesting_shit()
            # ------------------------- Any messages inbound?
            for msg in self.bm.get_in_messages():
                print 'Pushed a message'
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

        print 'I would sync those messages but I don\'t want to'
        print '%s of em' % (len(self.messages), )
