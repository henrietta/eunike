from eunike.objects import BackendInterface, Order
from eunike.textservices import unicode_to_sane_ascii
from threading import Lock
from satella.threads import BaseThread
from time import sleep, time
import serial
from Queue import Queue
from eunike.oxm.atcommand.notify import SMTPNotifier
from satella.instrumentation.counters import PulseCounter, \
                                             NumericValueCounter

DASH_TIMEOUT = 3
OK_TIMEOUT = 6

class ExecutorThread(BaseThread):

    class ATCommsError(Exception): 
        def __init__(self, instant_failure=False):
            self.instant_failure = instant_failure

    def mk_serport(self):
        try:
            self.serport
        except:
            pass
        else:
            self.serport.close()

        self.serport = serial.Serial(self.comport, self.baudrate, timeout=0)

    def __init__(self, oxmi, recovery_message, cc, confsection):
        BaseThread.__init__(self)
        self.name = confsection['handle']
        self.comport, self.baudrate = confsection['serial_port'], confsection['serial_baudrate']
        self.notifier = SMTPNotifier(confsection)
        self.mk_serport()
        self.mte = None     #: message to execute
        self.interesting_shit = Lock()
        self.interesting_shit.acquire()
        self.oxm = oxmi
        self.conseq_reset = 0

        self.recovery_message = recovery_message

        self.is_attempting_recovery = False

        self.cc_hard_resets = PulseCounter('hard_resets',
            resolution=24*60*60, units='resets', 
            description=u'Hard resets during last 24 hours')
        self.cc_soft_resets = PulseCounter('soft_resets',
            resolution=24*60*60, units='resets', 
            description=u'Hard resets during last 24 hours')
        self.cc_send_time = NumericValueCounter('send_time',
            units='seconds', description='Time it took to send last SMS',
            history=20)


        cc.add(self.cc_hard_resets)
        cc.add(self.cc_soft_resets)
        cc.add(self.cc_send_time)

    def on_interesting_shit(self):
        try:
            self.interesting_shit.release()
        except:
            pass

    def terminate(self):
        BaseThread.terminate(self)
        self.on_interesting_shit()

    def send_message(self, order):
        """Attempts sending the message. Raises ATCommsError if something
        failed"""

        sms_sent_speed = time()

        # transforms content into msgcnt
        msgtext = unicode_to_sane_ascii(order.content)

        # clear any URCs
        k = self.serport.read(1024)
        while len(k) > 0: k = self.serport.read(1024)

        self.serport.write('AT+CMGS="%s"\r' % (order.target, ))
        sleep(0.1)
        k = self.serport.read(1024)
        started_waiting_on = time()
        while not '>' in k:
            if (time() - started_waiting_on) > DASH_TIMEOUT:
                raise self.ATCommsError()
            sleep(0.1)
            k += self.serport.read(1024)

        if 'ERROR' in k:
            raise self.ATCommsError(True)

        self.serport.write('%s\x1A' % (msgtext, ))
        started_waiting_on = time()

        k = ''
        while True:
            if (time() - started_waiting_on) > OK_TIMEOUT:
                raise self.ATCommsError()
            sleep(0.5)
            k += self.serport.read(1024)

            if '\r\nERROR\r\n' in k:
                raise self.ATCommsError(True)

            if '\n\r\nOK\r\n' in k:
                self.cc_send_time.update(time() - sms_sent_speed)
                return


    def run(self):
        self._run()
        if self.mte != None:
            self.oxm.eio.order_passback(self.mte)

    def _run(self):
        while not self._terminating:
            self.interesting_shit.acquire()

            if self.is_attempting_recovery:

                while not self._terminating:
                    # We will be attempting to periodically send a SMS

                    for i in xrange(0, 15): # delay loop
                        sleep(3)
                        if self._terminating: break

                    try:
                        self.send_message(self.recovery_message)
                    except self.ATCommsError:
                        # still fucked up
                        self.attempt_recovery()
                    else:
                        # success!
                        self.is_attempting_recovery = False
                        self.oxm.eio.on_fail_status(False)
                        self.notifier.notify('EUNIKE: %s left failed state' % (self.name, ))                        
                        self.conseq_reset = 0
                        break

                if self._terminating:
                    return

            elif self.mte != None:
                try:
                    self.send_message(self.mte)
                except self.ATCommsError:
                    if not self.attempt_recovery():
                        self.oxm.eio.on_fail_status(True)
                        self.notifier.notify('EUNIKE: %s entered failed state' % (self.name, ))
                        self.oxm.eio.on_ready() # We won't be scheduled anyway :)
                        self.oxm.eio.on_order_failed(self.mte)
                        self.mte = None
                        self.is_attempting_recovery = True
                        self.on_interesting_shit()
                        continue
                    else:
                        # Try again
                        self.on_interesting_shit()
                        continue
                else:
                    self.conseq_reset = 0
                    self.oxm.eio.on_sent_successfully(self.mte)
                    self.mte = None
                    self.oxm.eio.on_ready()
            
    def attempt_recovery(self):
        """Returns False when it's hopeless"""
        self.conseq_reset += 1

        if self.conseq_reset == 7:
            return False

        elif self.conseq_reset > 4:  
            self.attempt_hard_reset()         
        else:
            self.attempt_soft_reset()

        return True # after conseq_reset==7 there's no need to return False

    def attempt_soft_reset(self):
        """To be used in case of transmission failure"""
        self.serport.write(' \x1AAT+CSQ\r\r')   # Vulcan nerve pinch
        sleep(1)
        self.serport.read(2048)
        self.cc_soft_resets.update()

    def attempt_hard_reset(self):
        """To be used in case of hard failures"""
        self.serport.write(' \x1A\r\rAT+CFUN=1\r\r')
        sleep(5)
        self.serport.read(2048)
        self.cc_hard_resets.update()
        self.mk_serport()


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

        test_message = Order(confsection['recovery_msg_target'],
                             confsection['recovery_msg_content'],
                             'sms', None, 0, 'System')

        self.et = ExecutorThread(self, test_message, cc, confsection)


    def on_message(self, order):
        """
        Schedule a message to execute
        @param order: Message to send
        @type order: L{eunike.objects.Order}
        """
        self.et.mte = order
        self.et.on_interesting_shit()

    def i_start(self):
        self.et.start()
        self.eio.on_ready()

    def i_stop(self):
        self.et.terminate()

    def i_join(self):
        self.et.join()
        try:
            self.et.serport.close()
        except:
            pass
