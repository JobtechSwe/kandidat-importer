import certifi
from ssl import create_default_context
from elasticsearch.helpers import bulk
from elasticsearch import Elasticsearch
from importers import settings

if settings.ES_USER and settings.ES_PWD:
    context = create_default_context(cafile=certifi.where())
    es = Elasticsearch([settings.ES_HOST], port=settings.ES_PORT,
                       use_ssl=True, scheme='https', ssl_context=context,
                       http_auth=(settings.ES_USER, settings.ES_PWD))
else:
    es = Elasticsearch([{'host': settings.ES_HOST, 'port': settings.ES_PORT}])


def _bulk_generator(documents, indexname, idkey, doctype='document'):
    for document in documents:
        doc_id = ('-').join([document[key] for key in idkey]) \
                         if isinstance(idkey, list) else document[idkey]
        yield {
            '_index': indexname,
            '_type': doctype,
            '_id': doc_id,
            '_source': document
        }


def bulk_index(documents, indexname, idkey='id'):
    bulk(es, _bulk_generator(documents, indexname, idkey))


def get_last_timestamp(indexname):
    response = es.search(index=indexname,
                         body={
                             "from": 0, "size": 1,
                             "sort": {"timestamp": "desc"},
                             "_source": "timestamp",
                             "query": {
                                 "match_all": {}
                             }
                         })
    hits = response['hits']['hits']
    return hits[0]['_source']['timestamp'] if hits else 0


def get_ids_with_timestamp(ts, indexname):
    # Possible failure if there are more than "size" documents with the same timestamp
    max_size = 1000
    response = es.search(index=indexname,
                         body={
                             "from": 0, "size": max_size,
                             "sort": {"timestamp": "desc"},
                             "_source": "id",
                             "query": {
                                 "term": {"timestamp": ts}
                             }
                         })
    hits = response['hits']['hits']
    return [hit['_source']['id'] for hit in hits]


def index_exists(indexname):
    return es.indices.exists(index=[indexname])


def alias_exists(aliasname):
    return es.indices.exists_alias(name=[aliasname])


def get_alias(aliasname):
    return es.indices.get_alias(name=[aliasname])


def put_alias(indexlist, aliasname):
    return es.indices.put_alias(index=indexlist, name=aliasname)


def create_index(indexname, extra_mappings=None):
    basic_body = {
        "mappings": {
            "document": {
                "properties": {
                    "timestamp": {
                        "type": "long"
                    },
                }
            }
        }
    }

    if extra_mappings:
        body = extra_mappings
        if 'mappings' in body:
            body.get('mappings', {}) \
                .get('document', {}).get('properties', {})['timestamp'] = {'type': 'long'}
        else:
            body.update(basic_body)
    else:
        body = basic_body

    # Creates an index with mappings, ignoring if it already exists
    es.indices.create(index=indexname, body=body, ignore=400)


def add_indices_to_alias(indexlist, aliasname):
    response = es.indices.update_alias(body={
        "actions": [
            {"add": {"indices": indexlist, "alias": aliasname}}
        ]
    })
    return response


def update_alias(indexname, old_indexlist, aliasname):
    actions = {
        "actions": [
            {"add": {"index": indexname, "alias": aliasname}}

        ]
    }
    for index in old_indexlist:
        actions["actions"].append({"remove": {"index": index,
                                              "alias": aliasname}})
    es.indices.update_aliases(body=actions)
