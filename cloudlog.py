import MySQLdb
from contextlib import contextmanager

QUERY_GET_LAST_10 = """
SELECT COL_CALL, COL_TIME_ON, COL_MODE, COL_FREQ, COL_RST_SENT, COL_RST_RCVD FROM TABLE_HRD_CONTACTS_V01
ORDER BY COL_TIME_ON DESC
LIMIT 10
"""

QUERY_GET_10_SINCE = """
SELECT COL_CALL, COL_TIME_ON, COL_MODE, COL_FREQ, COL_RST_SENT, COL_RST_RCVD FROM TABLE_HRD_CONTACTS_V01
WHERE COL_TIME_ON > %s
ORDER BY COL_TIME_ON ASC
LIMIT 10
"""

QUERY_COUNT_QSOS = """
SELECT COUNT(*) FROM TABLE_HRD_CONTACTS_V01
"""

QUERY_GET_CAT = """
SELECT frequency, mode, timestamp FROM cat ORDER BY timestamp DESC LIMIT 1
"""

@contextmanager
def closer(obj):
    try:
        yield obj
    finally:
        obj.close()

class Cloudlog:
    def __init__(self, config):
        self.config = config

    def connect(self):
        return MySQLdb.connect(host=self.config['DATABASE_SERVER'],
                                user=self.config['DATABASE_USER'],
                                passwd=self.config['DATABASE_PASSWORD'],
                                db=self.config['DATABASE'])

    def get_cat(self):
        retval = {}
        with closer(self.connect()) as conn, closer(conn.cursor()) as cur:
            cur.execute(QUERY_GET_CAT)
            row = cur.fetchone()
            if row:
                retval['frequency'] = row[0]
                retval['mode'] = row[1]
                retval['timestamp'] = row[2]
            else:
                retval['frequency'] = "Unknown"
                retval['mode'] = "Unknown"
                retval['timestamp'] = 0
            return retval

    def get_last_10_qsos(self):
        with closer(self.connect()) as conn, closer(conn.cursor()) as cur:
            cur.execute(QUERY_GET_LAST_10)
            qsos = cur.fetchall()
            retval = []
            for qso in qsos:
                retval.append({
                    "datetime": qso[1],
                    "callsign": qso[0],
                    "frequency": qso[3]/1000000,
                    "mode": qso[2],
                    "report_sent": qso[4],
                    "report_recv": qso[5]
                },)
            return retval

    def get_10_qsos_since(self, time):
        with closer(self.connect()) as conn, closer(conn.cursor()) as cur:
            cur.execute(QUERY_GET_10_SINCE, (time,))
            qsos = cur.fetchall()
            retval = []
            for qso in qsos:
                retval.append({
                    "datetime": qso[1],
                    "callsign": qso[0],
                    "frequency": qso[3]/1000000,
                    "mode": qso[2],
                    "report_sent": qso[4],
                    "report_recv": qso[5]
                },)
            return retval

    def count_qsos(self):
        with closer(self.connect()) as conn, closer(conn.cursor()) as cur:
            cur.execute(QUERY_COUNT_QSOS)
            return cur.fetchone()[0]
