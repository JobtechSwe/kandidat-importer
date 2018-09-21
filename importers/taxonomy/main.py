import logging
from importers.taxonomy import settings, taxonomy
from collections import OrderedDict
from importers.repository import elastic

logging.basicConfig()
logging.getLogger(__name__).setLevel(logging.DEBUG)
log = logging.getLogger(__name__)


def create_valuestore_jobs(taxonomy_jobterms, taxonomy_jobgroups,
                           taxonomy_jobfields):
    jobfields = {
        field['LocaleFieldID']: OrderedDict(
            [('id', str(field['LocaleFieldID'])),
             ('type', settings.taxonomy_type['yrkesomrade']),
             ('label', field['Term']), ('description', field['Description'])])
        for field in taxonomy_jobfields
    }
    jobgroups = {
        field['LocaleCode']: OrderedDict(
            [('id', str(field['LocaleCode'])),
             ('type', settings.taxonomy_type['yrkesgrupp']),
             ('label', field['Term']), ('description', field['Description']),
             ('parent', jobfields[field['LocaleFieldID']])])
        for field in taxonomy_jobgroups
    }
    jobterms = {
        field['OccupationNameID']:
        OrderedDict([('id', str(field['OccupationNameID'])),
                     ('type', settings.taxonomy_type['yrke']), ('label',
                                                                field['Term']),
                     ('parent', jobgroups[field['LocaleCode']])])
        for field in taxonomy_jobterms
    }
    return (jobterms, jobgroups, jobfields)


def create_valuestore_geo(taxonomy_municipalities, taxonomy_regions,
                          taxonomy_countries):
    countries = {
        field['CountryID']:
        OrderedDict([('id', str(field['CountryID'])),
                     ('type', settings.taxonomy_type['landkod']),
                     ('label', field['Term']),
                     ('num_id', int(field['CountryID'])),
                     ('country_code', field['CountryCode'])])
        for field in taxonomy_countries
    }
    regions = {
        field['NationalNUTSLevel3Code']: OrderedDict(
            [('id', str(field['NationalNUTSLevel3Code'])),
             ('type', settings.taxonomy_type['lanskod']),
             ('label', field['Term']), ('num_id',
                                        int(field['NationalNUTSLevel3Code']))])
        for field in taxonomy_regions
    }
    municipalities = {
        field['NationalNUTSLAU2Code']: OrderedDict(
            [('id', str(field['NationalNUTSLAU2Code'])),
             ('type', settings.taxonomy_type['kommunkod']), ('label',
                                                             field['Term']),
             ('parent', regions[field['NationalNUTSLevel3Code']]),
             ('num_id', int(field['NationalNUTSLAU2Code']))])
        for field in taxonomy_municipalities
    }
    return (municipalities, regions, countries)


def create_valuestore_skills(taxonomy_skills):
    skills = {
        field['SkillID']:
        OrderedDict([('id', str(field['SkillID'])),
                     ('type', settings.taxonomy_type['kompetens']),
                     ('label', field['Term']), ('description', field['Term'])])
        for field in taxonomy_skills
    }
    return (skills)


def create_valuestore_work_time_extent(taxonomy_work_time_extent):
    wte = {
        field['WorkTimeExtentID']:
        OrderedDict([('id', str(field['WorkTimeExtentID'])),
                     ('type', settings.taxonomy_type['arbetstidsomfattning']),
                     ('label', field['Term'])])
        for field in taxonomy_work_time_extent
    }
    return (wte)


def create_valuestore_languages(taxonomy_languages):
    languages = {
        field['LanguageID']:
        OrderedDict([('id', str(field['LanguageID'])),
                     ('type', settings.taxonomy_type['sprak']),
                     ('label', field['Term']), ('num_id',
                                                int(field['LanguageID']))])
        for field in taxonomy_languages
    }
    return (languages)


def fetch_full_taxonomy():
    try:
        taxonomy_jobfields = taxonomy.get_all_job_fields()
        taxonomy_jobgroups = taxonomy.get_all_job_groups()
        taxonomy_jobterms = taxonomy.get_all_job_terms()
        taxonomy_countries = taxonomy.get_all_countries()
        taxonomy_regions = taxonomy.get_all_regions()
        taxonomy_municipalities = taxonomy.get_all_municipalities()
        taxonomy_languages = taxonomy.get_all_languages()
        taxonomy_work_time_extent = taxonomy.get_all_work_time_extent()
        taxonomy_skills = taxonomy.get_all_skills()
    except Exception as e:
        log.error('Failed to fetch valuesets from Taxonomy Service', e)
        raise
    (valuestore_jobterm,
     valuestore_jobgroup, valuestore_jobfield) = create_valuestore_jobs(
         taxonomy_jobterms, taxonomy_jobgroups, taxonomy_jobfields)
    (valuestore_municipalities, valuestore_regions, valuestore_countries)\
        = create_valuestore_geo(
        taxonomy_municipalities, taxonomy_regions, taxonomy_countries)
    valuestore_languages = create_valuestore_languages(taxonomy_languages)
    valuestore_work_time_extent = create_valuestore_work_time_extent(
        taxonomy_work_time_extent)
    valuestore_skills = create_valuestore_skills(taxonomy_skills)
    return (
        list(valuestore_jobterm.values()) + list(
            valuestore_jobgroup.values()) + list(valuestore_jobfield.values())
        + list(valuestore_municipalities.values()) + list(
            valuestore_regions.values()) + list(valuestore_countries.values())
        + list(valuestore_languages.values())
        + list(valuestore_work_time_extent.values()) + list(
            valuestore_skills.values()))


def check_if_taxonomyversion_already_exists():
    try:
        tax_versions = taxonomy.get_taxonomy_version()
    except Exception as e:
        log.error('Failed to get taxonomy version from taxonomy service', e)
        raise
    highest_version = max([v['BastaxonomiId'] for v in tax_versions])
    expected_index_name = settings.ES_TAX_INDEX_BASE + str(highest_version)
    log.info(
        'Expected index name based on taxonomy service version is {}'.format(
            expected_index_name))
    try:
        index_exists = elastic.index_exists(expected_index_name)
    except Exception as e:
        log.error('Failed to check index existence on elastic', e)
        raise
    return (expected_index_name, index_exists)


def update_search_engine_valuestore(indexname, indexexist, values):
    try:
        elastic.create_index(indexname)
        elastic.bulk_index(values, indexname, ['type', 'id'])
    except Exception as e:
        log.error('Failed to load values into search engine', e)
        raise

    if not indexexist:
        try:
            if (elastic.alias_exists(settings.ES_TAX_INDEX_ALIAS)):
                alias = elastic.get_alias(settings.ES_TAX_INDEX_ALIAS)
                if (elastic.alias_exists(settings.ES_TAX_ARCHIVE_ALIAS)):
                    elastic.add_indices_to_alias(
                        list(alias.keys(), settings.ES_TAX_ARCHIVE_ALIAS))
                else:
                    elastic.put_alias(
                        list(alias.keys()), settings.ES_TAX_ARCHIVE_ALIAS)
                    elastic.update_alias(indexname, list(alias.keys()),
                                         settings.ES_TAX_INDEX_ALIAS)
            else:
                elastic.put_alias([indexname], settings.ES_TAX_INDEX_ALIAS)
        except Exception as e:
            log.error('Failed to update aliases', e)
            raise


def start():
    (indexname, indexexist) = check_if_taxonomyversion_already_exists()
    values = fetch_full_taxonomy()
    update_search_engine_valuestore(indexname, indexexist, values)


if __name__ == '__main__':
    start()
