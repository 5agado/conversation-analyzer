import src.util.io as mio
import src.util.stats as mstats
import os

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

    def getIntervalStats(self):
        start, end, interval = mstats.getIntervalStatsFor(self.messages)
        return start, end, interval

    def getDaysWithoutMessages(self):
        days = mstats.getDaysWithoutMessages(self.messages)
        return days

    def getDelayStats(self):
        overallDelay, delay = mstats.getDelayStatsFor(self)
        return overallDelay, delay

    def getDelayStatsByLength(self):
        delay, senderDelay = mstats.getDelayStatsByLength(self)
        return delay, senderDelay

    def getBasicLengthStats(self, sender=None):
        if not sender:
            totalNum, totalLength, avgLegth = mstats.getBasicLengthStats(self.messages)
        else:
            totalNum, totalLength, avgLegth = mstats.getBasicLengthStats(self.messagesBySender[sender])
        return totalNum, totalLength, avgLegth

    def generateDataFrameAgglomeratedStatsBy(self, mFun):
        df = mstats.generateDataFrameAgglomeratedStatsBy(mFun, self.messages, self.sender1, self.sender2)
        return df

    def generateDataFrameEmoticoStatsBy(self, mFun):
        df = mstats.generateDataFrameEmoticoStatsBy(mFun, self.messages, self.sender1, self.sender2)
        return df

    def generateDataFrameSingleWordCountBy(self, mFun, word):
        df = mstats.generateDataFrameSingleWordCountBy(mFun, word, self.messages, self.sender1, self.sender2)
        return df

    def getWordsCountStats(self, limit=0):
        wCount, wCountS1, wCountS2 = \
            mstats.getWordsCountStats(self.messages, self.sender1Messages, self.sender2Messages, limit)
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
