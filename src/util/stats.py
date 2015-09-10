from datetime import datetime, timedelta
import collections
import statistics
import numpy as np
import pandas as pd
import re
import nltk
import logging
import util.io as mio
import math
from model.message import Message

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

def getLexicalStats(messages):
    words = getWords(messages)
    text = nltk.Text(words)
    tokensCount = len(text)
    vocabularyCount = len(set(text))
    lexicalRichness = vocabularyCount / tokensCount
    return  tokensCount, vocabularyCount, lexicalRichness

def getEmoticonsStats(messages):
    numEmoticons = 0
    if len(messages) == 0:
        return numEmoticons
    emoticons = mio.getSetFromFile(mio.getResourcesPath() + "\emoticonList.txt")
    for m in messages:
        mEmoticons = getEmoticonsFromText(m.text, emoticons)
        numEmoticons += len(mEmoticons)
    return numEmoticons

def getEmoticonsFromText(text, emoticons):
    words = map(lambda w: cleanWord(str.lower(w), emoticons), text.split())
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
def getDelayStatsFor(messages):
    """Calculates the delays between the messages of the conversation.
    senderDelay consider the time that passed between a sender message and the successive reply
     from another sender. The result value is the sum of such time for each message.
     Notice that if the same sender sends many message, only the last one (before another sender message)
     is taken into consideration"""

    senderDelay = collections.defaultdict(timedelta)
    prevSender = messages[0].sender
    prevDatetime = datetime.strptime(messages[0].datetime, Message.DATE_TIME_FORMAT)
    for m in messages[1:]:
        currentDatetime = datetime.strptime(m.datetime, Message.DATE_TIME_FORMAT)
        currentSender = m.sender
        thisDelay = currentDatetime - prevDatetime
        if prevSender != currentSender:
            senderDelay[prevSender+ ':' +currentSender] += thisDelay
            prevSender = currentSender
        prevDatetime = currentDatetime

    return senderDelay

def getDelayStatsByLength(messages):
    delay = ([])
    senderDelay = collections.defaultdict(list)
    #senderDelay = {conv.sender1+ ':' +conv.sender2: [], conv.sender2+ ':' +conv.sender1: []}
    prevSender = messages[0].sender
    prevDatetime = datetime.strptime(messages[0].datetime, Message.DATE_TIME_FORMAT)
    #TODO Consider the option to sum all messages length until reply
    msgLen = messages[0].getMessageLength()
    for m in messages[1:]:
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

def getSequentialMessagesStats(messages):
    numOfSeqMsgs = collections.defaultdict(int)
    senderDelay = collections.defaultdict(timedelta)
    #senderDelay = {conv.sender1: timedelta(0), conv.sender2: timedelta(0)}
    prevSender = messages[0].sender
    prevDatetime = datetime.strptime(messages[0].datetime, Message.DATE_TIME_FORMAT)
    for m in messages[1:]:
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

def getWordsCount(messages):
    wordsCount = collections.Counter(getWords(messages))
    return wordsCount

def getWords(messages):
    #TODO consider using regex for emoticon structure; e.g. :DDD, xDDD
    emoticons = mio.getSetFromFile(mio.getResourcesPath() + "\emoticonList.txt")
    words = []
    for m in messages:
        mText = m.text.lower()
        words += list(filter(lambda w: len(w) > 0, [cleanWord(w, emoticons) for w in mText.split()]))
    return words

def cleanWord(word, skipSet):
    if word in skipSet:
        return word
    else:
        cWord = re.sub('^[^a-z0-9]*|[^a-z0-9]*$', '', word)
        #TODO better check for different possible words
        return cWord

def getWordsCountStats(messages, limit = 0):
    wCount = getWordsCount(messages)

    if limit == 0:
        return wCount
    else:
        return wCount.most_common(limit)

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

