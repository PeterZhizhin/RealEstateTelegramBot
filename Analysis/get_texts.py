#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pymongo
import nltk
import nltk.corpus
import ipdb
import string
from collections import defaultdict

db = pymongo.MongoClient()['telegram_realty_bot_db']
db = db['flats']

stop_words = nltk.corpus.stopwords.words('russian')
stop_words.extend(['что', 'это', 'так', 'вот', 'быть', 'как', 'в', '—', 'к', 'на'])
stemmer = nltk.stem.snowball.RussianStemmer()
stemmer.stopwords = set(stop_words)

def tokenize_me(file_text):
    #firstly let's apply nltk tokenization
    tokens = nltk.word_tokenize(file_text)

    #let's delete punctuation symbols
    tokens = [i for i in tokens if i not in string.punctuation]

    #deleting stop_words
    tokens = [i for i in tokens if i not in stop_words]

    #cleaning words
    tokens = [i.replace("«", "").replace("»", "") for i in tokens]

    tokens = [stemmer.stem(i) for i in tokens]

    return set(tokens)

comments = db.find({}, {'comment': 1})
count = db.count({})
words_dict = defaultdict(int)

for i, com in enumerate(comments):
    print(i, count)
    words = tokenize_me(com['comment'])
    for word in words:
        words_dict[word] += 1

with open('res.txt', 'w') as f:
    for key, value in words_dict.items():
        f.write('{} {}\n'.format(key, value))

