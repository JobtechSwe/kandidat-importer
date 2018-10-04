import logging
import sys
import psycopg2
from importers import settings

log = logging.getLogger(__name__)

if not settings.PG_DBNAME or not settings.PG_USER:
    print("You must set environment variables PG_DBNAME and PG_USER.")
    sys.exit(1)

try:
    pg_conn = psycopg2.connect(host=settings.PG_HOST,
                               port=settings.PG_PORT,
                               dbname=settings.PG_DBNAME,
                               user=settings.PG_USER,
                               password=settings.PG_PASSWORD)
except psycopg2.OperationalError as e:
    log.error("Failed to connect to PostgreSQL on %s:%s" % (settings.PG_HOST,
                                                            settings.PG_PORT))
    log.debug("Reason for PostgreSQL failure: %s" % str(e))
    sys.exit(1)


def query(sql, args):
    cur = pg_conn.cursor()
    cur.execute(sql, args)
    rows = cur.fetchall()
    cur.close()
    return rows


def read_from_pg_since(last_ids, timestamp, tablename, converter=None):
    cur = pg_conn.cursor()
    cur.execute("SELECT id, timestamp, doc FROM " + tablename +
                " WHERE timestamp >= %s ORDER BY timestamp ASC LIMIT %s",
                [timestamp, settings.PG_BATCH_SIZE])
    rows = cur.fetchall()
    # Create a list of dictionaries from row[2] adding to it the id and
    # timestamp from row[0] and row[1] unless the id is the one of the
    # same as last time method was called
    documents = [dict(converter.convert_message(row[2]) if converter else dict(row[2]),
                      **{'id': row[0], 'timestamp': row[1]})
                 for row in rows if row[0] not in last_ids]
    # Return a tuple containing a list of last ids, last timestamp and
    # list of dictionaries (annonser to save)
    return [row[0] for row in rows], rows[-1][1] if rows else 0, documents
