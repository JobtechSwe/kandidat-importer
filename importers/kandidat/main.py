import time
import logging
from importers.repository import matchningsdb, elastic
from importers import settings

logging.basicConfig()
logging.getLogger(__name__).setLevel(logging.INFO)

log = logging.getLogger(__name__)


def start():
    log.info("Importing kandidater")
    if not elastic.index_exists(settings.ES_KANDIDAT_INDEX):
        log.info("Creating index")
        elastic.create_index(settings.ES_KANDIDAT_INDEX)

    start_time = time.time()
    last_timestamp = elastic.get_last_timestamp(settings.ES_KANDIDAT_INDEX)
    log.info("Last timestamp: %s" % last_timestamp)
    last_identifiers = elastic.get_ids_with_timestamp(last_timestamp,
                                                      settings.ES_KANDIDAT_INDEX)
    doc_counter = 0

    while True:
        (last_identifiers,
         last_timestamp,
         mps) = matchningsdb.load_kandidater_from_madb(last_identifiers,
                                                       last_timestamp)
        doc_counter += len(mps)
        if mps:
            log.info("Indexed %d docs so far." % doc_counter)
            elastic.bulk_index(mps, settings.ES_KANDIDAT_INDEX)
        else:
            break

    elapsed_time = time.time() - start_time

    log.info("Indexed %d docs in: %s seconds." % (doc_counter, elapsed_time))


if __name__ == '__main__':
    start()
