def get_compound_nouns(en_doc, token, token_text):

    """
    Recursively find the left and right compound nouns
    """

    parent_token = token

    # If previous token is a compound noun
    while token.i > 0 and en_doc[token.i - 1].dep_ == "compound":
        token_text = en_doc[token.i - 1].text + " " + token_text
        token = en_doc[token.i - 1]
        # if the compound noun has any adjective modifier
        token_text = get_adj_phrase(token, token_text)

    token = parent_token

    # If next token is a compound noun
    while token.i < len(en_doc) - 1 and en_doc[token.i + 1].dep_ == "compound":
        token_text = token_text + " " + en_doc[token.i + 1].text
        token = en_doc[token.i + 1]
        # if the compound noun has any adjective modifier
        token_text = get_adj_phrase(token, token_text)

    # NOTE: Can token.shape_ == Xxxx... or XXXX... token.ent_iob_ help us here ...?

    return token_text


def get_adj_phrase(token, token_text):

    #To fetch all the adjectives describing the noun
    # amod: An adjectival modifier of a noun is any adjectival phrase that serves to modify the meaning of the noun.
    # ccomp: A clausal complement of a verb or adjective is a dependent clause which is a core argument.
    #        That is, it functions like an object of the verb, or adjective.
    # acomp: An adjectival complement of a verb is an adjectival phrase which functions as the complement

    for child in token.children:
        if child.dep_ == "amod" or child.dep_ == "acomp" or child.dep_ == "ccomp":  # not for how many
            if child.text != "much" and child.text != "many":
                token_text = child.lemma_ + " " + token_text
    return token_text


def get_root_phrase(token, keywords):

    # xcomp: An open clausal complement (xcomp) of a verb or an adjective is a predicative or clausal complement
    #        without its own subject.

    for child in token.children:
        if child.dep_ == "acomp" or child.dep_ == "xcomp" or child.dep_ == "ccomp":
            keywords.append(child.lemma_)
    return keywords


def get_noun_chunk(sentence, en_doc, keywords):

    root_word = ""

    for token in sentence:

        # If is Noun/Proper Noun, be it Singular or Plural
        if token.tag_ == "NN" or token.tag_ == "NNP" or token.tag_ == "NNPS" or token.tag_ == "NNS":
            # If the Noun itself is not a compound Noun then we can find its compound Nouns
            if token.dep_ != "compound":
                token_text = get_compound_nouns(en_doc, token, token.text)
                keywords.append(token_text)

        if token.tag_ == "JJ" and token.dep_ == "attr":
            token_text = get_compound_nouns(en_doc, token, token.text)
            token_text = get_adj_phrase(token, token_text)
            keywords.append(token_text)

        # If is a Cardinal Number & dependency is numeric modifier
        # nummod : A numeric modifier of a noun is any number phrase that
        #          serves to modify the meaning of the noun with a quantity.
        if token.dep_ == "nummod" or token.tag_ == "CD":
            token_text = token.text

            if token.i > 0:
                # If previous token is Adjective, the adjective is liked with the cardinal number
                if en_doc[token.i - 1].tag_ == "JJ":
                    token_text = en_doc[token.i - 1].text + " " + token.text

            if token.i < len(en_doc) - 1:
                # If next token is Adjective
                if en_doc[token.i + 1].tag_ == "JJ":
                    token_text = token.text + " " + en_doc[token.i + 1].text

            keywords.append(token_text)

        # Extracts the root word of sentence
        if token.dep_ == "ROOT":
            root_word = token.lemma_
            keywords = get_root_phrase(token, keywords)

    return root_word, keywords


def extract_features(question_type, en_doc, show_debug=False):

    keywords = []

    for sentence in en_doc.sents:
        root, keywords = get_noun_chunk(sentence, en_doc, keywords)
        keywords.append(root)

    return keywords
