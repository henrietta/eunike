from eunike.objects import BackendInterface, Order
from satella.threads import Monitor, BaseThread
from time import sleep, time
import sqlite3

class OSMInterface(BackendInterface, Monitor):
    def __init__(self, confsection):
        Monitor.__init__(self)
        self.conn = sqlite3.connect(confsection['path'], check_same_thread=False)

        # Check if table exists
        cur = self.conn.cursor()
        try:
            cur.execute('SELECT COUNT(rowid) FROM sent')
        except sqlite3.OperationalError:
            cur.execute('''CREATE TABLE sent (
                                rowid INTEGER PRIMARY KEY ASC,
                                sent_on DATE NOT NULL,
                                content BLOB NOT NULL,
                                target TEXT NOT NULL,
                                tag TEXT);
                        ''')
            cur.execute('CREATE INDEX i_sent_sent_on ON sent (sent_on)')
            self.conn.commit()
        cur.close()


    @Monitor.protect
    def log_as_sent(self, order):
        """Called by eunike to tell that a message has been successfully sent"""
        cur = self.conn.cursor()

        cur.execute('INSERT INTO sent (sent_on, content, target, tag) VALUES (?, ?, ?, ?)',
                        (time(), order.content.encode('utf8'), order.target, order.tag))
        self.conn.commit()
        cur.close()

    @Monitor.protect
    def i_stop(self):
        self.conn.close()        


    # ---- statistikon
    @Monitor.protect
    def st_get_count_from_day(self, day):
        """@param day: date object"""

        cur = self.conn.cursor()

        cur.execute('SELECT COUNT(rowid) FROM sent WHERE sent_on BETWEEN ? and (? + \'1 day\')')

        x = cur.fetchall()[0][0]
        cur.close()
        return x

