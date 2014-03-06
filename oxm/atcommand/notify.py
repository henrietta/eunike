"""
This class notifies somebody by SMTP
upon gate's failure
"""

import smtplib
from threading import Thread

class SMTPNotifier(object):
    def __init__(self, jsonconf):
        """@param jsonconf: atcommand's JSON configuration section (including
            baudrates and so on). If it does not exist, this class will nop"""
        if 'smtp' not in jsonconf:
            self.nop = True
            return

        self.nop = False
        self.host = jsonconf['smtp']['host']
        self.user = jsonconf['smtp']['user']
        self.passw = jsonconf['smtp']['pass']
        self.port = jsonconf['smtp']['port']
        self.sendfrom = jsonconf['smtp']['send_from']

        self.lnotify = jsonconf['smtp']['notify']

    def notify(self, message):
        """Send Message to all"""
        NOTThread(self, message).start()

class NOTThread(Thread):
    def __init__(self, sn, message):
        Thread.__init__(self)
        self.sn = sn
        self.message = message

    def run(self):
        sn = self.sn

        if sn.nop: return
        try:
            smtpcon = smtplib.SMTP(sn.host, sn.port)
            smtpcon.login(sn.user, sn.passw)
            for target in sn.lnotify:
                smtpcon.sendmail(sn.sendfrom, target, self.message)
            smtpcon.quit()
        except smtplib.SMTPException:
            return        