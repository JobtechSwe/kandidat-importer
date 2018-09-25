import json, pytest, sys
from importers.platsannons import converter
from importers.repository import taxonomy


@pytest.mark.parametrize("annons_key", ['anstallningstyp', '', None])
@pytest.mark.parametrize("message_key", ('anstallningTyp','mkey', '', None) )
@pytest.mark.parametrize("message_dict", [{"anstallningTyp": {"varde": "1"}}, {"anstallningTyp": {"varde": "2"}}
                                          ,{'': {'varde': 'v2'}}, {'mkey': {'EJvarde': 'v1'}}
                                          ,{}, None ] )
def test_expand_taxonomy_value(annons_key, message_key, message_dict):
    print('============================', sys._getframe().f_code.co_name, '============================ ')
    d =  converter._expand_taxonomy_value(annons_key, message_key, message_dict)
    print(d)
    if not message_dict:
        assert d is None
        return
    message_value = message_dict.get(message_key, {}).get('varde')
    if message_value :
        assert d['kod'] == message_value
        assert d['term'] == taxonomy.get_term(annons_key, message_value)
    else:
        assert d is None

def test_convert_message(msg): # see msg fixture in conftest.py
    print('============================', sys._getframe().f_code.co_name, '============================ ')
    print(msg)
    annons = converter.convert_message(msg)
    print(annons)
    if 'annons' in msg and 'version' in msg:
        print("Message is not in correct format, going to be formatted...")
        message = msg['annons']
        assert annons['id'] == message.get('annonsId')
        assert annons['rubrik'] == message.get('annonsrubrik')
        assert annons['sista_ansokningsdatum'] == converter._isodate(message.get('sistaAnsokningsdatum'))
        assert annons['antal_platser'] == message.get('antalPlatser')
        assert annons['beskrivning'] == {
            'information': message.get('ftgInfo'),
            'behov': message.get('beskrivningBehov'),
            'krav': message.get('beskrivningKrav'),
            'villkor': message.get('villkorsbeskrivning'),
            'annonstext': message.get('annonstext'),
        }
        assert annons['arbetsplats_id'] == message.get('arbetsplatsId')
        assert annons['anstallningstyp'] == converter._expand_taxonomy_value('anstallningstyp','anstallningTyp', message)
        assert annons['lonetyp'] == converter._expand_taxonomy_value('lonetyp', 'lonTyp', message)
        assert annons['varaktighet'] == converter._expand_taxonomy_value('varaktighet', 'varaktighetTyp', message)
        assert annons['arbetstidstyp'] == converter._expand_taxonomy_value('arbetstidstyp', 'arbetstidTyp', message)
        assert annons['arbetsomfattning'] == {
            'min': message.get('arbetstidOmfattningFran'),
            'max': message.get('arbetstidOmfattningTill')
        }
        assert annons['tilltrade'] == message.get('tilltrade')
        assert annons['arbetsgivare'] == {
            'id': message.get('arbetsgivareId'),
            'telefonnummer': message.get('telefonnummer'),
            'epost': message.get('epost'),
            'webbadress': message.get('webbadress'),
            'organisationsnummer': message.get('organisationsnummer'),
            'namn': message.get('arbetsgivareNamn'),
            'arbetsplats': message.get('arbetsplatsNamn')
        }
        assert annons['ansokningsdetaljer'] == {
            'information': message.get('informationAnsokningssatt'),
            'referens': message.get('referens'),
            'epost': message.get('ansokningssattEpost'),
            'via_af': message.get('ansokningssattViaAF'),
            'webbadress': message.get('ansokningssattWebbadress'),
            'annat': message.get('ansokningssattAnnatSatt')
        }
        assert annons['erfarenhet_kravs'] is not message.get('ingenErfarenhetKravs', False)
        assert annons['egen_bil'] == message.get('tillgangTillEgenBil', False)
        if message.get('korkort') :
            assert annons['korkort_kravs'] is True
        else:
            assert annons['korkort_kravs'] is False

        #TODO add test for yrkesroll
        if message.get('arbetsplatsadress'):
            print(annons['arbetsplatsadress'])
            arbplatsmessage = message.get('arbetsplatsadress')
            assert annons['arbetsplatsadress'] == {
                'kommun': arbplatsmessage.get('kommun', {}).get('varde'),
                'lan': arbplatsmessage.get('lan', {}).get('varde'),
                'gatuadress': arbplatsmessage.get('gatuadress'),
                'postnummer': arbplatsmessage.get('postnr'),
                'postort': arbplatsmessage.get('postort'),
                'latitud': arbplatsmessage.get('latitud'),
                'longitud': arbplatsmessage.get('longitud')
            }
        else:
            assert annons['arbetsplatsadress'] == {'kommun': None, 'lan': None, 'gatuadress': None, 'postnummer': None,
                                                   'postort': None, 'latitud': None, 'longitud': None}
            
    else:
        print("Message is already in correct format")
        assert msg == annons


@pytest.mark.parametrize("parsing_date", ['180924-00:00', '20180924T', 'mon sep 24', '00:00:00' ])
@pytest.mark.parametrize("not_parsing_date", ['fdsasfd', '2099-13-32', '18-09-24:01:01', '', None])
def test_isodate(parsing_date, not_parsing_date):
    assert converter._isodate(not_parsing_date) is None
    assert converter._isodate(parsing_date) is not None