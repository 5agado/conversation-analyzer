import logging
import sys
import argparse
import numpy as np
from model.conversation import Conversation
from util import plotting as mplot
from util import io as mio

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
                        dest='wCountLimit', default=100)

    args = parser.parse_args()
    filepath = args.filepath
    numMsgs = args.numMsgs
    wCountLimit = args.wCountLimit

    initLogger()
    #conv = Conversation(mio.getResourcesPath() + "\\unittest\\test_nltk_conv.txt")
    conv = Conversation(filepath)
    conv.loadMessages(numMsgs)

    _, vocabularyCount, _ = conv.getLexicalStats()
    _, wCount, _ = conv.getWordsCountStats(wCountLimit)

    (_, occFirst) = wCount[0]
    for i, (word, count) in enumerate(wCount[:10], start=1):
        print(word + " " + str(i) + " = " +  str(occFirst/count))
        print(word + " " + str(count) + " = " +  str(occFirst/i))
    words, count = zip(*wCount)
    x = range(len(words))

    mplot.plotStatsLines("Zip's Law", ['Rank', 'Count', 'Word'], x, words, count, None)

init(sys.argv[1:])