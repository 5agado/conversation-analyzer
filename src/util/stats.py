from datetime import datetime
import collections
import numpy as np
import pandas as pd
import re
import math
from scipy import stats
import util.io as mio
from model.message import Message

def getCentralTendencyValuesFor(measures):
    mean = measures.mean()
    median = measures.median()
    mode = measures.mode()
    return  mean, median, mode

def getVariationValuesFor(measures):
    meanDeviation = stats.pstdev(measures)
    variance = measures.var()
    stdDeviation = math.sqrt(variance)
    return  meanDeviation, variance, stdDeviation

def getTotalLengthOf (messages):
    totalLength = 0
    for m in messages:
        totalLength += m.getMessageLength()
    return totalLength

def getBasicLengthStats (messages):
    if len(messages) == 0:
        #print("Empty message list")
        return 0, 0, 0
    totalLength = getTotalLengthOf(messages)

    return len(messages), totalLength, totalLength/len(messages)

def getIntervalStatsFor(messages):
    start = datetime.strptime(messages[0].datetime, Message.DATE_TIME_FORMAT)
    end = datetime.strptime(messages[-1].datetime, Message.DATE_TIME_FORMAT)
    interval = end - start

    return  messages[0].datetime, messages[-1].datetime, interval

def generateDataFrameAgglomeratedStatsBy(mFun, messages, sender1, sender2):
    agglomeratedMessages = getMessagesBy(mFun, messages)
    aggBasicLengthStatsS1 = [getBasicLengthStats(list(filter(lambda m: m.sender == sender1, a))) for _, a in agglomeratedMessages.items()]
    aggBasicLengthStatsS2 = [getBasicLengthStats(list(filter(lambda m: m.sender == sender2, a))) for _, a in agglomeratedMessages.items()]
    s1y1 = [i[0] for i in aggBasicLengthStatsS1]
    s1y2 = [i[1] for i in aggBasicLengthStatsS1]
    s1y3 = [i[2] for i in aggBasicLengthStatsS1]
    s2y1 = [i[0] for i in aggBasicLengthStatsS2]
    s2y2 = [i[1] for i in aggBasicLengthStatsS2]
    s2y3 = [i[2] for i in aggBasicLengthStatsS2]
    toty1 = list(sum(t) for t in zip(s1y1, s2y1))
    toty2 = list(sum(t) for t in zip(s1y2, s2y2))
    toty3 = [l/n  if n!= 0 else 0 for (n,l) in zip(toty1, toty2)]

    data = np.array([s1y1, s2y1, s1y2, s2y2, s1y3, s2y3, toty1, toty2, toty3]).T
    c = [sender1 + '_numMsgs', sender2 + '_numMsgs',
         sender1 + '_lenMsgs', sender2 + '_lenMsgs',
         sender1 + '_avgLen', sender2 + '_avgLen',
         'totNumMsgs', 'totLenMsgs', 'totAvgLen']
    df = pd.DataFrame(data, index = list(agglomeratedMessages.keys()), columns = c)
    df.sort_index(inplace=True)
    return  df

def getWordsCount(messages):
    emoticons = mio.getSetFromFile(mio.getResourcesPath() + "\emoticonList.txt")
    wordsCount = collections.Counter([])
    for m in messages:
        #TODO words cleaning
        words = map(lambda w: cleanWord(str.lower(w), emoticons), m.text.split())
        words = list(filter(lambda w: len(w) > 0, words))
        wordsCount += collections.Counter(words)
    return wordsCount

def cleanWord(word, skipSet):
    if word in skipSet:
        return word
    else:
        cWord = re.sub('^[^a-z0-9]*|[^a-z0-9]*$', '', word)
        #TODO check for weird words and other options
        # if cWord == 'd':
        #     with open(mio.getResourcesPath() + '\ete.txt', "a+", encoding="utf8") as f:
        #         f.write(word + "\n")
        return cWord

def sortDict(d):
    return sorted(d, key=d.get, reverse=True)

def getWordsCountStats(messages, sender1Messages, sender2Messages, limit = 0):
    wCount = getWordsCount(messages)
    wCountS1 = getWordsCount(sender1Messages)
    wCountS2 = getWordsCount(sender2Messages)
    if limit == 0:
        return wCount, wCountS1, wCountS2
    else:
        return wCount.most_common(limit),\
               wCountS1.most_common(limit),\
               wCountS2.most_common(limit)

def getWordsMentioningStats(sender1Messages, sender2Messages):
    wordsSaidBySender1 = getWordsCount(sender1Messages).keys()
    wordsSaidBySender2 = getWordsCount(sender2Messages).keys()
    wordsSaidByBoth = set(wordsSaidBySender1).intersection(wordsSaidBySender2)
    wordsSaidJustByS1 = set(wordsSaidBySender1).difference(wordsSaidBySender2)
    wordsSaidJustByS2 = set(wordsSaidBySender2).difference(wordsSaidBySender1)
    return wordsSaidByBoth, wordsSaidJustByS1, wordsSaidJustByS2

def getMessagesBy(mFun, messages):
    groups= collections.defaultdict(list)
    for m in messages:
        groups[mFun(m)].append(m)
    return dict(groups)

def getMessagesByMonth(messages):
    groups= collections.defaultdict(list, [(i+1, []) for i in range(12)])
    return _getMessagesBy(lambda m:m.getMonth(), messages, groups)

def getMessagesByHour(messages):
    groups= collections.defaultdict(list, [(i, []) for i in range(24)])
    return _getMessagesBy(lambda m:m.getHour(), messages, groups)

def _getMessagesBy(mFun, messages, groups = None):
    if not groups:
        groups= collections.defaultdict(list)
    for m in messages:
        groups[mFun(m)].append(m)
    return dict(groups)

