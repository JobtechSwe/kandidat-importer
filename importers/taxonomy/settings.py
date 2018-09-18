import os

# Taxonomyservice settings
TAXONOMY_SERVICE_URL = os.getenv("TAXONOMY_SERVICE_URL",
                                 "http://wstaxonomiservice.ams.se/TaxonomiService.asmx")
LANGUAGE_CODE_SE = 502
COUNTRY_CODE_SE = 199

# Elasticsearch settings
ES_TAX_INDEX_BASE = os.getenv("ES_TAX_INDEX_BASE", "taxonomy-")
ES_TAX_INDEX_ALIAS = os.getenv("ES_TAX_INDEX_ALIAS", "taxonomy")
ES_TAX_ARCHIVE_ALIAS = os.getenv("ES_TAX_ARCHIVE_ALIAS", "taxonomy-archive")

# Query parameters
OCCUPATION = 'yrke'
GROUP = 'yrkesgrupp'
FIELD = 'yrkesomrade'
SKILL = 'kompetens'
LANGUAGE = 'sprak'
MUNICIPALITY = 'kommunkod'
REGION = 'lanskod'
WORKTIME_EXTENT = 'arbetstidsomfattning'

taxonomy_type = {
    OCCUPATION: 'jobterm',
    GROUP: 'jobgroup',
    FIELD: 'jobfield',
    SKILL: 'skill',
    LANGUAGE: 'language',
    MUNICIPALITY: 'municipality_code',
    REGION: 'region_code',
    WORKTIME_EXTENT: 'worktime_extent'
}
