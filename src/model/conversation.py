import util.io as mio
import numpy as np
import pandas as pd
import util.stats as mstats
import os
import nltk

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

    #TODO add option for limit messages by date
    #TODO check presence of at least one message
    def loadMessages(self, limit=0):
        #TODO generalize for N senders
        self.messages, [self.sender1, self.sender2] = mio.parseMessagesFromFile(self.filepath, limit)
        self.sender1Messages = list(filter(lambda m: m.sender == self.sender1, self.messages))
        self.sender2Messages = list(filter(lambda m: m.sender == self.sender2, self.messages))
        self.messagesBySender[self.sender1] = self.sender1Messages
        self.messagesBySender[self.sender2] = self.sender2Messages

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

    #TODO Use index label instead of number
    def generateDataFrameAgglomeratedStatsBy(self, mFun, agglomeratedMessages=None):
        if not agglomeratedMessages:
            agglomeratedMessages = mstats.getMessagesBy(mFun, self.messages)
        aggBasicLengthStatsS1 = [mstats.getBasicLengthStats(list(filter(lambda m: m.sender == self.sender1, a)))
                                 for _, a in agglomeratedMessages.items()]
        aggBasicLengthStatsS2 = [mstats.getBasicLengthStats(list(filter(lambda m: m.sender == self.sender2, a)))
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
        c = [self.sender1 + '_numMsgs', self.sender2 + '_numMsgs',
             self.sender1 + '_lenMsgs', self.sender2 + '_lenMsgs',
             self.sender1 + '_avgLen', self.sender2 + '_avgLen',
             'totNumMsgs', 'totLenMsgs', 'totAvgLen']
        df = pd.DataFrame(data, index=list(agglomeratedMessages.keys()), columns=c)
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

        totCount = [c1+c2 for (c1,c2) in zip(s1Count, s2Count)]

        #TODO ??already add ratio
        df[self.sender1 + '_count'] = np.array(s1Count)
        df[self.sender2 + '_count'] = np.array(s2Count)
        df['totnumEmoticons'] = np.array(totCount)
        return df

    def generateDataFrameEmoticoStatsBy(self, mFun):
        agglomeratedMessages = mstats.getMessagesBy(mFun, self.messages)
        df = self.generateDataFrameAgglomeratedStatsBy(mFun, agglomeratedMessages)

        emoticonStatsS1 = [mstats.getEmoticonsStats(list(filter(lambda m: m.sender == self.sender1, a)))
                                 for _, a in agglomeratedMessages.items()]
        emoticonStatsS2 = [mstats.getEmoticonsStats(list(filter(lambda m: m.sender == self.sender2, a)))
                                 for _, a in agglomeratedMessages.items()]

        #emoticonStatsS1 = [y for (x, y) in eStats1]
        #emoticonStatsS2 = [y for (x, y) in eStats2]

        totEmoStats = list(sum(t) for t in zip(emoticonStatsS1, emoticonStatsS2))
        s1Ratio = [n/l if l != 0 else 0 for (n, l) in zip(emoticonStatsS1, df.ix[:, 2])]
        s2Ratio = [n/l if l != 0 else 0 for (n, l) in zip(emoticonStatsS2, df.ix[:, 3])]
        totRatio = [n/l if l != 0 else 0 for (n, l) in zip(totEmoStats, df.ix[:, 7])]

        df[self.sender1 + '_numEmoticons'] = np.array(emoticonStatsS1)
        df[self.sender2 + '_numEmoticons'] = np.array(emoticonStatsS2)
        df['totnumEmoticons'] = np.array(totEmoStats)
        df[self.sender1 + '_emoticonsRatio'] = np.array(s1Ratio)
        df[self.sender2 + '_emoticonsRatio'] = np.array(s2Ratio)
        df['totEmoticonsRatio'] = np.array(totRatio)
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
