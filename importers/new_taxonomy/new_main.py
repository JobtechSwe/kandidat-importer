import logging
import json
from importers.new_taxonomy import settings, taxonomy_service, converter
from importers.repository import elastic
from pkg_resources import resource_string


logging.basicConfig()
logging.getLogger(__name__).setLevel(logging.INFO)
log = logging.getLogger(__name__)
concept_id_counter = 100000001


def fetch_full_taxonomy():
    try:
        print("Printar concept_id_counter innan första användning:", concept_id_counter)
        log.info("Fetchning taxonomy")
        taxonomy_jobfields = taxonomy_service.get_all_job_fields()
        taxonomy_jobfields = add_concept_id(taxonomy_jobfields)  # adding concept_id
        taxonomy_jobgroups = taxonomy_service.get_all_job_groups()
        taxonomy_jobgroups = add_concept_id(taxonomy_jobgroups)  # adding concept_id
        taxonomy_jobterms = taxonomy_service.get_all_job_terms()
        taxonomy_jobterms = add_concept_id(taxonomy_jobterms)  # adding concept_id
        taxonomy_countries = taxonomy_service.get_all_countries()
        taxonomy_countries = add_concept_id(taxonomy_countries)  # adding concept_id
        taxonomy_regions = taxonomy_service.get_all_regions()
        taxonomy_regions = add_concept_id(taxonomy_regions)  # adding concept_id
        taxonomy_municipalities = taxonomy_service.get_all_municipalities()
        taxonomy_municipalities = add_concept_id(taxonomy_municipalities)  # adding concept_id
        taxonomy_languages = taxonomy_service.get_all_languages()
        taxonomy_languages = add_concept_id(taxonomy_languages)  # adding concept_id
        taxonomy_work_time_extent = taxonomy_service.get_all_work_time_extent()
        taxonomy_work_time_extent = add_concept_id(taxonomy_work_time_extent)  # adding concept_id
        taxonomy_skills = taxonomy_service.get_all_skills()
        taxonomy_skills = add_concept_id(taxonomy_skills)  # adding concept_id
        taxonomy_employmenttypes = taxonomy_service.get_all_employment_types()
        taxonomy_employmenttypes = add_concept_id(taxonomy_employmenttypes)  # adding concept_id
        taxonomy_drivinglicence = taxonomy_service.get_all_driving_licences()
        taxonomy_drivinglicence = add_concept_id(taxonomy_drivinglicence)  # adding concept_id
        taxonomy_wagetype = taxonomy_service.get_all_wage_type()
        taxonomy_wagetype = add_concept_id(taxonomy_wagetype)  # adding concept_id
        taxonomy_education_level = taxonomy_service.get_all_education_levels()
        taxonomy_education_level = add_concept_id(taxonomy_education_level)  # adding concept_id
        taxonomy_education_field = taxonomy_service.get_all_education_fields()
        taxonomy_education_field = add_concept_id(taxonomy_education_field)  # adding concept_id
        taxonomy_duration = taxonomy_service.get_all_duration()
        taxonomy_duration = add_concept_id(taxonomy_duration)  # adding concept_id
        taxonomy_occupation_experience = taxonomy_service.get_all_occupation_experience()
        taxonomy_occupation_experience = add_concept_id(taxonomy_occupation_experience)  # adding concept_id
    except Exception as e:
        log.error('Failed to fetch valuesets from Taxonomy Service', e)
        raise
    # Load places
    file_places = json.loads(resource_string('importers.taxonomy.resources',
                                             'platser.json').decode('utf-8'))
    file_places = add_concept_id(file_places)
    log.info("Converting taxonomy to elastic format")
    (valuestore_jobterm,
     valuestore_jobgroup,
     valuestore_jobfield) = converter.create_valuestore_jobs(taxonomy_jobterms,
                                                             taxonomy_jobgroups,
                                                             taxonomy_jobfields)
    (valuestore_places,
     valuestore_municipalities,
     valuestore_regions,
     valuestore_countries) = converter.create_valuestore_geo(file_places,
                                                             taxonomy_municipalities,
                                                             taxonomy_regions,
                                                             taxonomy_countries)
    valuestore_languages = converter.create_valuestore_languages(taxonomy_languages)
    valuestore_work_time_extent = converter.create_valuestore_work_time_extent(taxonomy_work_time_extent)
    valuestore_skills = converter.create_valuestore_skills(taxonomy_skills)
    valuestore_employmenttypes = converter.create_valuestore_employment_types(taxonomy_employmenttypes)
    valuestore_drivinglicences = converter.create_valuestore_driving_licence(taxonomy_drivinglicence)
    valuestore_wagetype = converter.create_valuestore_wagetype(taxonomy_wagetype)
    valuestore_education_level = converter.create_valuestore_education_level(taxonomy_education_level)
    valuestore_education_field = converter.create_valuestore_education_field(taxonomy_education_field)
    valuestore_duration = converter.create_valuestore_duration(taxonomy_duration)
    valuestore_occupation_experience = converter.create_valuestore_occupation_experience(taxonomy_occupation_experience)
    return (
        list(valuestore_jobterm.values())
        + list(valuestore_jobgroup.values())
        + list(valuestore_jobfield.values())
        + list(valuestore_places.values())
        + list(valuestore_municipalities.values())
        + list(valuestore_regions.values())
        + list(valuestore_countries.values())
        + list(valuestore_languages.values())
        + list(valuestore_work_time_extent.values())
        + list(valuestore_skills.values())
        + list(valuestore_employmenttypes.values())
        + list(valuestore_drivinglicences.values())
        + list(valuestore_wagetype.values())
        + list(valuestore_education_level.values())
        + list(valuestore_education_field.values())
        + list(valuestore_duration.values())
        + list(valuestore_occupation_experience.values())
    )


def add_concept_id(value_category):
    global concept_id_counter
    #print(type(value_category))
    for i in value_category:
        #print("\n", i)
        i["concept_id"] = concept_id_counter
        #for k, v in i.items():
        #    print(k, v)
        concept_id_counter += 1
    #    print(value_category[i])
    print("Printar concept_id_counter efter vardekategori:", concept_id_counter)
    return value_category


def check_if_taxonomyversion_already_exists():
    try:
        tax_versions = taxonomy_service.get_taxonomy_version()
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


def update_search_engine_valuestore(indexname, indexexists, values):
    # Create and/or update valuestore index
    try:
        log.info("creating index {} and loading taxonomy".format(indexname))
        elastic.create_index(indexname, settings.TAXONOMY_INDEX_CONFIGURATION)
        elastic.bulk_index(values, indexname, ['type', 'id'])
    except Exception as e:
        log.error('Failed to load values into search engine', e)
        raise
    # Create and/or assign index to taxonomy alias and
    # assign old index to archive alias
    try:
        if (elastic.alias_exists(settings.ES_TAX_INDEX_ALIAS)):
            log.info("updating alias {}".format(settings.ES_TAX_INDEX_ALIAS))
            alias = elastic.get_alias(settings.ES_TAX_INDEX_ALIAS)
            elastic.update_alias(
                indexname, list(alias.keys()), settings.ES_TAX_INDEX_ALIAS)
            if (not indexexists):
                if (elastic.alias_exists(settings.ES_TAX_ARCHIVE_ALIAS)):
                    log.info("Adding index {} to archive alias {}".format(indexname, settings.ES_TAX_ARCHIVE_ALIAS))
                    elastic.add_indices_to_alias(list(alias.keys()),
                                                 settings.ES_TAX_ARCHIVE_ALIAS)
                else:
                    log.info("Creating {} alias and adding index {}".format(settings.ES_TAX_ARCHIVE_ALIAS))
                    elastic.put_alias(
                        list(alias.keys()), settings.ES_TAX_ARCHIVE_ALIAS)
        else:
            log.info("creating alias {} and inserting index {}".format(settings.ES_TAX_INDEX_ALIAS, indexname))
            elastic.put_alias([indexname], settings.ES_TAX_INDEX_ALIAS)
    except Exception as e:
        log.error('Failed to update aliases', e)
        raise


def start():
    (indexname, indexexist) = check_if_taxonomyversion_already_exists()
    values = fetch_full_taxonomy()
    print("Antal värden i values:", len(values))
    for value in values:
        try:
            value["concept_id_num"] != False
        except KeyError:
            print("Printar varde utan concetp_id_num:", value)
    update_search_engine_valuestore(indexname, indexexist, values)
    log.info("import-taxonomy finished")


if __name__ == '__main__':
    start()
