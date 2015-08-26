#from model.conversation import Conversation
from datetime import datetime, timedelta
import collections
from src.util import io as mio
import argparse
from src.util import stats as mstats
from datetime import datetime
from src.model.message import Message
from src.util import plotting as mplot
import sys
import pandas as pd
import configparser
from src.model.conversation import Conversation
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
    conv = Conversation(mio.getResourcesPath() + "\\unittest\\test_nltk_conv.txt")
    #conv = Conversation(filepath)
    conv.loadMessages(numMsgs)
    rawText = conv.getEntireConvText()
    mio.displayDispersionPlot(conv, ['sender1', ':D', 'well'])
    mio.showConcordance(conv, "phone")
    #tokens = nltk.word_tokenize(rawText)
    #words = [w.lower() for w in tokens]
    mio.printAllLexicalStats(conv)

def drawParse(conv):
    rawText = conv.getEntireConvText()
    #tokens = nltk.word_tokenize(rawText)
    #words = [w.lower() for w in tokens]
    words = mstats.getWords(conv.messages)
    sentences = nltk.sent_tokenize(rawText)
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
    sentences = [nltk.pos_tag(sent) for sent in sentences]
    #text.generate()
    #for m in conv.messages:
    #    print(nltk.sent_tokenize(m.text))

    from nltk.corpus import conll2000
    test_sents = conll2000.chunked_sents('test.txt', chunk_types=['NP'])
    train_sents = conll2000.chunked_sents('train.txt', chunk_types =['NP'])
    chunker = ChunkParser(train_sents)

    for s in sentences:
        chunker.parse(s).draw()

class ChunkParser(nltk.ChunkParserI):
    def __init__(self, train_sents):
        train_data = [[(t,c) for w,t,c in nltk.chunk.tree2conlltags(sent)] for sent in train_sents]
        self.tagger = nltk.TrigramTagger(train_data)

    def parse(self, sentence):
        pos_tags= [pos for (word,pos) in sentence]
        tagged_pos_tags = self.tagger.tag(pos_tags)
        chunktags = [chunktag for (pos,chunktag) in tagged_pos_tags]
        conlltags = [(word,pos,chunktag) for ((word,pos), chunktag) in zip(sentence,chunktags)]
        return nltk.chunk.conlltags2tree(conlltags)

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
