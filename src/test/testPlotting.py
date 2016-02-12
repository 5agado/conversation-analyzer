import unittest
from model.conversation import Conversation
import util.plotting as mplot
import util.io as mio
from util.convStats import ConvStats
from util.convStatsDataFrame import ConvStatsDataFrame

class PlottingTestCase(unittest.TestCase):
    TEST_FILE = "\\unittest\\test_plotting.txt"

    def getConversation(self, filepath):
        conv = Conversation(filepath)
        conv.loadMessages(0)
        conv.stats = ConvStatsDataFrame(conv)
        #conv.stats = ConvStats(conv)
        return conv

    def test_basicLengthStats(self):
        conv = self.getConversation(mio.getResourcesPath() + PlottingTestCase.TEST_FILE)
        mplot.plotBasicLengthStats(conv)

    def test_hoursStats(self):
        conv = self.getConversation(mio.getResourcesPath() + PlottingTestCase.TEST_FILE)
        data = conv.stats.generateDataFrameAgglomeratedStatsByHour()
        data = data[data.sender != 'total']
        mplot.plotHoursStats(data)

    def test_monthStats(self):
        conv = self.getConversation(mio.getResourcesPath() + PlottingTestCase.TEST_FILE)
        data = conv.stats.generateDataFrameAgglomeratedStatsByYearAndMonth()
        data = data[data.sender != 'total']
        mplot.plotMonthStats(data)

    def test_MsgsLen(self):
        conv = self.getConversation(mio.getResourcesPath() + PlottingTestCase.TEST_FILE)
        data = conv.stats.generateDataFrameAgglomeratedStatsByYearAndMonth()

        data.drop('avgLen', axis=1, inplace=True)
        data.drop('numMsgs', axis=1, inplace=True)
        data = data.loc[data['sender'] == 'total']
        data.drop('sender', axis=1, inplace=True)

        mplot.plotBasicLengthStatsHeatmap(data)

    def test_RichnessVariation(self):
        conv = self.getConversation(mio.getResourcesPath() + PlottingTestCase.TEST_FILE)
        data = conv.stats._getLexicalStats()
        mplot.plotRichnessVariation(data)

    def test_WordUsage(self):
        word = "the"
        conv = self.getConversation(mio.getResourcesPath() + PlottingTestCase.TEST_FILE)
        data = conv.stats.generateDataFrameSingleWordCountBy(word)
        data = data[data.sender != 'total']

        mplot.plotWordUsage(data, word)

if __name__ == '__main__':
    unittest.main()
