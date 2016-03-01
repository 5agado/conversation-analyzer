#from model.conversation import Conversation
import argparse
import logging
import os
import sys

import numpy as np
from matplotlib import pyplot as plt
from scipy.stats.stats import pearsonr

from model.conversationDataframe import ConversationDataframe
from util import conversationGenerator
from util import io as mio
from util import plotting as mplot


#from sklearn import datasets, linear_model

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
    parser.add_argument('-p', metavar='conversationfilePath', dest='filepath')
    parser.add_argument('-n', metavar='numberOfMessages', type=int,
                        dest='numMsgs', default=1000)
    parser.add_argument('-l', metavar='wordsCountLimit', type=int,
                        dest='wCountLimit', default=20)

    args = parser.parse_args()
    filepath = args.filepath
    numMsgs = args.numMsgs
    wCountLimit = args.wCountLimit

    initLogger()
    #conv = Conversation(mio.getResourcesPath() + "\\unittest\\test_plotting.txt")
    conv = ConversationDataframe(mio.getResourcesPath() + "\\unittest\\test_plotting.txt")
    #conv = Conversation(filepath)
    conv.loadMessages(numMsgs)
    mio.printWordsUsedJustByToFile(conv)
    return

    #sentences = mnlp.sentenceSegmentation(conv.getEntireConvText())
    #sentences = mnlp.wordTokenization(conv.getEntireConvText())
    #for s in sentences:
    #    print(s)
    #rawText = conv.getEntireConvText()
    #mio.displayDispersionPlot(conv, ['sender1', ':D', 'well'])
    #mio.showConcordance(conv, "phone")
    #tokens = nltk.word_tokenize(rawText)
    #words = [w.lower() for w in tokens]

def testZipfLaw(conv):
    _, wCount, _ = conv.stats.getWordCountStats()
    print(wCount)

    (_, occFirst) = wCount[0]
    for i, (word, count) in enumerate(wCount[:10], start=1):
        print(word + " " + str(i) + " = " +  str(occFirst/count))
        print(word + " " + str(count) + " = " +  str(occFirst/i))
    words, count = zip(*wCount)

    mplot.plotZipfLaw(words, count)
    return

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

def testConversationGenerator():
    conv = conversationGenerator.generateNewConversation(100, "2014.01.30 06:01:57", "2014.12.30 06:01:57", ["s1", "s2"], 3, 20)
    mio.printListToFile(conv, os.path.join(mio.getResourcesPath(), "test.txt"))

init(sys.argv[1:])
