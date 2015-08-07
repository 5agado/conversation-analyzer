from datetime import datetime, timedelta
import collections
import statistics
import numpy as np
import pandas as pd
import re
import logging
import src.util.io as mio
import math
from src.model.message import Message

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

def getTotalLengthOf(messages):
    totalLength = 0
    for m in messages:
        totalLength += m.getMessageLength()
    return totalLength

def getBasicLengthStats(messages):
    if len(messages) == 0:
        return 0, 0, 0
    totalLength = getTotalLengthOf(messages)

    return len(messages), totalLength, totalLength/len(messages)

def getEmoticonsStats(messages):
    numEmoticons = 0
    if len(messages) == 0:
        return numEmoticons
    for m in messages:
        mEmoticons = getEmoticonsFromMessage(m)
        numEmoticons += len(mEmoticons)
    return numEmoticons

def getEmoticonsFromMessage(message):
    emoticons = mio.getSetFromFile(mio.getResourcesPath() + "\emoticonList.txt")
    words = map(lambda w: cleanWord(str.lower(w), emoticons), message.text.split())
    msgEmoticons = list(filter(lambda w: w in emoticons, words))
    return msgEmoticons

def getIntervalStatsFor(messages):
    start = datetime.strptime(messages[0].datetime, Message.DATE_TIME_FORMAT)
    end = datetime.strptime(messages[-1].datetime, Message.DATE_TIME_FORMAT)
    interval = end - start

    return messages[0].datetime, messages[-1].datetime, interval

def getDaysWithoutMessages(messages):
    """Generate a date-range between the date of the first and last message
    and returns those dates for which there is no corresponding message in messages"""
    days = []
    start = datetime.strptime(messages[0].date, Message.DATE_FORMAT).date()
    end = datetime.strptime(messages[-1].date, Message.DATE_FORMAT).date()
    datelist = pd.date_range(start, end).tolist()
    agglomeratedMessages = getMessagesBy(lambda m: m.date, messages)
    for d in datelist:
        if not d.date().strftime(Message.DATE_FORMAT) in agglomeratedMessages:
            days.append(d.date())
    return days

#TODO still specific for just two senders
def getDelayStatsFor(conv):
    """Calculates the delays between the messages of the conversation.
    overallDelay consider all separated messages
    senderDelay consider the time that passed between a sender message and the successive reply
     from another sender. The result value is the sum of such time for each message.
     Notice that if the same sender sends many message, only the last one (before another sender message)
     is taken into consideration"""

    senderDelay = {conv.sender1+ ':' +conv.sender2: timedelta(0), conv.sender2+ ':' +conv.sender1: timedelta(0)}
    overallDelay = timedelta(0)
    prevSender = conv.messages[0].sender
    prevDatetime = datetime.strptime(conv.messages[0].datetime, Message.DATE_TIME_FORMAT)
    for m in conv.messages[1:]:
        currentDatetime = datetime.strptime(m.datetime, Message.DATE_TIME_FORMAT)
        currentSender = m.sender
        thisDelay = currentDatetime - prevDatetime
        if prevSender != currentSender:
            senderDelay[prevSender+ ':' +currentSender] += thisDelay
            prevSender = currentSender
        overallDelay += thisDelay
        prevDatetime = currentDatetime

    return overallDelay, senderDelay

def getDelayStatsByLength(conv):
    delay = ([])
    senderDelay = {conv.sender1+ ':' +conv.sender2: [], conv.sender2+ ':' +conv.sender1: []}
    prevSender = conv.messages[0].sender
    prevDatetime = datetime.strptime(conv.messages[0].datetime, Message.DATE_TIME_FORMAT)
    #TODO Consider the option to sum all messages length until reply
    msgLen = conv.messages[0].getMessageLength()
    for m in conv.messages[1:]:
        currentDatetime = datetime.strptime(m.datetime, Message.DATE_TIME_FORMAT)
        currentSender = m.sender
        thisDelay = currentDatetime - prevDatetime
        if prevSender != currentSender:
            delay.append((msgLen, thisDelay.total_seconds()))
            senderDelay[prevSender+ ':' +currentSender].append((msgLen, thisDelay.total_seconds()))
            prevSender = currentSender
        msgLen = m.getMessageLength()
        prevDatetime = currentDatetime

    return delay, senderDelay

def getSequentialMessagesStats(conv):
    numOfSeqMsgs = collections.defaultdict(int)
    senderDelay = {conv.sender1: timedelta(0), conv.sender2: timedelta(0)}
    prevSender = conv.messages[0].sender
    prevDatetime = datetime.strptime(conv.messages[0].datetime, Message.DATE_TIME_FORMAT)
    for m in conv.messages[1:]:
        currentDatetime = datetime.strptime(m.datetime, Message.DATE_TIME_FORMAT)
        currentSender = m.sender
        thisDelay = currentDatetime - prevDatetime
        if prevSender == currentSender:
            numOfSeqMsgs[prevSender] += 1
            senderDelay[prevSender] += thisDelay
        else:
            prevSender = currentSender
        prevDatetime = currentDatetime

    return numOfSeqMsgs, senderDelay

#TODO Use index label instead of number
def generateDataFrameAgglomeratedStatsBy(mFun, messages, sender1, sender2):
    agglomeratedMessages = getMessagesBy(mFun, messages)
    aggBasicLengthStatsS1 = [getBasicLengthStats(list(filter(lambda m: m.sender == sender1, a)))
                             for _, a in agglomeratedMessages.items()]
    aggBasicLengthStatsS2 = [getBasicLengthStats(list(filter(lambda m: m.sender == sender2, a)))
                             for _, a in agglomeratedMessages.items()]
    s1y1 = [i[0] for i in aggBasicLengthStatsS1]
    s1y2 = [i[1] for i in aggBasicLengthStatsS1]
    s1y3 = [i[2] for i in aggBasicLengthStatsS1]
    s2y1 = [i[0] for i in aggBasicLengthStatsS2]
    s2y2 = [i[1] for i in aggBasicLengthStatsS2]
    s2y3 = [i[2] for i in aggBasicLengthStatsS2]
    toty1 = list(sum(t) for t in zip(s1y1, s2y1))
    toty2 = list(sum(t) for t in zip(s1y2, s2y2))
    toty3 = [l/n if n != 0 else 0 for (n, l) in zip(toty1, toty2)]

    data = np.array([s1y1, s2y1, s1y2, s2y2, s1y3, s2y3, toty1, toty2, toty3]).T
    c = [sender1 + '_numMsgs', sender2 + '_numMsgs',
         sender1 + '_lenMsgs', sender2 + '_lenMsgs',
         sender1 + '_avgLen', sender2 + '_avgLen',
         'totNumMsgs', 'totLenMsgs', 'totAvgLen']
    df = pd.DataFrame(data, index=list(agglomeratedMessages.keys()), columns=c)
    return df

def generateDataFrameEmoticoStatsBy(mFun, messages, sender1, sender2):
    df = generateDataFrameAgglomeratedStatsBy(mFun, messages, sender1, sender2)

    #TODO operation repeated
    agglomeratedMessages = getMessagesBy(mFun, messages)
    emoticonStatsS1 = [getEmoticonsStats(list(filter(lambda m: m.sender == sender1, a)))
                             for _, a in agglomeratedMessages.items()]
    emoticonStatsS2 = [getEmoticonsStats(list(filter(lambda m: m.sender == sender2, a)))
                             for _, a in agglomeratedMessages.items()]
    totEmoStats = list(sum(t) for t in zip(emoticonStatsS1, emoticonStatsS2))
    s1Ratio = [n/l if l != 0 else 0 for (n, l) in zip(emoticonStatsS1, df.ix[:, 2])]
    s2Ratio = [n/l if l != 0 else 0 for (n, l) in zip(emoticonStatsS2, df.ix[:, 3])]
    totRatio = [n/l if l != 0 else 0 for (n, l) in zip(totEmoStats, df.ix[:, 7])]

    df[sender1 + '_numEmoticons'] = np.array(emoticonStatsS1)
    df[sender2 + '_numEmoticons'] = np.array(emoticonStatsS2)
    df['totnumEmoticons'] = np.array(totEmoStats)
    df[sender1 + '_emoticonsRatio'] = np.array(s1Ratio)
    df[sender2 + '_emoticonsRatio'] = np.array(s2Ratio)
    df['totEmoticonsRatio'] = np.array(totRatio)
    return df

def generateDataFrameSingleWordCountBy(mFun, word, messages, sender1, sender2):
    df = generateDataFrameAgglomeratedStatsBy(mFun, messages, sender1, sender2)
    wOcc1, wOcc2 = getSingleWordCountBy(word, mFun, messages, sender1, sender2)

    s1Count = [y for (x, y) in wOcc1]
    s2Count = [y for (x, y) in wOcc2]
    totCount = [c1+c2 for (c1,c2) in zip(s1Count, s2Count)]

    #TODO ??already add ratio
    df[sender1 + '_count'] = np.array(s1Count)
    df[sender2 + '_count'] = np.array(s2Count)
    df['totnumEmoticons'] = np.array(totCount)
    return df

def getWordsCountBy(mFun, messages, sender1, sender2):
    agglomeratedMessages = getMessagesBy(mFun, messages)
    #wordsFrequencyStats = getWordsCount(messages)
    wordsFrequencyStatsS1 = [(d, getWordsCount(list(filter(lambda m: m.sender == sender1, a))))
                             for d, a in agglomeratedMessages.items()]
    wordsFrequencyStatsS2 = [(d, getWordsCount(list(filter(lambda m: m.sender == sender2, a))))
                             for d, a in agglomeratedMessages.items()]
    #return  wordsFrequencyStats, wordsFrequencyStatsS1, wordsFrequencyStatsS2
    return  wordsFrequencyStatsS1, wordsFrequencyStatsS2

def getSingleWordCountBy(word, mFun, messages, sender1, sender2):
    wordsFrequencyStatsS1, wordsFrequencyStatsS2 = getWordsCountBy(mFun, messages, sender1, sender2)
    wordFrequencyS1 = [(by, count[word]) if word in count else (by, 0) for (by, count) in wordsFrequencyStatsS1]
    wordFrequencyS2 = [(by, count[word]) if word in count else (by, 0) for (by, count) in wordsFrequencyStatsS2]

    return  wordFrequencyS1, wordFrequencyS2

def getWordsCount(messages):
    #TODO consider using regex for emoticon structure; e.g. :DDD, xDDD
    emoticons = mio.getSetFromFile(mio.getResourcesPath() + "\emoticonList.txt")
    wordsCount = collections.Counter([])
    for m in messages:
        words = map(lambda w: cleanWord(str.lower(w), emoticons), m.text.split())
        words = list(filter(lambda w: len(w) > 0, words))
        wordsCount += collections.Counter(words)
    return wordsCount

def cleanWord(word, skipSet):
    if word in skipSet:
        return word
    else:
        cWord = re.sub('^[^a-z0-9]*|[^a-z0-9]*$', '', word)
        #TODO better check for different possible words
        # if cWord == 'd':
        #     with open(mio.getResourcesPath() + '\ete.txt', "a+", encoding="utf8") as f:
        #         f.write(word + "\n")
        return cWord

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
    groups = collections.defaultdict(list)
    for m in messages:
        groups[mFun(m)].append(m)
    return dict(groups)

def getMessagesByMonth(messages):
    groups = collections.defaultdict(list, [(i+1, []) for i in range(12)])
    return _getMessagesBy(lambda m: m.getMonth(), messages, groups)

def getMessagesByHour(messages):
    groups = collections.defaultdict(list, [(i, []) for i in range(24)])
    return _getMessagesBy(lambda m: m.getHour(), messages, groups)

def _getMessagesBy(mFun, messages, groups=None):
    if not groups:
        groups = collections.defaultdict(list)
    for m in messages:
        groups[mFun(m)].append(m)
    return dict(groups)

