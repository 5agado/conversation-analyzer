import util.io as mio
import util.stats as mstats
import os

class Conversation:
    def __init__(self, filepath):
        self.sender1 = None
        self.sender2 = None
        self.filepath = filepath
        self.folder = os.path.dirname(filepath) + '\stats'
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        self.messages = None
        self.sender1Messages = None
        self.sender2Messages = None
        self.messagesBySender = {self.sender1:self.sender1Messages, self.sender2:self.sender2Messages}

    def loadMessages(self, limit = 0):
        #TODO generalize for N senders
        self.messages, [self.sender1, self.sender2] = mio.parseMessagesFromFile(self.filepath, limit)
        self.sender1Messages = list(filter(lambda m: m.sender == self.sender1, self.messages))
        self.sender2Messages = list(filter(lambda m: m.sender == self.sender2, self.messages))
        self.messagesBySender[self.sender1] = self.sender1Messages
        self.messagesBySender[self.sender2] = self.sender2Messages

    def getIntervalStats(self):
        start, end, interval = mstats.getIntervalStatsFor(self.messages)
        return start, end, interval

    def getBasicLengthStats(self, sender=None):
        if not sender:
            totalNum, totalLength, avgLegth = mstats.getBasicLengthStats(self.messages)
        else:
            totalNum, totalLength, avgLegth = mstats.getBasicLengthStats(self.messagesBySender[sender])
        return  totalNum, totalLength, avgLegth

    def generateDataFrameAgglomeratedStatsBy(self, mFun):
        df = mstats.generateDataFrameAgglomeratedStatsBy(mFun, self.messages, self.sender1, self.sender2)
        return df

    def getWordsCountStats(self, limit=0):
        wCount, wCountS1, wCountS2 = mstats.getWordsCountStats(self.messages, self.sender1Messages, self.sender2Messages, limit)
        return wCount, wCountS1, wCountS2

    def getWordsMentioningStats(self):
        wordsSaidByBoth, wordsSaidJustByS1, wordsSaidJustByS2 = mstats.getWordsMentioningStats(self.sender1Messages, self.sender2Messages)
        return  wordsSaidByBoth, wordsSaidJustByS1, wordsSaidJustByS2
