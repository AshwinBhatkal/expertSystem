import sys
from es_operate import ElasticSearchOperate

def upRank(fact_id):
    es = ElasticSearchOperate()
    es.upRankFact(fact_id)

if __name__ == "__main__":
    upRank(sys.argv[1])
