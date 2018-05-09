from elasticsearch import Elasticsearch
import logging
from es_config import __index_name__, __doc_type__, __title__, __content__,\
    __rank__, __num_shards__, __num_replicas__, __analyzer_en__
"""
Meta Class for managing elasticsearch db connection. It also serves as an singleton
"""

logger = logging.getLogger(__name__)


class ElasticSearchMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(ElasticSearchMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ElasticSearchConn(metaclass=ElasticSearchMeta):
    __hostname__ = 'localhost'
    __port__ = 9200
    __es_conn__ = None
    es_index_config = None

    def __init__(self):
        self.es_index_config = {
            "settings": {
                "number_of_shards": __num_shards__,
                "number_of_replicas": __num_replicas__
            },
            "mappings": {
                __doc_type__: {
                    "properties": {
                        __title__: {
                            "type": "text"
                        },
                        __content__: {
                            "type": "text",
                            "analyzer": __analyzer_en__
                        },
                        __rank__: {
                            "type": "long"
                        }
                    }
                }
            }
        }
        es_host = {'host': self.__hostname__, 'port': self.__port__}
        self.__es_conn__ = Elasticsearch(hosts=[es_host])

    def get_db_connection(self):
        # ignore 400 cause by IndexAlreadyExistsException when creating an index
        res = self.__es_conn__.indices.create(index=__index_name__, body=self.es_index_config, ignore=400)
        if 'error' in res and res['status'] == 400:
            logger.debug("Index already exists")
        elif res['acknowledged'] and res['index'] == __index_name__:
            # logger.debug("Index Created")
            pass
        else:
            logger.error("Index creation failed")

        return self.__es_conn__
