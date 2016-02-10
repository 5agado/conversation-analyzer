#from model.conversation import Conversation
from datetime import datetime, timedelta
import collections
import re
from util import io as mio
import argparse
import queue as Q
from util import convStats as mstats
from datetime import datetime
from model.message import Message
from util import plotting as mplot
import sys
import pandas as pd
import configparser
from model.conversation import Conversation
import util.nlp as mnlp
import logging
from matplotlib import pyplot as plt
import os
from scipy.stats.stats import pearsonr
import numpy as np
import nltk
from sklearn import datasets, linear_model

def initLogger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)s - %(message)s",
                                  "%Y-%m-%d %H:%M:%S")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

def init(_):
    parser = argparse.ArgumentParser(description='Conversation Analyzer')
    parser.add_argument('-p', metavar='conversationfilePath', dest='filepath', required=True)
    parser.add_argument('-n', metavar='numberOfMessages', type=int,
                        dest='numMsgs', default=1000)
    parser.add_argument('-l', metavar='wordsCountLimit', type=int,
                        dest='wCountLimit', default=20)

    args = parser.parse_args()
    filepath = args.filepath
    numMsgs = args.numMsgs
    wCountLimit = args.wCountLimit

    initLogger()
    #conv = Conversation(mio.getResourcesPath() + "\\unittest\\test_nltk_conv.txt")
    conv = Conversation(filepath)
    #conv.loadMessages(numMsgs, "2014.09.26", "2014.09.30")
    conv.loadMessages(numMsgs)

    q = Q.PriorityQueue()
    wCount, wCountS1, wCountS2 = conv.getWordsCountStats()
    wCountS1 = dict(wCountS1)
    wCountS2 = dict(wCountS2)
    maxRatio = 0
    word = None
    for k, count1 in wCountS1.items():
        if k in wCountS2:
            ratio = count1/wCountS2[k]
            #q.put((, word))
            if ratio>maxRatio:
                maxRatio = ratio
                word = k
            if ratio>5:
                print(k)
    print("For sender " + conv.sender1)
    while not q.empty():
        print (q.get())
    print(word)
    print(wCountS1[word])
    print(wCountS2[word])
    print(maxRatio)
    #mio.printIntervalStatsFor(conv)
    #mnlp.senderClassification(conv)

    #sentences = emoticons.split(conv.getEntireConvText())
    #print(sentences)

    #sentences = mnlp.sentenceSegmentation(conv.getEntireConvText())
    #sentences = mnlp.wordTokenization(conv.getEntireConvText())
    #for s in sentences:
    #    print(s)
    #mio.printAgglomeratedStatsToFile(lambda m: m.getHour(), 'Hours', conv)
    #mio.printAgglomeratedStatsToFile(lambda m: m.date, 'Day', conv)
    #mio.printAgglomeratedStatsToFile(lambda m: m.getMonth(), 'Month', conv)
    #mplot.plotDaysWithoutMessages(conv)
    #mplot.plotBasicLengthStats(conv)
    #rawText = conv.getEntireConvText()
    #mio.displayDispersionPlot(conv, ['sender1', ':D', 'well'])
    #mio.showConcordance(conv, "phone")
    #tokens = nltk.word_tokenize(rawText)
    #words = [w.lower() for w in tokens]
    #mio.printAllLexicalStats(conv)

def plotDelayByLengthStats(conv):
    delay, senderDelay = mstats.getDelayStatsByLength(conv)
    x = np.array([v[0] for v in senderDelay[conv.sender1+ ':' +conv.sender2]])
    y = np.array([v[1] for v in senderDelay[conv.sender1+ ':' +conv.sender2]])
    print(pearsonr(x, y))
    print(np.corrcoef(x, y)[0, 1])
    print(x)
    print(x[:,np.newaxis])

    # Create linear regression object
    regr = linear_model.LinearRegression()

    # Train the model using the training sets
    regr.fit(x[:,np.newaxis],y)

    plt.scatter(x, y, color='red')
    plt.plot(x, regr.predict(x[:,np.newaxis]), color='blue')
    plt.show()

init(sys.argv[1:])
