# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import collections
from model.message import Message
from datetime import datetime, timedelta
from util import statsUtil
from util.iConvStats import IConvStats

class ConvStats(IConvStats):
    def __init__(self, conversation):
        super().__init__(conversation)

    def getBasicLengthStats(self, sender=None):
        if not sender:
            totalNum, totalLength, avgLegth = ConvStats._getBasicLengthStats(self.conversation.messages)
        else:
            totalNum, totalLength, avgLegth = ConvStats._getBasicLengthStats(self.conversation.messagesBySender[sender])
        return totalNum, totalLength, avgLegth

    @staticmethod
    def _getBasicLengthStats(messages):
        if len(messages) == 0:
            return 0, 0, 0
        totalLength = ConvStats._getTotalLengthOf(messages)

        return len(messages), totalLength, totalLength/len(messages)

    def getLexicalStats(self, sender=None):
        if not sender:
            tokensCount, vocabularyCount, lexicalRichness = ConvStats._getLexicalStats(self.conversation.messages)
        else:
            tokensCount, vocabularyCount, lexicalRichness = ConvStats._getLexicalStats(self.conversation.messagesBySender[sender])
        return tokensCount, vocabularyCount, lexicalRichness

    @staticmethod
    def _getLexicalStats(messages):
        words = statsUtil.getWords(messages)
        #text = nltk.Text(words)
        tokensCount = len(words)
        vocabularyCount = len(set(words))
        if tokensCount == 0:
            lexicalRichness = 0
        else:
            lexicalRichness = vocabularyCount / tokensCount
        return  tokensCount, vocabularyCount, lexicalRichness

    @staticmethod
    def _getTotalLengthOf(messages):
        totalLength = 0
        for m in messages:
            totalLength += m.getMessageLength()
        return totalLength

    def getWordsCountStats(self, limit=0):
        wCount = ConvStats._getWordsCountStats(self.conversation.messages, limit)
        wCountS1 = ConvStats._getWordsCountStats(self.conversation.sender1Messages, limit)
        wCountS2 = ConvStats._getWordsCountStats(self.conversation.sender2Messages, limit)

        return wCount, wCountS1, wCountS2

    @staticmethod
    def _getWordsCountStats(messages, limit = 0):
        wCount = IConvStats.getWordsCount(messages)

        if limit == 0:
            return wCount.most_common()
        else:
            return wCount.most_common(limit)

    def generateDataFrameAgglomeratedStatsByHour(self):
        res = self._generateDataFrameAgglomeratedStatsBy(lambda m: m.getHour())
        return res

    def _generateDataFrameAgglomeratedStatsBy(self, mFun, agglomeratedMessages=None):
        if not agglomeratedMessages:
            agglomeratedMessages = self._getMessagesBy(mFun, self.conversation.messages)
        aggBasicLengthStatsS1 = [ConvStats._getBasicLengthStats(list(filter(lambda m: m.sender == self.conversation.sender1, a)))
                                 for _, a in agglomeratedMessages.items()]
        aggBasicLengthStatsS2 = [ConvStats._getBasicLengthStats(list(filter(lambda m: m.sender == self.conversation.sender2, a)))
                                 for _, a in agglomeratedMessages.items()]

        df = pd.DataFrame(index=list(agglomeratedMessages.keys()))

        df[self.conversation.sender1 + '_numMsgs'] = [i[0] for i in aggBasicLengthStatsS1]
        df[self.conversation.sender2 + '_numMsgs'] = [i[0] for i in aggBasicLengthStatsS2]
        df[self.conversation.sender1 + '_lenMsgs'] = [i[1] for i in aggBasicLengthStatsS1]
        df[self.conversation.sender2 + '_lenMsgs'] = [i[1] for i in aggBasicLengthStatsS2]
        df[self.conversation.sender1 + '_avgLen'] = [i[2] for i in aggBasicLengthStatsS1]
        df[self.conversation.sender2 + '_avgLen'] = [i[2] for i in aggBasicLengthStatsS2]
        df['totNumMsgs'] = df[self.conversation.sender1 + '_numMsgs'] + df[self.conversation.sender2 + '_numMsgs']
        df['totLenMsgs'] = df[self.conversation.sender1 + '_lenMsgs'] + df[self.conversation.sender2 + '_lenMsgs']
        df['totAvgLen'] = df['totLenMsgs'].astype("float64") /  df['totNumMsgs'].astype("float64")

        return df

    def generateDataFrameSingleWordCountBy(self, mFun, word):
        agglomeratedMessages = IConvStats._getMessagesBy(mFun, self.conversation.messages)
        df = self._generateDataFrameAgglomeratedStatsBy(mFun, agglomeratedMessages)

        wOcc1 = [(d, IConvStats.getWordsCount(list(filter(lambda m: m.sender == self.conversation.sender1, a))))
                             for d, a in agglomeratedMessages.items()]
        wOcc2 = [(d, IConvStats.getWordsCount(list(filter(lambda m: m.sender == self.conversation.sender2, a))))
                             for d, a in agglomeratedMessages.items()]

        s1Count = [count[word] if word in count else (by, 0) for (by, count) in wOcc1]
        s2Count = [count[word] if word in count else (by, 0) for (by, count) in wOcc2]

        df[self.conversation.sender1 + '_count'] = np.array(s1Count)
        df[self.conversation.sender2 + '_count'] = np.array(s2Count)
        df['totCount'] = df[self.conversation.sender1 + '_count'] + df[self.conversation.sender2 + '_count']
        return df

    # @staticmethod
    # def getWordsCount(messages):
    #     text = [m.text.lower() for m in messages]
    #     wordsCount = collections.Counter(statsUtil.getWords(' '.join(text)))
    #     return wordsCount

    def getEmoticonsStats(self):
        numEmoticons = ConvStats._getEmoticonsStats(self.conversation.messages)
        numEmoticonsS1 = ConvStats._getEmoticonsStats(self.conversation.sender1Messages)
        numEmoticonsS2 = ConvStats._getEmoticonsStats(self.conversation.sender2Messages)
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

    def generateDataFrameEmoticonsStatsBy(self, mFun):
        agglomeratedMessages = IConvStats._getMessagesBy(mFun, self.conversation.messages)
        df = self.generateDataFrameAgglomeratedStatsBy(mFun, agglomeratedMessages)

        emoticonStatsS1 = [ConvStats._getEmoticonsStats(list(filter(lambda m: m.sender == self.conversation.sender1, a)))
                                 for _, a in agglomeratedMessages.items()]
        emoticonStatsS2 = [ConvStats._getEmoticonsStats(list(filter(lambda m: m.sender == self.conversation.sender2, a)))
                                 for _, a in agglomeratedMessages.items()]

        df[self.conversation.sender1 + '_numEmoticons'] = np.array(emoticonStatsS1)
        df[self.conversation.sender2 + '_numEmoticons'] = np.array(emoticonStatsS2)
        df['totNumEmoticons'] = df[self.conversation.sender1 + '_numEmoticons'] + df[self.conversation.sender2 + '_numEmoticons']
        df[self.conversation.sender1 + '_emoticonsRatio'] = df[self.conversation.sender1 + '_numEmoticons'] /  df[self.conversation.sender1 + '_lenMsgs']
        df[self.conversation.sender2 + '_emoticonsRatio'] = df[self.conversation.sender2 + '_numEmoticons'] /  df[self.conversation.sender2 + '_lenMsgs']
        df['totEmoticonsRatio'] = df['totNumEmoticons'] /  df['totLenMsgs']
        return df

    def getIntervalStats(self):
        start, end, interval = ConvStats._getIntervalStatsFor(self.conversation.messages)
        return start, end, interval

    @staticmethod
    def _getIntervalStatsFor(messages):
        start = datetime.strptime(messages[0].datetime, Message.DATE_TIME_FORMAT)
        end = datetime.strptime(messages[-1].datetime, Message.DATE_TIME_FORMAT)
        interval = end - start

        return messages[0].datetime, messages[-1].datetime, interval

    @staticmethod
    def _getMessagesBy(mFun, messages, groups=None):
        if not groups:
            groups = collections.defaultdict(list)
        for m in messages:
            groups[int(mFun(m))].append(m)
        return dict(groups)

    @staticmethod
    def getMessagesByYear(messages):
        return ConvStats._getMessagesBy(lambda m: m.getYear(), messages)

    @staticmethod
    def getMessagesByMonth(messages):
        groups = collections.defaultdict(list, [(i+1, []) for i in range(12)])
        return ConvStats._getMessagesBy(lambda m: m.getMonth(), messages, groups)

    @staticmethod
    def getMessagesByHour(messages):
        groups = collections.defaultdict(list, [(i, []) for i in range(24)])
        return ConvStats._getMessagesBy(lambda m: m.getHour(), messages, groups)

    def getDaysWithoutMessages(self):
        days = ConvStats._getDaysWithoutMessages(self.conversation.messages)
        return days

    @staticmethod
    def _getDaysWithoutMessages(messages):
        """Generate a date-range between the date of the first and last message
        and returns those dates for which there is no corresponding message in messages"""
        days = []
        start = datetime.strptime(messages[0].date, Message.DATE_FORMAT).date()
        end = datetime.strptime(messages[-1].date, Message.DATE_FORMAT).date()
        datelist = pd.date_range(start, end).tolist()
        agglomeratedMessages = ConvStats._getMessagesBy(lambda m: m.date, messages)
        for d in datelist:
            if not d.date().strftime(Message.DATE_FORMAT) in agglomeratedMessages:
                days.append(d.date())
        return days


    def getWordsMentioningStats(self):
        wordsSaidByBoth, wordsSaidJustByS1, wordsSaidJustByS2 = \
            ConvStats._getWordsMentioningStats(self.conversation.sender1Messages, self.conversation.sender2Messages)
        return wordsSaidByBoth, wordsSaidJustByS1, wordsSaidJustByS2

    @staticmethod
    def _getWordsMentioningStats(sender1Messages, sender2Messages):
        wordsSaidBySender1 = IConvStats.getWordsCount(sender1Messages).keys()
        wordsSaidBySender2 = IConvStats.getWordsCount(sender2Messages).keys()
        wordsSaidByBoth = set(wordsSaidBySender1).intersection(wordsSaidBySender2)
        wordsSaidJustByS1 = set(wordsSaidBySender1).difference(wordsSaidBySender2)
        wordsSaidJustByS2 = set(wordsSaidBySender2).difference(wordsSaidBySender1)
        return wordsSaidByBoth, wordsSaidJustByS1, wordsSaidJustByS2
