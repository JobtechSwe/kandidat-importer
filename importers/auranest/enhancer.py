import logging
import re
import time
import multiprocessing
from io import StringIO
from importers.repository import elastic

log = logging.getLogger(__name__)


def _build_pattern(ontology_type):
    start = int(round(time.time() * 1000))
    print("Building regex pattern for '%s'" % ontology_type)
    ontology_words = elastic.load_terms(ontology_type)
    pattern = ''
    first = True
    count = 0
    for word in ontology_words:
        if not first:
            pattern += '|'
        if '+' in word or '#' in word:
            pattern += word.replace('+', '\\+')
        else:
            pattern += '\\b'+word+'\\b'
        first = False
        count += 1
    cp = re.compile(pattern, re.I)
    now = int(round(time.time() * 1000))
    print("Completed %s pattern with %d concepts in %d milliseconds."
          % (ontology_type, count, (now-start)))
    return cp


_yrkes_pattern = _build_pattern('YRKE')
_kompetens_pattern = _build_pattern('KOMPETENS')


def enrich_ad(annons, skill_pattern, occ_pattern, jobnr):
    # print("Enrich ad nr %d (%s) ..." % (jobnr, annons.get('id')))
    text = annons.get('content', {}).get('text', '')
    skills = [c.lower() for c in skill_pattern.findall(text)] if text else []
    jobtitles = [c.lower() for c in occ_pattern.findall(text)] if text else []

    annons['skills'] = skills
    annons['occupations'] = jobtitles

    # print("Done with job nr %d (%s)" % (jobnr, annons.get('id')))
    return annons


def enrich(annonser):
    pool = multiprocessing.Pool(processes=8)
    output = [pool.apply_async(enrich_ad,
                                args=(annonser[i],
                                      _kompetens_pattern,
                                      _yrkes_pattern, i, )) for i in range(len(annonser))]
    results = [p.get() for p in output]

    # print(results)
    return results


if __name__ == '__main__':
    start = int(round(time.time() * 1000))
    print("Match 1")
    r = enrich([{'content': {'text': 'Testar att söka efter Python och Java.'}}])
    print(r)
    now = int(round(time.time() * 1000))
    print("Time elapsed: %d" % (now-start))
    start = int(round(time.time() * 1000))
    print("Match 2")
    r = enrich([{'content': {'text': 'Inköpare - Tillverkningsbolag Tekniskt inköpare för produktion Familjärt bolag med högt i tak Om vår klient Vår kund är i grunden ett Svenskt tillverkningsföretag placerat 10 minuter ifrån T- Centralen. Deras kontor ligger vägg i vägg med produktionslinjen och de anställer cirka 100 personer. Behovet är permanent men du kommer att börja som konsult via Michael Page. Arbetsbeskrivning I din roll som Inköpare kommer du att köpa in material till produktionen. Detta inkluderar både operativt inköp samt leverantörsutveckling. Du kommer att arbeta nära inköpschefen för att tillsammans driva inköpsenheten med kostnadsbesparingar och förbättrade leveranser. Några av dina arbetsuppgifter kommer att inkludera: - Köpa in material till produktion - Lägga prognos och leveransplan - Utveckling av dina leverantörer på leveranskvalitét, pris, logistik etc genom personliga möten och avtal - Uppföljning av reklamationer - Lageroptimering - Framtagning av inköpsstatistik - Övergripande förbättringsåtgärder och stöd till inköpschef Arbetsspråket är internationellt vilket inkluderar flytande kunskaper i både tal och skrift på Svenska och Engelska. Vem söer vi? För att bli framgångsrik i rollen krävs att du: - Har minst 3-4 års erfarenhet av liknande roll - Akademisk examen inom Inköp eller Ekonomi - Gärna ha arbetat i SAP - Trivs i att bygga kundrelationer - Vill utvecklas och ta stort personligt ansvar Nyckelord: Procurement, Purchase, Teknisk Inköpare Övrigt Är du intresserad av att arbeta med inköp för en internationell organisation? Skicka in din ansökan eller ring Henric på Michael Page (+46 8 545 270 40) redan nu! Trots att rollen är långsiktig letar vi efter att hitta rätt kandidat ASAP..'}}])
    print(r)
    now = int(round(time.time() * 1000))
    print("Time elapsed: %d" % (now-start))
    start = int(round(time.time() * 1000))
    print("Match 2")
    r = enrich([{'content': {'text': 'Testar att söka efter Python och Java.'}},{'content': {'text': 'Inköpare - Tillverkningsbolag Tekniskt inköpare för produktion Familjärt bolag med högt i tak Om vår klient Vår kund är i grunden ett Svenskt tillverkningsföretag placerat 10 minuter ifrån T- Centralen. Deras kontor ligger vägg i vägg med produktionslinjen och de anställer cirka 100 personer. Behovet är permanent men du kommer att börja som konsult via Michael Page. Arbetsbeskrivning I din roll som Inköpare kommer du att köpa in material till produktionen. Detta inkluderar både operativt inköp samt leverantörsutveckling. Du kommer att arbeta nära inköpschefen för att tillsammans driva inköpsenheten med kostnadsbesparingar och förbättrade leveranser. Några av dina arbetsuppgifter kommer att inkludera: - Köpa in material till produktion - Lägga prognos och leveransplan - Utveckling av dina leverantörer på leveranskvalitét, pris, logistik etc genom personliga möten och avtal - Uppföljning av reklamationer - Lageroptimering - Framtagning av inköpsstatistik - Övergripande förbättringsåtgärder och stöd till inköpschef Arbetsspråket är internationellt vilket inkluderar flytande kunskaper i både tal och skrift på Svenska och Engelska. Vem söer vi? För att bli framgångsrik i rollen krävs att du: - Har minst 3-4 års erfarenhet av liknande roll - Akademisk examen inom Inköp eller Ekonomi - Gärna ha arbetat i SAP - Trivs i att bygga kundrelationer - Vill utvecklas och ta stort personligt ansvar Nyckelord: Procurement, Purchase, Teknisk Inköpare Övrigt Är du intresserad av att arbeta med inköp för en internationell organisation? Skicka in din ansökan eller ring Henric på Michael Page (+46 8 545 270 40) redan nu! Trots att rollen är långsiktig letar vi efter att hitta rätt kandidat ASAP..'}}])
    print(r)
    now = int(round(time.time() * 1000))
    print("Time elapsed: %d" % (now-start))
