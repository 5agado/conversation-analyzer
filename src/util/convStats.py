# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import collections
import statistics
import numpy as np
import pandas as pd
import re
import nltk
import logging
import sys
import util.io as mio
import math
from model.message import Message
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
            agglomeratedMessages = self.getMessagesBy(mFun, self.conversation.messages)
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
