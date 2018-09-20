import json
from importers.repository import taxonomy


def convert_message(msg):
    message_envelope = json.loads(msg) if isinstance(msg, str) else msg
    if 'annons' in message_envelope and 'version' in message_envelope:
        message = message_envelope['annons']
        annons = dict()
        annons['id'] = message.get('annonsId')
        annons['rubrik'] = message.get('annonsrubrik')
        annons['sista_ansokningsdatum'] = message.get('sistaAnsokningsdatum')
        annons['antal_platser'] = message.get('antalPlatser')
        annons['beskrivning'] = {
            'information': message.get('ftgInfo'),
            'behov': message.get('beskrivningBehov'),
            'krav': message.get('beskrivningKrav'),
            'villkor': message.get('villkorsbeskrivning'),
            'annonstext': "%s\n%s\n%s\n%s" % (message.get('ftgInfo', ''),
                                              message.get('beskrivningBehov', ''),
                                              message.get('beskrivningKrav', ''),
                                              message.get('villkorsbeskrivning', ''))
        }
        annons['arbetsplats_id'] = message.get('arbetsplatsId')
        annons['anstallningstyp'] = _expand_taxonomy_value('anstallningstyp',
                                                           'anstallningTyp',
                                                           message)
        annons['lonetyp'] = _expand_taxonomy_value('lonetyp', 'lonTyp', message)
        annons['varaktighet'] = _expand_taxonomy_value('varaktighet',
                                                       'varaktighetTyp', message)
        annons['arbetstidstyp'] = _expand_taxonomy_value('arbetstidstyp',
                                                         'arbetstidTyp', message)
        annons['arbetsomfattning'] = {
            'min': message.get('arbetstidOmfattningFran'),
            'max': message.get('arbetstidOmfattningTill')
        }
        annons['tilltrade'] = message.get('tilltrade')
        annons['arbetsgivare'] = {
            'id': message.get('arbetsgivareId'),
            'telefonnummer': message.get('telefonnummer'),
            'epost': message.get('epost'),
            'webbadress': message.get('webbadress'),
            'organisationsnummer': message.get('organisationsnummer'),
            'namn': message.get('arbetsgivareNamn'),
            'arbetsplats': message.get('arbetsplatsNamn')
        }
        annons['ansokningsdetaljer'] = {
            'information': message.get('informationAnsokningssatt'),
            'referens': message.get('referens'),
            'epost': message.get('ansokningssattEpost'),
            'via_af': message.get('ansokningssattViaAF'),
            'webbadress': message.get('ansokningssattWebbadress'),
            'annat': message.get('ansokningssattAnnatSatt')
        }
        annons['erfarenhet_kravs'] = not message.get('ingenErfarenhetKravs', False)
        annons['egen_bil'] = message.get('tillgangTillEgenBil', False)
        if message.get('korkort', []):
            annons['korkort_kravs'] = True
        else:
            annons['korkort_kravs'] = False
        if 'yrkesroll' in message:
            yrkesroll = taxonomy.get_entity('yrkesroll',
                                            message.get('yrkesroll', {}).get('varde'))
            if yrkesroll:
                yrkesgrupp = yrkesroll.pop('parent')
                yrkesomrade = yrkesgrupp.pop('parent')

                annons['yrkesroll'] = {'kod': yrkesroll['id'],
                                       'term': yrkesroll['label']}
                annons['yrkesgrupp'] = {'kod': yrkesgrupp['id'],
                                        'term': yrkesgrupp['label']}
                annons['yrkesomrade'] = {'kod': yrkesomrade['id'],
                                         'term': yrkesomrade['label']}
        arbplatsmessage = message.get('arbetsplatsadress', {})
        annons['arbetsplatsadress'] = {
            'kommun': arbplatsmessage.get('kommun', {}).get('varde'),
            'lan': arbplatsmessage.get('lan', {}).get('varde'),
            'gatuadress': arbplatsmessage.get('gatuadress'),
            'postnummer': arbplatsmessage.get('postnr'),
            'postort': arbplatsmessage.get('postort'),
            'latitud': arbplatsmessage.get('latitud'),
            'longitud': arbplatsmessage.get('longitud')
        }
        annons['krav'] = {
            'kompetenser': [
                {'kod': kompetens.get('varde'),
                 'term': taxonomy.get_term('kompetens', kompetens.get('varde')),
                 'vikt': kompetens.get('vikt')
                 }
                for kompetens in
                message.get('kompetenser', []) if kompetens.get('vikt', 0) > 3
            ],
            'sprak': [
                {'kod': sprak.get('varde'),
                 'term': taxonomy.get_term('sprak', sprak.get('varde')),
                 'vikt': sprak.get('vikt')
                 }
                for sprak in message.get('sprak', []) if sprak.get('vikt', 0) > 3
            ],
            'utbildningsniva': [
                {'kod': utbn.get('varde'),
                 'term': taxonomy.get_term('utbildningsniva', utbn.get('varde')),
                 'vikt': utbn.get('vikt')
                 }
                for utbn in
                [message.get('utbildningsniva', {})] if utbn.get('vikt', 0) > 3

            ],
            'utbildningsinriktning': [
                {'kod': utbi.get('varde'),
                 'term': taxonomy.get_term('utbildningsinriktning', utbi.get('varde')),
                 'vikt': utbi.get('vikt')
                 }
                for utbi in
                [message.get('utbildningsinriktning', {})] if utbi.get('vikt', 0) > 3
            ],
            'yrkeserfarenheter': [
                {'kod': yrkerf.get('varde'),
                 'term': taxonomy.get_term('yrkesroll', yrkerf.get('varde')),
                 'vikt': yrkerf.get('vikt')
                 }
                for yrkerf in
                message.get('yrkeserfarenheter', []) if yrkerf.get('vikt', 0) > 3
            ],
        }
        annons['meriterande'] = {
            'kompetenser': [
                {'kod': kompetens.get('varde'),
                 'term': taxonomy.get_term('kompetens', kompetens.get('varde')),
                 'vikt': kompetens.get('vikt')
                 }
                for kompetens in
                message.get('kompetenser', []) if kompetens.get('vikt', 0) < 4
            ],
            'sprak': [
                {'kod': sprak.get('varde'),
                 'term': taxonomy.get_term('sprak', sprak.get('varde')),
                 'vikt': sprak.get('vikt')
                 }
                for sprak in message.get('sprak', []) if sprak.get('vikt', 0) < 4
            ],
            'utbildningsniva': [
                {'kod': utbn.get('varde'),
                 'term': taxonomy.get_term('utbildningsniva', utbn('varde')),
                 'vikt': utbn('vikt')
                 }
                for utbn in
                [message.get('utbildningsniva', {})] if utbn and utbn.get('vikt', 0) < 4
            ],
            'utbildningsinriktning': [
                {'kod': utbi.get('varde'),
                 'term': taxonomy.get_term('utbildningsinriktning', utbi.get('varde')),
                 'vikt': utbi.get('vikt')
                 }
                for utbi in
                [message.get('utbildningsinriktning', {})] if utbi.get('vikt', 0) < 4
            ],
            'yrkeserfarenheter': [
                {'kod': yrkerf.get('varde'),
                 'term': taxonomy.get_term('yrkesroll', yrkerf.get('varde')),
                 'vikt': yrkerf.get('vikt')
                 }
                for yrkerf in
                message.get('yrkeserfarenheter', []) if yrkerf.get('vikt', 0) < 4
            ],
        }
        annons['publiceringsdatum'] = message.get('publiceringsdatum')
        annons['kalla'] = message.get('kalla')
        annons['publiceringskanaler'] = {
            'platsbanken': message.get('publiceringskanalPlatsbanken', False),
            'ais': message.get('publiceringskanalAis', False),
            'platsjournalen': message.get('publiceringskanalPlatsjournalen', False),
        }
        annons['status'] = {
            'publicerad': (message.get('publicerad') == 'PUBLICERAD'),
            'sista_publiceringsdatum': message.get('sistaPubliceringsdatum'),
            'skapad': message.get('skapadTid'),
            'skapad_av': message.get('skapadAv'),
            'uppdaterad': message.get('uppdateradTid'),
            'uppdaterad_av': message.get('uppdateradAv'),
            'anvandarId': message.get('anvandarId'),
        }
        return annons
    else:
        # Message is already in correct format
        return message_envelope


def _expand_taxonomy_value(annons_key, message_key, message_dict):
    message_value = message_dict.get(message_key, {}).get('varde')
    if message_value:
        return {
            'kod': message_value,
            'term': taxonomy.get_term(annons_key, message_value)
        }
    return None
