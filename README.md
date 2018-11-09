# kandidat-importer
Elasticsearch importscript för kandidat-söktjänster.

## Användning
Script som är tänkta att köras med olika intervall, i regel via cron, för att ladda in diverse olika typer av data till Elasticsearch.

## Installation
### Exempel virtualenv:

    $ workon <virtuell miljö för huvudapplikationen>
    $ python setup.py develop

### Exempel anaconda:

    $ source activate <virtuell miljö för huvudapplikationen>
    $ python setup.py develop
    

#### Användning

    $ import-kandidater
    
