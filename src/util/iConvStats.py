# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from datetime import datetime, timedelta
import collections
import numpy as np
import pandas as pd
from model.message import Message
from util import statsUtil

class IConvStats(metaclass=ABCMeta):
    STATS_NAME_BASICLENGTH = 'basicLengthStats'
    STATS_NAME_LEXICAL = 'lexicalStats'
    STATS_NAME_WORDCOUNT = 'wordCountStats'
    STATS_NAME_EMOTICONS = 'emoticonsStats'

    def __init__(self, conversation):
        self.conversation = conversation

    @abstractmethod
    def getBasicLengthStats(self, sender=None):
        pass

    @abstractmethod
    def generateDataFrameAgglomeratedStatsByHour(self):
        pass

    @abstractmethod
    def getEmoticonsStats(self):
        pass

    @abstractmethod
    def getLexicalStats(self, sender=None):
        pass

    #@abstractmethod
    #def generateDataFrameSingleWordCountBy(self, mFun, word):
    #    pass

    @abstractmethod
    def getIntervalStats(self):
        pass

    @abstractmethod
    def getDaysWithoutMessages(self):
        pass

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

    @abstractmethod
    def getWordsMentioningStats(self):
        pass