from es_operate import ElasticSearchOperate

def search_rank(query):
    es = ElasticSearchOperate()
    result_all = es.search_fact(query)
    return result_all
