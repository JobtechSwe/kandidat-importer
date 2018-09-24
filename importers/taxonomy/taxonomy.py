from zeep import Client
from zeep.transports import Transport
from zeep.helpers import serialize_object
from importers.taxonomy import settings

transport = Transport(timeout=2000, operation_timeout=5000)
wsdl = settings.TAXONOMY_SERVICE_URL + "?WSDL"
client = Client(wsdl=wsdl, transport=transport)
# This step is necessary to handle incorrectly
# specified service url in the open api.
service = client.create_service("{urn:ams.se:Taxonomy}TaxonomiServiceSoap12",
                                settings.TAXONOMY_SERVICE_URL)


def get_all_job_terms():
    result = service.GetAllOccupationNames(settings.LANGUAGE_CODE_SE)
    return serialize_object(result)


def get_all_skills():
    result = service.GetAllSkills(settings.LANGUAGE_CODE_SE)
    return serialize_object(result)


def get_all_job_groups():
    result = service.GetAllLocaleGroups(settings.LANGUAGE_CODE_SE)
    return serialize_object(result)


def get_all_job_fields():
    result = service.GetAllLocaleFields(settings.LANGUAGE_CODE_SE)
    return serialize_object(result)


def get_all_languages():
    result = service.GetAllLanguages(settings.LANGUAGE_CODE_SE)
    return serialize_object(result)


def get_all_municipalities():
    result = service.GetAllMunicipalities(settings.LANGUAGE_CODE_SE)
    return serialize_object(result)


def get_all_regions():
    result = service.GetEURegionsByCountryID(
        settings.LANGUAGE_CODE_SE,
        settings.COUNTRY_CODE_SE)
    return serialize_object(result)


def get_all_work_time_extent():
    result = service.GetAllWorkTimeExtents(settings.LANGUAGE_CODE_SE)
    return serialize_object(result)


def get_taxonomy_version():
    result = service.GetVersionInformations()
    return serialize_object(result)


def get_all_countries():
    r = service.GetAllCountries(settings.LANGUAGE_CODE_SE)
    return serialize_object(r)


def get_all_education_levels():
    pass
