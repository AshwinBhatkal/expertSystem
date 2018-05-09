from query_container import QueryContainer

def get_conjuncts(token):

    """
    A conjunct is the relation between two elements connected by a coordinating conjunction, such as and, or, etc.
     We treat conjunctions asymmetrically: The head of the relation is the first conjunct and all the other conjuncts
      depend on it via the conj relation.

    Coordinating Conjunction: and, or, but, yet, so, nor, for.
    Correlative Conjunctions: either...or, whether...or, not only...but also
    """

    parent = token.head
    conj = [parent.text]

    for child in parent.children:
        if child.dep_ == "conj":
            conj.append(child.text)

    return conj


def get_query(sentence, feature_list):

    """
    This function sequentially adds the query components to the structured query.
    """

    query_container = QueryContainer()
    query_container.add_features(feature_list)

    conjunct_list = []
    neg_list = []
    mark_list = []

    for token in sentence:

        # cc: A cc is the relation between a conjunct and a preceding coordinating conjunction.
        if token.dep_ == "cc":
            conjunct_list.append(get_conjuncts(token))
            conjunct_list.append(token.text)
            query_container.add_coordinating_conjunct(token.text)

        # neg: The negation modifier is the relation between a negation word and the word it modifies.
        if token.dep_ == "neg":
            if token.i > token.head.i:
                neg_list.append([token.text, token.head.text])
            else:
                neg_list.append([token.head.text, token.text])

        # mark: A marker is the word introducing a finite clause subordinate to another clause.
        if token.dep_ == "mark":
            if token.i > token.head.i:
                mark_list.append([token.text, token.head.text])
            else:
                mark_list.append([token.head.text, token.text])

    query_container.add_conjunctions(conjunct_list)
    query_container.add_negations(neg_list)
    query_container.add_markers(mark_list)

    return query_container


def construct_query(features_list, en_doc):
    query_constructed_obj = []

    for sentence in en_doc.sents:
        query_constructed_obj.append(get_query(sentence, features_list))

    return query_constructed_obj
