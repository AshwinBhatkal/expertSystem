#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import sys
import logging

import spacy

from flask import Flask, render_template
import os, subprocess

from question_classifier import classify_question
from feature_extractor import extract_features
from query_const import construct_query
from genericScraper.scraper import crawlPages
from doc_search_rank import search_rank
from candidate_ans import get_candidate_answers
from constants import EN_MODEL_MD, EN_MODEL_DEFAULT
from feedback import upRank

app = Flask(__name__)

def get_nlp(language, lite, lang_model=""):

    err_msg = "Language model {0} not found. Please, refer https://spacy.io/usage/models"

    nlp = None

    if not lang_model == "" and not lang_model == "en":

        try:
            nlp = spacy.load(lang_model)
        except ImportError:
            print(err_msg.format(lang_model))
            raise

    elif language == 'en':

        if lite:
            nlp = spacy.load(EN_MODEL_DEFAULT)
        else:
            try:
                nlp = spacy.load(EN_MODEL_MD)

            except ImportError:
                print(err_msg.format(EN_MODEL_MD))
                print('Using default language model')
                nlp = spacy.load(EN_MODEL_DEFAULT)

    elif not language == 'en':
        print('Currently only English language is supported. '
              'Please contribute to https://github.com/5hirish/adam_qas to add your language.')
        sys.exit(0)

    return nlp


class QasInit:

    nlp = None
    language = "en"
    lang_model = None
    lite = False

    question_doc = None

    question_class = ""
    question_keywords = None
    query = None

    candidate_answers = None

    def __init__(self, language, lite, lang_model=""):
        self.language = language
        self.lite = lite
        self.lang_model = lang_model
        self.nlp = get_nlp(self.language, self.lite, self.lang_model)

    def get_question_doc(self, question):

        self.question_doc = self.nlp(u'' + question)

        return self.question_doc

    def process_question(self):
        # self.question_class = classify_question(self.question_doc)

        self.question_keywords = extract_features(self.question_class, self.question_doc)

        self.query = construct_query(self.question_keywords, self.question_doc)

    def process_answer(self):

        # crawlPage()
        top_facts = search_rank(self.query)

        return top_facts

@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/question/<name>')
def get_question(name):
    qas.get_question_doc(name)
    qas.process_question()
    answers = qas.process_answer()
    if not answers:
        return "No answer"
    final_answer = "The possible answers for your query are as below :\n"
    num = 1
    for answer in answers:
        final_answer += str(num) + " . ['" + answer[0] + "', '" + answer[1]+ "]\n"
        num += 1
    # return "The possible answers for your query are as below : 1 . ['f-a-5mIBNuJyU2brNiFk', 'Angular is the underlying framework that powers Ionic.'] 2 . ['aua-5mIBNuJyU2brNiEl', 'Check out “Where does the Ionic Framework fit in?” to get a good understanding of Ionic’s core philosophy and goals..'] 3 . ['tua-5mIBNuJyU2brpiHD', 'Ionic comes with the same 700+ Ionicons icons we’ve all come to know and love..'] 4 . ['uOa-5mIBNuJyU2brpiHI', 'Active icons are typically full and thick, where as inactive icons are outlined and thin.'] 5 . ['-Oa-5mIBNuJyU2brrSH7', 'Storage uses a variety of storage engines underneath, picking the best one available depending on the platform..']"

    return final_answer

@app.route('/feedback/<id>')
def get_feedback(id):
    return subprocess.check_output(['python3', 'feedback.py', id])

if __name__ == '__main__':
    logging.getLogger('gensim').setLevel(logging.CRITICAL) # to override gensim warning error message
    qas = QasInit(language="en", lite=False, lang_model="en")
    # crawlPages() # run this for the first run
    app.run(host='localhost', port=8080)
