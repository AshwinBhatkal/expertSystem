import os
import pandas

from sklearn.naive_bayes import GaussianNB
from sklearn.svm import LinearSVC
from sklearn.externals import joblib
from scipy.sparse import csr_matrix

from constants import CORPUS_DIR, EN_MODEL_MD
from corpus.data import QUESTION_CLASSIFICATION_TRAINING_DATA, QUESTION_CLASSIFICATION_MODEL

def pre_process(dta):
    return pandas.get_dummies(dta)


def remove_irrelevant_features(df_question):
    df_question_class = df_question.pop('Class')

    df_question.pop('Question')
    df_question.pop('WH-Bigram')

    return df_question_class


def transform_data_matrix(df_question_train, df_question_predict):

    df_question_train_columns = list(df_question_train.columns)
    df_question_predict_columns = list(df_question_predict.columns)

    df_question_trans_columns = list(set(df_question_train_columns + df_question_predict_columns))

    trans_data_train = {}

    for feature in df_question_trans_columns:
        if feature not in df_question_train:
            trans_data_train[feature] = [0 for i in range(len(df_question_train.index))]
        else:
            trans_data_train[feature] = list(df_question_train[feature])

    df_question_train = pandas.DataFrame(trans_data_train)
    df_question_train = csr_matrix(df_question_train)

    trans_data_predict = {}

    for feature in trans_data_train:
        if feature not in df_question_predict:
            trans_data_predict[feature] = 0
        else:
            trans_data_predict[feature] = list(df_question_predict[feature])  # KeyError

    df_question_predict = pandas.DataFrame(trans_data_predict)
    df_question_predict = csr_matrix(df_question_predict)

    return df_question_train, df_question_predict

def _bayes_classifier(X_train, y, X_predict):
    gnb = GaussianNB()
    gnb.fit(X_train, y)
    prediction = gnb.predict(X_predict)
    return prediction


def support_vector_machine(df_question_train, df_question_class, df_question_predict):
    lin_clf = LinearSVC()
    lin_clf.fit(df_question_train, df_question_class)
    prediction = lin_clf.predict(df_question_predict)
    return prediction, lin_clf


def predict_question_class(question_clf, df_question_predict):
    return question_clf.predict(df_question_predict), question_clf


def load_classifier_model(model_type="linearSVC"):

    training_model_path = os.path.join(CORPUS_DIR, QUESTION_CLASSIFICATION_MODEL)

    if model_type == "linearSVC":
        return joblib.load(training_model_path)


def get_question_predict_data(en_doc=None, df_question_test=None):

    if df_question_test is None:
        # currently only supports single sentence classification
        sentence_list = list(en_doc.sents)[0:1]

    else:
        sentence_list = df_question_test["Question"].tolist()

        import spacy
        en_nlp = spacy.load(EN_MODEL_MD)

    question_data_frame = []

    for sentence in sentence_list:

        wh_bi_gram = []
        root_token, wh_pos, wh_nbor_pos, wh_word = [""] * 4

        if df_question_test is not None:
            en_doc = en_nlp(u'' + sentence)
            sentence = list(en_doc.sents)[0]

        for token in sentence:

            if token.tag_ == "WDT" or token.tag_ == "WP" or token.tag_ == "WP$" or token.tag_ == "WRB":
                wh_pos = token.tag_
                wh_word = token.text
                wh_bi_gram.append(token.text)
                wh_bi_gram.append(str(en_doc[token.i + 1]))
                wh_nbor_pos = en_doc[token.i + 1].tag_

            if token.dep_ == "ROOT":
                root_token = token.tag_

        question_data_frame_obj = {'WH': wh_word, 'WH-POS': wh_pos, 'WH-NBOR-POS': wh_nbor_pos, 'Root-POS': root_token}
        question_data_frame.append(question_data_frame_obj)

    df_question = pandas.DataFrame(question_data_frame)

    return df_question


def classify_question(en_doc=None, df_question_train=None, df_question_test=None):
    """ Determine whether this is a who, what, when, where or why question """

    if df_question_train is None:
        training_data_path = os.path.join(CORPUS_DIR, QUESTION_CLASSIFICATION_TRAINING_DATA)
        df_question_train = pandas.read_csv(training_data_path, sep='|', header=0)

    df_question_class = remove_irrelevant_features(df_question_train)

    if df_question_test is None:
        df_question_predict = get_question_predict_data(en_doc=en_doc)
    else:
        df_question_predict = get_question_predict_data(df_question_test=df_question_test)

    df_question_train = pre_process(df_question_train)
    df_question_predict = pre_process(df_question_predict)

    df_question_train, df_question_predict = transform_data_matrix(df_question_train, df_question_predict)

    question_clf = load_classifier_model()

    predicted_class, svc_clf = support_vector_machine(df_question_train, df_question_class, df_question_predict)

    if df_question_test is not None:
        return predicted_class, svc_clf, df_question_class, df_question_train
    else:
        return predicted_class
