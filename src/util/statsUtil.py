# -*- coding: utf-8 -*-

import statistics
import numpy as np
import pandas as pd
import re
import nltk
import logging
import sys
import util.io as mio
import math

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

def cleanWord(word, skipSet):
    if word in skipSet:
        return word
    else:
        cWord = re.sub('^[^a-z0-9]*|[^a-z0-9]*$', '', word)
        return cWord

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