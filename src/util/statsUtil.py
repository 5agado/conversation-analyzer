# -*- coding: utf-8 -*-

import collections
import pandas as pd
import math
from datetime import datetime
import re
import statistics
import nltk
import numpy as np

def getCentralTendencyValuesFor(measures):
    mean = measures.mean()
    median = measures.median()
    mode = statistics.mode(measures)
    return mean, median, mode

def getVariationValuesFor(measures):
    c = measures.mean()
    meanDeviation = sum(math.fabs(x-c) for x in measures)/len(measures)
    variance = sum((x-c)**2 for x in measures)/len(measures)
    #variance = statistics.pvariance(measures)
    stdDeviation = variance**0.5
    #stdDeviation = statistics.pstdev(measures)
    return meanDeviation, variance, stdDeviation

def getWordsCount(text):
    wordsCount = collections.Counter(getWords(text))
    return wordsCount

def getBigramsCount(text):
    words = getWords(text)
    bigramsCount = collections.Counter(nltk.bigrams(words))
    return bigramsCount

def getTrigramsCount(text):
    words = getWords(text)
    trigramsCount = collections.Counter(nltk.trigrams(words))
    return trigramsCount

def getWords(text):
    mText = text.lower()
    emoticons = set(getEmoticonsFromText(mText))
    #words = list(filter(lambda w: len(w) > 0, [cleanWord(w, emoticons) for w in mText.split()]))
    words = list(filter(lambda w: len(w) > 0,
                        [w if w in emoticons else re.sub('^[^a-z0-9]*|[^a-z0-9]*$', '', w)
                         for w in mText.split()]))
    return words

def cleanWord(word, skipSet):
    if word in skipSet:
        return word
    else:
        cWord = re.sub('^[^a-z0-9]*|[^a-z0-9]*$', '', word)
        return cWord

def getEmoticonsCount(text):
    emoticonsCount = collections.Counter(getEmoticonsFromText(text))
    return emoticonsCount

def getEmoticonsFromText(text):
    emoticons = re.compile("""(^|(?<=\s))(
        #Western
        [<>\}30o]?
        [:;=8bx]                     # eyes
        [\-o\*\']?                 # optional nose
        [\)\]\(\[dopi3/\}\*\{@\|\\\]+ #mouth
        |
        [\)\]\(\[dopi3/\}\*\{@\|\\\]+ #mouth
        [\-o\*\']?                 # optional nose
        [:;=8bx]                     # eyes
        [<>]?
        |
        #Eastern
        [><\-ùu\+\*èçòû\^\?] #eye
        [\-_\.]* #nose
        [><\-ùu\+\*èçòû\^\?]#eye
        [\']?
        |
        <3
        |
        \\\o/
    )(?=\s|\W|$)""", re.IGNORECASE|re.VERBOSE)
    msgEmoticons = [(text[a.start(): a.end()]) for a in list(emoticons.finditer(text))]
    return msgEmoticons

# def getEmoticonsFromText(text, emoticons):
#     words = map(lambda w: cleanWord(str.lower(w), emoticons), text.split())
#     msgEmoticons = list(filter(lambda w: w in emoticons, words))
#     return msgEmoticons

def dateRangeTransform(stats, filters=None):
    df = transformStats(stats, 'stat', 'val', filters)
    df['date'] = df.apply(lambda x:datetime.strptime(
            "{0}-{1}-{2}".format(x['year'],x['month'], x['day']), "%Y-%m-%d"),axis=1)
    df = df[['date','val']].set_index('date')
    df.columns = [filters['stat']]
    idx = pd.date_range(df.index.values[0], df.index.values[-1])
    df = df.reindex(idx, fill_value=0)

    return df

def filter_stats(stats, filters):
    res = stats.copy()

    for filter_column, filter_values in filters.items():
        if filter_values:
            filter_values = np.array(filter_values, dtype=res[filter_column].dtype)
            res = res[res[filter_column].isin(filter_values)]

    return res

def transformSentimentStats(sentimentStats, valueNames, groupByColumns, aggFun='mean'):
    data = sentimentStats.groupby(groupByColumns).agg(dict([(x, aggFun) for x in valueNames]))
    data = transformStats(data, 'emotion', 'val')

    return data

def transformStats(stats, statsName, valName, filters=None):
    """
    Transform stats for plotting with stacking of current indexes
    :param stats: df to transform
    :param statsName: name to give to stats column (previously different column values)
    :param valName: name to give to value column (previously cell values)
    :return:
    """
    res = stats.stack().reset_index()
    res.columns.values[-2] = statsName
    res.columns.values[-1] = valName

    if filters:
        res = filter_stats(res, filters)

    return res