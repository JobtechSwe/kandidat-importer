import logging
from flashtext import KeywordProcessor
from importers.repository import elastic


log = logging.getLogger(__name__)

log.info("Initalizing keyword processor")
keyword_processor = KeywordProcessor()
[keyword_processor.add_non_word_boundary(token) for token in list('åäöÅÄÖ')]
for t in elastic.load_terms('KOMPETENS'):
    keyword_processor.add_keyword(t['term'], t)
for t in elastic.load_terms('YRKE'):
    keyword_processor.add_keyword(t['term'], t)


def enrich(annonser):
    results = []
    for annons in annonser:
        text = annons.get('content', {}).get('text', '')
        kwords = keyword_processor.extract_keywords(text)
        annons['skills'] = list(set([ont['term'] for ont in kwords if ont['type'] == 'KOMPETENS']))
        annons['occupations'] = list(set([ont['term'] for ont in kwords if ont['type'] == 'YRKE']))
        results.append(annons)

    return results

