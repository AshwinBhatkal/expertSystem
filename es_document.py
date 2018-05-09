
from es_config import __content__, __title__, __rank__

class ElasticSearchDocument:

    _source = None

    def __init__(self, id, source, score=0):
        self._source = dict()
        self._source['id'] = id
        self._source['score'] = score
        self._source[__title__] = source[__title__]
        self._source[__content__] = source[__content__]
        self._source[__rank__] = source[__rank__]

    def get_title(self):
        return self._source[__title__]

    def get_content(self):
        return self._source[__content__]

    def get_rank(self):
        return self._source[__rank__]
