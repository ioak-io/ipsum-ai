import re
import pandas as pd
from pymongo import InsertOne, DeleteMany, ReplaceOne, UpdateOne
from bson.objectid import ObjectId
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.stem import WordNetLemmatizer

from src.main.utils.db_connection_factory import get_collection, clean_array
from src.main.service.lemmatizer_helper import lemmatize_sentence
import src.main.utils.minio_utils as minio_utils

lemmatizer = WordNetLemmatizer()


PUNCTUATION = """!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""
NUMERIC = "0123456789"
TOP_K_KEYWORDS = 15  # top k number of keywords to retrieve in a ranked document


def _get_vectorizer_filename(space):
    return 'similarity_vectorizer_' + space + '.sav'


def clean_text(text):
    """Doc cleaning"""

    # Lowering text
    text = text.lower()

    print(" ".join([c for c in text if c in (PUNCTUATION + NUMERIC)]))
    # Removing punctuation
    text = "".join([c for c in text if c not in (PUNCTUATION + NUMERIC)])

    # Removing whitespace and newlines
    text = re.sub('\s+', ' ', text)

    return text


def sort_coo(coo_matrix):
    """Sort a dict with highest score"""
    tuples = zip(coo_matrix.col, coo_matrix.data)
    return sorted(tuples, key=lambda x: (x[1], x[0]), reverse=True)


def extract_topn_from_vector(feature_names, sorted_items, topn=10):
    """get the feature names and tf-idf score of top n items"""

    # use only topn items from vector
    sorted_items = sorted_items[:topn]

    score_vals = []
    feature_vals = []

    # word index and corresponding tf-idf score
    for idx, score in sorted_items:

        # keep track of feature name and its corresponding score
        score_vals.append(round(score, 3))
        feature_vals.append(feature_names[idx])

    # create a tuples of feature, score
    results = {}
    for idx in range(len(feature_vals)):
        results[feature_vals[idx]] = score_vals[idx]

    return results


def get_keywords(vectorizer, doc):
    """Return top k keywords from a doc using TF-IDF method"""

    feature_names = vectorizer.get_feature_names_out()

    # generate tf-idf for the given document
    tf_idf_vector = vectorizer.transform([doc])

    # sort the tf-idf vectors by descending order of scores
    sorted_items = sort_coo(tf_idf_vector.tocoo())

    # extract only TOP_K_KEYWORDS
    keywords = extract_topn_from_vector(
        feature_names, sorted_items, TOP_K_KEYWORDS)

    return list(keywords.keys())


def _get_stopwords(space):
    stopwords_collection = get_collection(space, 'stopwords')
    response = []
    for item in list(stopwords_collection.find()):
        response.append(item['text'])
    return response


def train(space):
    note_collection = get_collection(space, 'note')
    note_list = clean_array(list(note_collection.find()))
    content_list = [_get_text_from_note(o) for o in note_list]
    # stopwords = stopwords_dictionary.stopwordsEn
    stopwords = _get_stopwords(space)

    vectorizer = TfidfVectorizer(
        stop_words=stopwords, smooth_idf=True, use_idf=True)

    vectorizer.fit_transform(content_list)

    feature_names = vectorizer.get_feature_names_out()
    minio_utils.save(vectorizer, _get_vectorizer_filename(space))
    keywords_collection = get_collection(space, 'keywords')
    keywords_collection.delete_many({})
    keywords_collection.insert_one({'data': list(feature_names)})

    print(lemmatize_sentence(clean_text('perception perceive perceiving eating running')))

    return list(feature_names)


def _get_text_from_note(note):
    text = note['name'] + ' ' + note['contentText']
    if ('summary' in note):
        text += ' ' + note['summary']
    return lemmatize_sentence(clean_text(text))


def populate_keywords(space):
    note_collection = get_collection(space, 'note')
    note_list = clean_array(list(note_collection.find()))
    vectorizer = minio_utils.load(_get_vectorizer_filename(space))
    db_operations = []
    for note in note_list:
        keywords = get_keywords(vectorizer, _get_text_from_note(note))
        operation = UpdateOne({'_id': ObjectId(note['_id'])}, {
                              '$set': {'keywords': keywords}})
        db_operations.append(operation)
    if (len(db_operations) > 0):
        note_collection.bulk_write(db_operations)
    return {'status': 'success', 'notes': len(db_operations)}


def populate_links(space):
    note_collection = get_collection(space, 'note')
    notelink_auto_collection = get_collection(space, 'notelink.auto')
    note_list = clean_array(list(note_collection.find()))
    db_operations = []
    all_links = []
    for index, item in enumerate(note_list):
        links = _find_links(item, note_list[index:])
        all_links += links
    for link in all_links:
        operation = InsertOne(link)
        db_operations.append(operation)
    notelink_auto_collection.delete_many({})
    if (len(db_operations) > 0):
        notelink_auto_collection.bulk_write(db_operations)
    return {'status': 'success', 'links': len(db_operations)}


def populate_for_note(space, reference):
    note_collection = get_collection(space, 'note')
    notelink_auto_collection = get_collection(space, 'notelink.auto')
    note_list = clean_array(
        list(note_collection.find({})))
    source_note = None
    target_note_list = []
    for item in note_list:
        if (item['reference'] == reference):
            source_note = item
        else:
            target_note_list.append(item)
    if (source_note == None):
        return {'status': 'note not found', 'links': 0}
    vectorizer = minio_utils.load(_get_vectorizer_filename(space))
    keywords = get_keywords(vectorizer, _get_text_from_note(source_note))
    source_note['keywords'] = keywords
    note_collection.update_one({'reference': reference}, {
                               '$set': {'keywords': keywords}})

    db_operations = []
    all_links = _find_links(source_note, target_note_list)
    for link in all_links:
        operation = InsertOne(link)
        db_operations.append(operation)
    notelink_auto_collection.delete_many(
        {'$or': [{'sourceNoteRef': reference}, {'linkedNoteRef': reference}]})
    if (len(db_operations) > 0):
        notelink_auto_collection.bulk_write(db_operations)
    return {'status': 'success', 'links': len(db_operations)}


def _find_links(note, note_list):
    response = []
    for item in note_list:
        keywords = _intersection(item['keywords'], note['keywords'])
        if (len(keywords) > 1 and note['reference'] != item['reference']):
            response.append({
                'sourceNoteRef': note['reference'],
                'linkedNoteRef': item['reference'],
                'keywords': keywords
            })
    return response


def predict(space, text):
    vectorizer = minio_utils.load(_get_vectorizer_filename(space))
    return get_keywords(vectorizer, text)


def _intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3
