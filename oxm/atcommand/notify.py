"""
This class notifies somebody by SMTP
upon gate's failure
"""

import smtplib


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
        if self.nop: return
        try:
            smtpcon = smtplib.SMTP(self.host, self.port)
            smtpcon.login(self.user, self.passw)
            for target in self.lnotify:
                smtpcon.sendmail(self.sendfrom, target, message)
            smtpcon.quit()
        except smtplib.SMTPException:
            return


