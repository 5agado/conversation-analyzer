import util.io as mio
import numpy as np
import logging
import pandas as pd
import time
import util.stats as mstats
import os
import nltk
import sys

class Conversation:
    def __init__(self, filepath):
        self.sender1 = None
        self.sender2 = None
        self.filepath = filepath
        self.statsFolder = os.path.dirname(filepath) + '\\stats'
        if not os.path.exists(self.statsFolder):
            os.makedirs(self.statsFolder)
        self.messages = None
        self.sender1Messages = None
        self.sender2Messages = None
        self.messagesBySender = {self.sender1:self.sender1Messages, self.sender2:self.sender2Messages}

    def loadMessages(self, limit=0, startDate=None, endDate=None):
        logging.info("Start loading messages for conversation " + self.filepath)
        start = time.time()

        self.messages, [self.sender1, self.sender2] = \
            mio.parseMessagesFromFile(self.filepath, limit, startDate, endDate)
        if len(self.messages) == 0:
            raise Exception("No messages found for conversation " + self.filepath)
        self.sender1Messages = list(filter(lambda m: m.sender == self.sender1, self.messages))
        self.sender2Messages = list(filter(lambda m: m.sender == self.sender2, self.messages))
        self.messagesBySender[self.sender1] = self.sender1Messages
        self.messagesBySender[self.sender2] = self.sender2Messages

        end = time.time()
        logging.info("Loading completed in {0:.2f}s".format(end-start))

    def getAsNLTKText(self, sender=None):
        if sender:
            return nltk.Text(self.getConvTextBySender(sender))
        else:
            return nltk.Text(self.getEntireConvText())

    def getEntireConvText(self):
        text = ''
        for m in self.messages:
            text += m.text + '\n'
        return text

    def getConvTextBySender(self, sender):
        text = ''
        for m in self.messages:
            if m.sender == sender:
                text += m.text + '\n'
        return text

    def getIntervalStats(self):
        start, end, interval = mstats.getIntervalStatsFor(self.messages)
        return start, end, interval

    def getDaysWithoutMessages(self):
        days = mstats.getDaysWithoutMessages(self.messages)
        return days

    def getDelayStats(self):
        delay = mstats.getDelayStatsFor(self.messages)
        return delay

    def getDelayStatsByLength(self):
        delay, senderDelay = mstats.getDelayStatsByLength(self.messages)
        return delay, senderDelay

    def getBasicLengthStats(self, sender=None):
        if not sender:
            totalNum, totalLength, avgLegth = mstats.getBasicLengthStats(self.messages)
        else:
            totalNum, totalLength, avgLegth = mstats.getBasicLengthStats(self.messagesBySender[sender])
        return totalNum, totalLength, avgLegth

    def getLexicalStats(self, sender=None):
        if not sender:
            tokensCount, vocabularyCount, lexicalRichness = mstats.getLexicalStats(self.messages)
        else:
            tokensCount, vocabularyCount, lexicalRichness = mstats.getLexicalStats(self.messagesBySender[sender])
        return tokensCount, vocabularyCount, lexicalRichness

    def generateDataFrameAgglomeratedStatsBy(self, mFun, agglomeratedMessages=None):
        if not agglomeratedMessages:
            agglomeratedMessages = mstats.getMessagesBy(mFun, self.messages)
        aggBasicLengthStatsS1 = [mstats.getBasicLengthStats(list(filter(lambda m: m.sender == self.sender1, a)))
                                 for _, a in agglomeratedMessages.items()]
        aggBasicLengthStatsS2 = [mstats.getBasicLengthStats(list(filter(lambda m: m.sender == self.sender2, a)))
                                 for _, a in agglomeratedMessages.items()]

        df = pd.DataFrame(index=list(agglomeratedMessages.keys()))

        df[self.sender1 + '_numMsgs'] = [i[0] for i in aggBasicLengthStatsS1]
        df[self.sender2 + '_numMsgs'] = [i[0] for i in aggBasicLengthStatsS2]
        df[self.sender1 + '_lenMsgs'] = [i[1] for i in aggBasicLengthStatsS1]
        df[self.sender2 + '_lenMsgs'] = [i[1] for i in aggBasicLengthStatsS2]
        df[self.sender1 + '_avgLen'] = [i[2] for i in aggBasicLengthStatsS1]
        df[self.sender2 + '_avgLen'] = [i[2] for i in aggBasicLengthStatsS2]
        df['totNumMsgs'] = df[self.sender1 + '_numMsgs'] + df[self.sender2 + '_numMsgs']
        df['totLenMsgs'] = df[self.sender1 + '_lenMsgs'] + df[self.sender2 + '_lenMsgs']
        df['totAvgLen'] = df['totLenMsgs'].astype("float64") /  df['totNumMsgs'].astype("float64")

        return df

    def generateDataFrameSingleWordCountBy(self, mFun, word):
        agglomeratedMessages = mstats.getMessagesBy(mFun, self.messages)
        df = self.generateDataFrameAgglomeratedStatsBy(mFun, agglomeratedMessages)

        wOcc1 = [(d, mstats.getWordsCount(list(filter(lambda m: m.sender == self.sender1, a))))
                             for d, a in agglomeratedMessages.items()]
        wOcc2 = [(d, mstats.getWordsCount(list(filter(lambda m: m.sender == self.sender2, a))))
                             for d, a in agglomeratedMessages.items()]

        s1Count = [count[word] if word in count else (by, 0) for (by, count) in wOcc1]
        s2Count = [count[word] if word in count else (by, 0) for (by, count) in wOcc2]

        df[self.sender1 + '_count'] = np.array(s1Count)
        df[self.sender2 + '_count'] = np.array(s2Count)
        df['totCount'] = df[self.sender1 + '_count'] + df[self.sender2 + '_count']
        return df

    def generateDataFrameEmoticoStatsBy(self, mFun):
        agglomeratedMessages = mstats.getMessagesBy(mFun, self.messages)
        df = self.generateDataFrameAgglomeratedStatsBy(mFun, agglomeratedMessages)

        emoticonStatsS1 = [mstats.getEmoticonsStats(list(filter(lambda m: m.sender == self.sender1, a)))
                                 for _, a in agglomeratedMessages.items()]
        emoticonStatsS2 = [mstats.getEmoticonsStats(list(filter(lambda m: m.sender == self.sender2, a)))
                                 for _, a in agglomeratedMessages.items()]

        df[self.sender1 + '_numEmoticons'] = np.array(emoticonStatsS1)
        df[self.sender2 + '_numEmoticons'] = np.array(emoticonStatsS2)
        df['totNumEmoticons'] = df[self.sender1 + '_numEmoticons'] + df[self.sender2 + '_numEmoticons']
        df[self.sender1 + '_emoticonsRatio'] = df[self.sender1 + '_numEmoticons'] /  df[self.sender1 + '_lenMsgs']
        df[self.sender2 + '_emoticonsRatio'] = df[self.sender2 + '_numEmoticons'] /  df[self.sender2 + '_lenMsgs']
        df['totEmoticonsRatio'] = df['totNumEmoticons'] /  df['totLenMsgs']
        return df

    def getWordsCountStats(self, limit=0):
        wCount = mstats.getWordsCountStats(self.messages, limit)
        wCountS1 = mstats.getWordsCountStats(self.sender1Messages, limit)
        wCountS2 = mstats.getWordsCountStats(self.sender2Messages, limit)

        return wCount, wCountS1, wCountS2

    def getWordsMentioningStats(self):
        wordsSaidByBoth, wordsSaidJustByS1, wordsSaidJustByS2 = \
            mstats.getWordsMentioningStats(self.sender1Messages, self.sender2Messages)
        return wordsSaidByBoth, wordsSaidJustByS1, wordsSaidJustByS2

    def getEmoticonsStats(self):
        numEmoticons = mstats.getEmoticonsStats(self.messages)
        numEmoticonsS1 = mstats.getEmoticonsStats(self.sender1Messages)
        numEmoticonsS2 = mstats.getEmoticonsStats(self.sender2Messages)
        return  numEmoticons, numEmoticonsS1, numEmoticonsS2
