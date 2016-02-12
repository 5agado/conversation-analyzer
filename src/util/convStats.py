# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import collections
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

    @staticmethod
    def getWordsCount(messages):
        text = [m.text.lower() for m in messages]
        wordsCount = collections.Counter(statsUtil.getWords(' '.join(text)))
        return wordsCount
