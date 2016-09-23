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
from util import statsUtil

from matplotlib import animation
from stats.iConvStats import IConvStats
import pandas as pd



import seaborn as sns


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
                        dest='numMsgs', default=0)
    parser.add_argument('-l', metavar='wordsCountLimit', type=int,
                        dest='wCountLimit', default=20)

    args = parser.parse_args()
    filepath = args.filepath
    numMsgs = args.numMsgs
    wCountLimit = args.wCountLimit

    initLogger()
    #conv = ConversationDataframe(mio.getResourcesPath() + "\\unittest\\test_plotting.txt")
    conv = ConversationDataframe(filepath)
    conv.loadMessages(numMsgs)
    return

    res = conv.messages.rename(columns={'text':'numMsgs'})
    res['lenMsgs'] = res['numMsgs'].apply(lambda x: len(x))
    x = pd.to_numeric(res['hour'])
    testCorrelation(x, res['lenMsgs'])
    #testAnimation(conv)

    #sentences = mnlp.sentenceSegmentation(conv.getEntireConvText())
    #sentences = mnlp.wordTokenization(conv.getEntireConvText())
    #for s in sentences:
    #    print(s)
    #rawText = conv.getEntireConvText()
    #mio.displayDispersionPlot(conv, ['sender1', ':D', 'well'])
    #mio.showConcordance(conv, "phone")
    #tokens = nltk.word_tokenize(rawText)
    #words = [w.lower() for w in tokens]

def testCorrelation(x, y):
    print(np.corrcoef(x, y)[0, 1])
    sns.regplot(x=x, y=y)
    plt.show()

def saveBunchOfStatsDf(conv):
    statsList = [IConvStats.STATS_NAME_BASICLENGTH, IConvStats.STATS_NAME_LEXICAL,
                 IConvStats.STATS_NAME_WORDCOUNT, IConvStats.STATS_NAME_EMOTICONS]
    for stat in statsList:
        filepath = conv.statsFolder + '\\' + stat + '.txt'
        df = conv.stats.generateStats(stat)
        mio.printDataFrameToFile(df, filepath)
        filepath = conv.statsFolder + '\\' + stat + 'byHour.txt'
        df = conv.stats.generateStatsByHour(stat)
        mio.printDataFrameToFile(df, filepath)
        filepath = conv.statsFolder + '\\' + stat + 'byYearAndHour.txt'
        df = conv.stats.generateStatsByYearAndHour(stat)
        mio.printDataFrameToFile(df, filepath)

def testAnimation(conv):
    data = conv.stats.generateStatsByYearMonthHour(IConvStats.STATS_NAME_BASICLENGTH)
    data = data.groupby('year').get_group('2014')
    grouped = data.groupby('month')
    keys = sorted(list(grouped.groups.keys()))
    print(keys)
    fig = plt.figure()
    ax = plt.axes()

    def animate(i):
        df = grouped.get_group(keys[i]).sort_values("hour")

        print(df.head())
        ax.clear()
        sns.barplot(x="hour", y="lenMsgs", hue="sender", data=df, ax=ax)
        ax.set_title(i)

    anim = animation.FuncAnimation(fig, animate,
                               frames=len(grouped), interval=2000)
    plt.show()


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
