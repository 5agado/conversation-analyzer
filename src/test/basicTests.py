#from model.conversation import Conversation
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
                        dest='numMsgs', default=10000)
    parser.add_argument('-l', metavar='wordsCountLimit', type=int,
                        dest='wCountLimit', default=20)

    args = parser.parse_args()
    filepath = args.filepath
    numMsgs = args.numMsgs
    wCountLimit = args.wCountLimit

    initLogger()
    conv = Conversation(mio.getResourcesPath() + "\\unittest\\test_delay_conv.txt")
    #conv = Conversation(filepath)
    conv.loadMessages(numMsgs)
    print(mstats.getDelayStatsByLength(conv))


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
