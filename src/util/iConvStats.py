# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from datetime import datetime, timedelta
import collections
import numpy as np
import pandas as pd
from model.message import Message
from util import statsUtil

class IConvStats(metaclass=ABCMeta):
    def __init__(self, conversation):
        self.conversation = conversation

    @abstractmethod
    def getBasicLengthStats(self, sender=None):
        pass

    @abstractmethod
    def generateDataFrameAgglomeratedStatsByHour(self):
        pass

    def getEmoticonsStats(self):
        numEmoticons = IConvStats._getEmoticonsStats(self.conversation.messages)
        numEmoticonsS1 = IConvStats._getEmoticonsStats(self.conversation.sender1Messages)
        numEmoticonsS2 = IConvStats._getEmoticonsStats(self.conversation.sender2Messages)
        return  numEmoticons, numEmoticonsS1, numEmoticonsS2

    @staticmethod
    def _getEmoticonsStats(messages):
        numEmoticons = 0
        if len(messages) == 0:
            return numEmoticons
        #emoticons = mio.getSetFromFile(mio.getResourcesPath() + "\emoticonList.txt")
        for m in messages:
            mEmoticons = statsUtil.getEmoticonsFromText(m.text)
            numEmoticons += len(mEmoticons)
        return numEmoticons

    def getIntervalStats(self):
        start, end, interval = IConvStats._getIntervalStatsFor(self.conversation.messages)
        return start, end, interval

    @staticmethod
    def _getIntervalStatsFor(messages):
        start = datetime.strptime(messages[0].datetime, Message.DATE_TIME_FORMAT)
        end = datetime.strptime(messages[-1].datetime, Message.DATE_TIME_FORMAT)
        interval = end - start

        return messages[0].datetime, messages[-1].datetime, interval

    def getDaysWithoutMessages(self):
        days = IConvStats.getDaysWithoutMessages(self.conversation.messages)
        return days

    @staticmethod
    def _getDaysWithoutMessages(messages):
        """Generate a date-range between the date of the first and last message
        and returns those dates for which there is no corresponding message in messages"""
        days = []
        start = datetime.strptime(messages[0].date, Message.DATE_FORMAT).date()
        end = datetime.strptime(messages[-1].date, Message.DATE_FORMAT).date()
        datelist = pd.date_range(start, end).tolist()
        agglomeratedMessages = IConvStats._getMessagesBy(lambda m: m.date, messages)
        for d in datelist:
            if not d.date().strftime(Message.DATE_FORMAT) in agglomeratedMessages:
                days.append(d.date())
        return days

    def getDelayStats(self):
        delay = IConvStats._getDelayStatsFor(self.conversation.messages)
        return delay

    @staticmethod
    def _getDelayStatsFor(messages):
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

    def getDelayStatsByLength(self):
        delay, senderDelay = IConvStats._getDelayStatsByLength(self.conversation.messages)
        return delay, senderDelay

    @staticmethod
    def _getDelayStatsByLength(messages):
        delay = ([])
        senderDelay = collections.defaultdict(list)
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

    @staticmethod
    def getSequentialMessagesStats(messages):
        numOfSeqMsgs = collections.defaultdict(int)
        senderDelay = collections.defaultdict(timedelta)
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

    @staticmethod
    @abstractmethod
    def getWordsCount(messages):
        pass

    def getWordsCountStats(self, limit=0):
        wCount = IConvStats._getWordsCountStats(self.conversation.messages, limit)
        wCountS1 = IConvStats._getWordsCountStats(self.conversation.sender1Messages, limit)
        wCountS2 = IConvStats._getWordsCountStats(self.conversation.sender2Messages, limit)

        return wCount, wCountS1, wCountS2

    def getWordsMentioningStats(self):
        wordsSaidByBoth, wordsSaidJustByS1, wordsSaidJustByS2 = \
            IConvStats._getWordsMentioningStats(self.conversation.sender1Messages, self.conversation.sender2Messages)
        return wordsSaidByBoth, wordsSaidJustByS1, wordsSaidJustByS2

    @staticmethod
    def _getWordsCountStats(messages, limit = 0):
        wCount = IConvStats.getWordsCount(messages)

        if limit == 0:
            return wCount.most_common()
        else:
            return wCount.most_common(limit)

    @staticmethod
    def _getWordsMentioningStats(sender1Messages, sender2Messages):
        wordsSaidBySender1 = IConvStats.getWordsCount(sender1Messages).keys()
        wordsSaidBySender2 = IConvStats.getWordsCount(sender2Messages).keys()
        wordsSaidByBoth = set(wordsSaidBySender1).intersection(wordsSaidBySender2)
        wordsSaidJustByS1 = set(wordsSaidBySender1).difference(wordsSaidBySender2)
        wordsSaidJustByS2 = set(wordsSaidBySender2).difference(wordsSaidBySender1)
        return wordsSaidByBoth, wordsSaidJustByS1, wordsSaidJustByS2

    @staticmethod
    def _getMessagesBy(mFun, messages, groups=None):
        if not groups:
            groups = collections.defaultdict(list)
        for m in messages:
            groups[int(mFun(m))].append(m)
        return dict(groups)

    @staticmethod
    def getMessagesByYear(messages):
        return IConvStats._getMessagesBy(lambda m: m.getYear(), messages)

    @staticmethod
    def getMessagesByMonth(messages):
        groups = collections.defaultdict(list, [(i+1, []) for i in range(12)])
        return IConvStats._getMessagesBy(lambda m: m.getMonth(), messages, groups)

    @staticmethod
    def getMessagesByHour(messages):
        groups = collections.defaultdict(list, [(i, []) for i in range(24)])
        return IConvStats._getMessagesBy(lambda m: m.getHour(), messages, groups)

    @abstractmethod
    def getLexicalStats(self, sender=None):
        pass

    @abstractmethod
    def generateDataFrameSingleWordCountBy(self, mFun, word):
        pass

    def generateDataFrameEmoticonsStatsBy(self, mFun):
        agglomeratedMessages = IConvStats._getMessagesBy(mFun, self.conversation.messages)
        df = self.generateDataFrameAgglomeratedStatsBy(mFun, agglomeratedMessages)

        emoticonStatsS1 = [IConvStats._getEmoticonsStats(list(filter(lambda m: m.sender == self.conversation.sender1, a)))
                                 for _, a in agglomeratedMessages.items()]
        emoticonStatsS2 = [IConvStats._getEmoticonsStats(list(filter(lambda m: m.sender == self.conversation.sender2, a)))
                                 for _, a in agglomeratedMessages.items()]

        df[self.conversation.sender1 + '_numEmoticons'] = np.array(emoticonStatsS1)
        df[self.conversation.sender2 + '_numEmoticons'] = np.array(emoticonStatsS2)
        df['totNumEmoticons'] = df[self.conversation.sender1 + '_numEmoticons'] + df[self.conversation.sender2 + '_numEmoticons']
        df[self.conversation.sender1 + '_emoticonsRatio'] = df[self.conversation.sender1 + '_numEmoticons'] /  df[self.conversation.sender1 + '_lenMsgs']
        df[self.conversation.sender2 + '_emoticonsRatio'] = df[self.conversation.sender2 + '_numEmoticons'] /  df[self.conversation.sender2 + '_lenMsgs']
        df['totEmoticonsRatio'] = df['totNumEmoticons'] /  df['totLenMsgs']
        return df
