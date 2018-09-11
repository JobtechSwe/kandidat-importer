from zeep import Client
from zeep.transports import Transport
from zeep.helpers import serialize_object
from importers.taxonomy import settings

transport = Transport(timeout=2000, operation_timeout=5000)
wsdl = settings.TAXONOMY_SERVICE_URL + "?WSDL"
client = Client(wsdl=wsdl, transport=transport)

def get_all_job_terms():
    r = client.service.GetAllOccupationNames(settings.LANGUAGE_CODE_SE)
    return serialize_object(r)

def get_all_skills():
    return serialize_object(client.service.GetAllSkills(settings.LANGUAGE_CODE_SE))

def get_all_job_groups():
    return serialize_object(client.service.GetAllLocaleGroups(settings.LANGUAGE_CODE_SE))

def get_all_job_fields():
    return serialize_object(client.service.GetAllLocaleFields(settings.LANGUAGE_CODE_SE))

def get_all_languages():
    return serialize_object(client.service.GetAllLanguages(settings.LANGUAGE_CODE_SE))

def get_all_municipalities():
    return serialize_object(client.service.GetAllMunicipalities(settings.LANGUAGE_CODE_SE))

def get_all_regions():
    return serialize_object(client.service.GetEURegionsByCountryID(settings.LANGUAGE_CODE_SE, settings.COUNTRY_CODE_SE))

def get_all_work_time_extent():
    return serialize_object(client.service.GetAllWorkTimeExtents(settings.LANGUAGE_CODE_SE))

def get_taxonomy_version():
    r = client.service.GetVersionInformations()
    return serialize_object(r)
