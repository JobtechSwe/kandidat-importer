from importers.repository import elastic, postgresql
from importers.platsannons import converter
from importers import settings
import time


def start():
    start_time = time.time()
    if not elastic.index_exists(settings.ES_ANNONS_INDEX):
        elastic.create_index(settings.ES_ANNONS_INDEX)
    last_timestamp = elastic.get_last_timestamp(settings.ES_ANNONS_INDEX)
    print("Last timestamp: %d" % last_timestamp)
    last_identifiers = elastic.get_ids_with_timestamp(last_timestamp,
                                                      settings.ES_ANNONS_INDEX)
    doc_counter = 0

    while True:
        (last_identifiers, last_timestamp, platsannonser) = \
            postgresql.read_from_pg_since(last_identifiers,
                                          last_timestamp, 'platsannonser', converter)
        doc_counter += len(platsannonser)
        if platsannonser:
            elastic.bulk_index(platsannonser, settings.ES_ANNONS_INDEX)
        else:
            break

    elapsed_time = time.time() - start_time

    print("Indexed %d docs in: %s seconds." % (doc_counter, elapsed_time))


if __name__ == '__main__':
    start()
