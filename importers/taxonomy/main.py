import logging
import json
from importers.taxonomy import settings, taxonomy_service
from collections import OrderedDict
from importers.repository import elastic
from valuestore.taxonomy import tax_type
from pkg_resources import resource_string

logging.basicConfig()
logging.getLogger(__name__).setLevel(logging.INFO)
log = logging.getLogger(__name__)


def create_valuestore_jobs(taxonomy_jobterms, taxonomy_jobgroups,
                           taxonomy_jobfields):
    jobfields = {
        field['LocaleFieldID']: OrderedDict(
            [('id', str(field['LocaleFieldID'])),
             ('type', tax_type['yrkesomrade']),
             ('label', field['Term']), ('description', field['Description']),
             ('num_id', int(field['LocaleFieldID']))])
        for field in taxonomy_jobfields
    }
    jobgroups = {
        field['LocaleCode']: OrderedDict(
            [('id', str(field['LocaleCode'])),
             ('type', tax_type['yrkesgrupp']),
             ('label', field['Term']), ('description', field['Description']),
             ('num_id', int(field['LocaleCode'])),
             ('parent', jobfields[field['LocaleFieldID']])])
        for field in taxonomy_jobgroups
    }
    jobterms = {
        field['OccupationNameID']:
        OrderedDict([('id', str(field['OccupationNameID'])),
                     ('type', tax_type['yrkesroll']),
                     ('label', field['Term']),
                     ('num_id', int(field['LocaleCode'])),
                     ('parent', jobgroups[field['LocaleCode']])])
        for field in taxonomy_jobterms
    }
    return (jobterms, jobgroups, jobfields)


def create_valuestore_geo(file_places, taxonomy_municipalities, taxonomy_regions,
                          taxonomy_countries):
    countries = {
        field['CountryID']:
        OrderedDict([('id', str(field['CountryID'])),
                     ('type', tax_type['land']),
                     ('label', field['Term']),
                     ('num_id', int(field['CountryID'])),
                     ('country_code', field['CountryCode'])])
        for field in taxonomy_countries
    }
    regions = {
        field['NationalNUTSLevel3Code']: OrderedDict(
            [('id', str(field['NationalNUTSLevel3Code'])),
             ('type', tax_type['lan']),
             ('label', field['Term']), ('num_id',
                                        int(field['NationalNUTSLevel3Code']))])
        for field in taxonomy_regions
    }
    municipalities = {
        field['NationalNUTSLAU2Code']: OrderedDict(
            [('id', str(field['NationalNUTSLAU2Code'])),
             ('type', tax_type['kommun']), ('label', field['Term']),
             ('parent', regions[field['NationalNUTSLevel3Code']]),
             ('num_id', int(field['NationalNUTSLAU2Code']))])
        for field in taxonomy_municipalities
    }

    places = {}
    for place in file_places:
        identifier = "%s-%s" % (place['kommunkod'], _slugify(place['label']))
        municipality = municipalities[place['kommunkod']]
        places[identifier] = dict({'id': identifier}, **place)
        places[identifier]['parent'] = municipality

    return (places, municipalities, regions, countries)


def _slugify(string):
    return string.lower().replace('å', 'a') \
            .replace('ä', 'a').replace('ö', 'o').replace(' ', '_') if string else None


def create_valuestore_skills(taxonomy_skills):
    skills = {
        field['SkillID']:
        OrderedDict([('id', str(field['SkillID'])),
                     ('type', tax_type['kompetens']),
                     ('label', field['Term']), ('description', field['Term'])])
        for field in taxonomy_skills
    }
    return (skills)


def create_valuestore_work_time_extent(taxonomy_work_time_extent):
    wte = {
        field['WorkTimeExtentID']:
        OrderedDict([('id', str(field['WorkTimeExtentID'])),
                     ('type', tax_type['arbetstidsomfattning']),
                     ('label', field['Term'])])
        for field in taxonomy_work_time_extent
    }
    return (wte)


def create_valuestore_languages(taxonomy_languages):
    languages = {
        field['LanguageID']:
        OrderedDict([('id', str(field['LanguageID'])),
                     ('type', tax_type['sprak']),
                     ('label', field['Term']), ('num_id',
                                                int(field['LanguageID']))])
        for field in taxonomy_languages
    }
    return (languages)


def create_valuestore_employment_types(taxonomy_employmenttypes):
    employment_types = {
        field['EmploymentTypeID']:
        OrderedDict([('id', str(field['EmploymentTypeID'])),
                     ('type', tax_type['anstallningstyp']),
                     ('label', field['Term']),
                     ('num_id', int(field['EmploymentTypeID']))])
        for field in taxonomy_employmenttypes
    }
    return employment_types


def create_valuestore_driving_licence(taxonomy_drivinglicence):
    driving_licence = {
        field['DrivingLicenceID']:
        OrderedDict([('id', str(field['DrivingLicenceID'])),
                     ('type', tax_type['korkort']),
                     ('label', field['Term']),
                     ('description', field['Description']),
                     ('num_id', int(field['DrivingLicenceID']))])
        for field in taxonomy_drivinglicence
    }
    return driving_licence


def create_valuestore_wagetype(taxonomy_wagetype):
    wage_type = {
        field['WageTypeID']:
        OrderedDict([('id', str(field['WageTypeID'])),
                     ('type', tax_type['lonetyp']),
                     ('label', field['Term']),
                     ('num_id', int(field['WageTypeID']))])
        for field in taxonomy_wagetype
    }
    return wage_type


def create_valuestore_education_level(taxonomy_education_level):
    education_level = {
        field['EducationLevelID']:
        OrderedDict([('id', str(field['EducationLevelID'])),
                     ('type', tax_type['utbildningsniva']),
                     ('label', field['Term']),
                     ('num_id', int(field['EducationLevelID']))])
        for field in taxonomy_education_level
    }
    return education_level


def create_valuestore_education_field(taxonomy_education_field):
    education_field = {
        field['EducationFieldID']:
        OrderedDict([('id', str(field['EducationFieldID'])),
                     ('type', tax_type['utbildningsinriktning']),
                     ('label', field['Term']),
                     ('description', field['Description']),
                     ('num_id', int(field['EducationFieldID']))])
        for field in taxonomy_education_field
    }
    return education_field


def create_valuestore_duration(taxonomy_duration):
    duration = {
        field['EmploymentDurationID']:
        OrderedDict([('id', str(field['EmploymentDurationID'])),
                     ('type', tax_type['varaktighet']),
                     ('label', field['Term']),
                     ('EURESCode', field['EURESCode']),
                     ('num_id', int(field['EmploymentDurationID']))])
        for field in taxonomy_duration
    }
    return duration


def create_valuestore_occupation_experience(taxonomy_occupation_experience):
    occupation_experience = {
        field['OccupationExperienceYearID']:
        OrderedDict([('id', str(field['OccupationExperienceYearID'])),
                     ('type', tax_type['erfarenhetsniva']),
                     ('label', field['ExperienceYearCandidate']),
                     ('num_id', int(field['OccupationExperienceYearID']))])
        for field in taxonomy_occupation_experience
    }
    return occupation_experience


def fetch_full_taxonomy():
    try:
        taxonomy_jobfields = taxonomy_service.get_all_job_fields()
        taxonomy_jobgroups = taxonomy_service.get_all_job_groups()
        taxonomy_jobterms = taxonomy_service.get_all_job_terms()
        taxonomy_countries = taxonomy_service.get_all_countries()
        taxonomy_regions = taxonomy_service.get_all_regions()
        taxonomy_municipalities = taxonomy_service.get_all_municipalities()
        taxonomy_languages = taxonomy_service.get_all_languages()
        taxonomy_work_time_extent = taxonomy_service.get_all_work_time_extent()
        taxonomy_skills = taxonomy_service.get_all_skills()
        taxonomy_employmenttypes = taxonomy_service.get_all_employment_types()
        taxonomy_drivinglicence = taxonomy_service.get_all_driving_licences()
        taxonomy_wagetype = taxonomy_service.get_all_wage_type()
        taxonomy_education_level = taxonomy_service.get_all_education_levels()
        taxonomy_education_field = taxonomy_service.get_all_education_fields()
        taxonomy_duration = taxonomy_service.get_all_duration()
        taxonomy_occupation_experience = taxonomy_service.get_all_occupation_experience()
    except Exception as e:
        log.error('Failed to fetch valuesets from Taxonomy Service', e)
        raise
    # Load places
    file_places = json.loads(resource_string('importers.taxonomy.resources',
                                             'platser.json').decode('utf-8'))
    (valuestore_jobterm,
     valuestore_jobgroup, valuestore_jobfield) = create_valuestore_jobs(
         taxonomy_jobterms, taxonomy_jobgroups, taxonomy_jobfields)
    (valuestore_places, valuestore_municipalities,
     valuestore_regions,
     valuestore_countries) = create_valuestore_geo(file_places,
                                                   taxonomy_municipalities,
                                                   taxonomy_regions,
                                                   taxonomy_countries)
    valuestore_languages = create_valuestore_languages(taxonomy_languages)
    valuestore_work_time_extent = create_valuestore_work_time_extent(
        taxonomy_work_time_extent)
    valuestore_skills = create_valuestore_skills(taxonomy_skills)
    valuestore_employmenttypes = create_valuestore_employment_types(
        taxonomy_employmenttypes)
    valuestore_drivinglicences = create_valuestore_driving_licence(
        taxonomy_drivinglicence)
    valuestore_wagetype = create_valuestore_wagetype(taxonomy_wagetype)
    valuestore_education_level = create_valuestore_education_level(taxonomy_education_level)
    valuestore_education_field = create_valuestore_education_field(taxonomy_education_field)
    valuestore_duration = create_valuestore_duration(taxonomy_duration)
    valuestore_occupation_experience = create_valuestore_occupation_experience(taxonomy_occupation_experience)
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
        elastic.create_index(indexname, settings.TAXONOMY_INDEX_CONFIGURATION)
        elastic.bulk_index(values, indexname, ['type', 'id'])
    except Exception as e:
        log.error('Failed to load values into search engine', e)
        raise
    # Create and/or assign index to taxonomy alias and
    # assign old index to archive alias
    try:
        if (elastic.alias_exists(settings.ES_TAX_INDEX_ALIAS)):
            alias = elastic.get_alias(settings.ES_TAX_INDEX_ALIAS)
            elastic.update_alias(
                indexname, list(alias.keys()), settings.ES_TAX_INDEX_ALIAS)
            if (not indexexists):
                if (elastic.alias_exists(settings.ES_TAX_ARCHIVE_ALIAS)):
                    elastic.add_indices_to_alias(list(alias.keys()),
                                                 settings.ES_TAX_ARCHIVE_ALIAS)
                else:
                    elastic.put_alias(
                        list(alias.keys()), settings.ES_TAX_ARCHIVE_ALIAS)
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
