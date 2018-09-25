# elastic-importer
Elasticsearch importscript för kandidat- och annons-söktjänster.

## Användning
Script som är tänkta att köras med olika intervall, i regel via cron, för att ladda in diverse olika typer av data till Elasticsearch.

## Installation
### Exempel virtualenv:

    $ workon <virtuell miljö för huvudapplikationen>
    $ python setup.py develop

### Exempel anaconda:

    $ source activate <virtuell miljö för huvudapplikationen>
    $ python setup.py develop
    

### import-taxonomy
Importerar värdeförråd från Arbetsförmedlingens taxonomitjänst via SOAP. Förutsätter att det finns ett Elasticsearch-cluster att ladda
in datan till. Datat ändras relativt sällan och scriptet bör inte köras mer ofta än dagligen för närvarande.
Följande environmental variabler används:

|Environment variable   | Default value  |
|---|---|
| ES_HOST  | localhost  |
| ES_PORT  | 9200  |
| ES_USER  |   |
| ES_PWD  |   |
| ES_TAX_INDEX_BASE  | taxonomy-  |
| ES_TAX_INDEX_ALIAS  |  taxonomy |
| ES_TAX_ARCHIVE_ALIAS  |  taxonomy-archive |
| TAXONOMY_SERVICE_URL  | http://api.arbetsformedlingen.se/taxonomi/v0/TaxonomiService.asmx  |


#### Användning

    $ import-taxonomy
    
### import-kandidater
TBD
#### Användning
TBD

### import-platsannonser
TBD
#### Användning
TBD

### import-auranest
TBD
#### Användning
TBD
