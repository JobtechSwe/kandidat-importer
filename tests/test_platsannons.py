from importers.repository import elastic, postgresql
from importers.platsannons import settings
import time
from importers.platsannons.main import read_from_pg_since

'''
def read_from_pg_since(last_ids, timestamp):
    rows = postgresql.query("SELECT id, ts, doc FROM platsannonser WHERE ts >= %s ORDER BY ts LIMIT %s", [timestamp, settings.PG_BATCH_SIZE])
    # Create a list of dictionaries from row[2] adding to it the id and timestamp from row[0] and row[1] unless
    # the id is the one of the same as last time method was called
    documents = [dict(row[2], **{'id': row[0], 'timestamp': row[1]}) for row in rows if row[0] not in last_ids]
    # Return a tuple containing a list of last ids, last timestamp and list of dictionaries (annonser to save)
    return [row[0] for row in rows], rows[-1][1] if rows else 0, documents

'''
def test_read_from_pg_sinse():
    #print (last_timestamp = elastic.get_last_timestamp_from_elastic(settings.ES_INDEX))
    #read_from_pg_since(1,0)
    print (settings.PG_BATCH_SIZE, settings.ES_INDEX)