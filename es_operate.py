from datetime import datetime

from es_connect import ElasticSearchConn
from es_config import __index_name__, __doc_type__, __title__, __content__, __rank__
from query_container import QueryContainer
from es_document import ElasticSearchDocument

def resolve_operator(conj_op):
    if conj_op == "and":
        return "and"
    elif conj_op == "or":
        return "or"


class ElasticSearchOperate:
    es_conn = None

    def __init__(self):
        es = ElasticSearchConn()
        self.es_conn = es.get_db_connection()

    def insert_fact(self, fact):
        fact_body = {
            "title" : "ash",
            "content" : fact,
            "rank" : 0
        }
        res = self.es_conn.index(index=__index_name__, doc_type=__doc_type__, body=fact_body)
        return res['result'] == 'created' or res['result'] == 'updated'

    def upRankFact(self, fact_id):
        body = {
            "script" : {
                "source": "ctx._source.rank += 1",
                "lang": "painless"
            }
        }
        res = self.es_conn.update(index=__index_name__, doc_type=__doc_type__, id=fact_id, body=body)
        return res['result'] == 'created' or res['result'] == 'updated'

    # def update_wiki_article(self, pagid, content):
    #     wiki_body = {
    #         "script": {
    #             "source": "ctx._source." + __wiki_content__ + " = params." + __wiki_content__,
    #             "lang": "painless",
    #             "params": {
    #                 __wiki_content__: content
    #             }
    #         }
    #     }
    #     res = self.es_conn.update(index=__index_name__, doc_type=__doc_type__, id=pagid, body=wiki_body)
    #     return res['result'] == 'updated'

    def search_fact(self, search_query): # used in ranking documents

        search_res = []

        for query in search_query:
            if not isinstance(query, QueryContainer):
                query_cont = QueryContainer(query)
            else:
                query_cont = query
            if isinstance(query_cont, QueryContainer):
                features = query_cont.get_features()
                conjunct = query_cont.get_conjunctions()
                negations = query_cont.get_negations()
                markers = query_cont.get_markers()

                must_match = []
                should_match = []
                must_not_match = []

                if conjunct is not None and len(conjunct) > 0:
                    for index, conj in enumerate(conjunct):
                        if isinstance(conj, list):
                            features = [feat for feat in features if feat not in conj]
                            if index < len(conjunct) - 1:
                                conj_op = conjunct[index + 1]
                                es_operator = resolve_operator(conj_op)
                                must_match_query = {
                                    "match": {
                                        __content__: {
                                            "query": " ".join(conj),
                                            "operator": es_operator
                                        }
                                    }
                                }
                                must_match.append(must_match_query)

                # FIXME: No support for negations with conjunctions

                if negations is not None and len(negations) > 0:
                    for index, negate in enumerate(negations):
                        if isinstance(negate, list):
                            features = [feat for feat in features if feat not in negate]
                            if index < len(negations) - 1:
                                conj_op = negations[index + 1]
                                es_operator = resolve_operator(conj_op)
                                must_not_match_term = {
                                    __content__: {
                                        "query": " ".join(negations[index]),
                                        "operator": es_operator
                                    }
                                }
                                must_not_match.append(must_not_match_term)

                if features is not None and len(features) > 0:
                    must_match_query = {
                        "match": {
                            __content__: {
                                "query": " ".join(features)
                            }
                        }
                    }
                    must_match.append(must_match_query)

                search_body = {
                    "query": {
                        "bool": {
                            "must": must_match,
                            "should": should_match,
                            "must_not": must_not_match,
                        }
                    }
                }

                es_result = self.es_conn.search(index=__index_name__, doc_type=__doc_type__, body=search_body)
                if es_result['hits']['hits'] is not None:
                    es_result_hits = es_result['hits']['hits']
                    es_result_hits = es_result_hits[0:5]

                    es_result_hits = self.sortBasedOnRank(es_result_hits)

                    for result in es_result_hits:

                        search_res_temp = []
                        fact_id = result['_id']
                        # fact_score = result['_score']
                        fact_source = result['_source'] # This contains all the data
                        # es_document = ElasticSearchDocument(fact_id, fact_source, fact_score)

                        search_res_temp.append(fact_id)
                        search_res_temp.append(fact_source[__content__])
                        search_res.append(search_res_temp)

            else:
                raise ValueError("Incorrect Query Type")

        return search_res

    def sortBasedOnRank(self, results):
        for i in range(len(results)):
            for j in range(i,len(results)):
                if results[i]['_source'][__rank__] < results[j]['_source'][__rank__]:
                    temp = results[j]
                    for k in range(j,i,-1):
                        results[k] = results[k-1]
                    results[i] = temp

        return results
