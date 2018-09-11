from importers.repository import elastic
from importers.taxonomy import settings

taxtype_legend = {
    'yrke': 'jobterm',
    'yrkesroll': 'jobterm',
    'yrkesgrupp': 'jobgroup',
    'yrkesomrade': 'jobfield',
    'sprak': 'language',
    'kompetens': 'skill',
    'kommun': 'municipality',
    'lan': 'region',
    'sprak': 'language',
    'land': 'country',
    'utbildningsinriktning': 'education',
    'utbildningsniva': 'education_level',
    'korkort': 'drivers_license',
    'varaktighet': 'duration_type',
    'lonetyp': 'wage_type',
    'anstallningstyp': 'employment_type',
    'arbetstidstyp': 'worktime_extent',
}

taxonomy_cache = {}


def get_term(taxtype, taxid):
    if taxtype not in taxonomy_cache:
        taxonomy_cache[taxtype] = {}
    if taxid in taxonomy_cache[taxtype]:
        return taxonomy_cache[taxtype][taxid]
    taxonomy_entity = get_entity(taxtype, taxid)
    label = None
    if 'label' in taxonomy_entity:
        label = taxonomy_entity['label']
    if 'term' in taxonomy_entity:
        label = taxonomy_entity['term']
    taxonomy_cache[taxtype][taxid] = label
    return label


def get_entity(taxtype, taxid):
    doc_id = "%s-%s" % (taxtype_legend.get(taxtype, ''), taxid)

    taxonomy_entity = elastic.es.get_source(index=settings.ES_TAX_INDEX_ALIAS,
                                            id=doc_id,
                                            doc_type='_all', ignore=404)
    return taxonomy_entity
