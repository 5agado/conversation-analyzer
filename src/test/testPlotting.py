import unittest
from model.conversation import Conversation
import util.plotting as mplot
import util.io as mio
from util.convStats import ConvStats
from util.iConvStats import IConvStats
from util.convStatsDataFrame import ConvStatsDataFrame

class PlottingTestCase(unittest.TestCase):
    TEST_FILE = "\\unittest\\test_plotting.txt"

    def getConversation(self, filepath):
        conv = Conversation(filepath)
        conv.loadMessages(0)

        #anonymise conversation
        sendersAliases = ['Donnie', 'Frank']
        aliasesMap = {conv.sender1 : sendersAliases[0], conv.sender2 : sendersAliases[1]}
        for m in conv.messages:
            m.sender = aliasesMap[m.sender]
        conv.sender1 = sendersAliases[0]
        conv.sender2 = sendersAliases[1]

        conv.stats = ConvStatsDataFrame(conv)
        #conv.stats = ConvStats(conv)
        return conv

    def test_basicLengthStats(self):
        conv = self.getConversation(mio.getResourcesPath() + PlottingTestCase.TEST_FILE)
        mplot.plotBasicLengthStats(conv)

    def test_hoursStats(self):
        conv = self.getConversation(mio.getResourcesPath() + PlottingTestCase.TEST_FILE)
        data = conv.stats.generateAgglomeratedStatsByHour(IConvStats.STATS_NAME_BASICLENGTH)
        data = data[data.sender != 'total']
        mplot.plotHoursStats(data)

    def test_monthStats(self):
        conv = self.getConversation(mio.getResourcesPath() + PlottingTestCase.TEST_FILE)
        data = conv.stats.generateAgglomeratedStatsByYearAndMonth(IConvStats.STATS_NAME_BASICLENGTH)
        data = data[data.sender != 'total']
        mplot.plotMonthStats(data)

    def test_MsgsLen(self):
        conv = self.getConversation(mio.getResourcesPath() + PlottingTestCase.TEST_FILE)
        data = conv.stats.generateAgglomeratedStatsByYearMonthDay(IConvStats.STATS_NAME_BASICLENGTH)

        data.drop('avgLen', axis=1, inplace=True)
        data.drop('numMsgs', axis=1, inplace=True)
        data = data.loc[data['sender'] == 'total']
        data.drop('sender', axis=1, inplace=True)

        mplot.plotBasicLengthStatsHeatmap(data)

    def test_RichnessVariation(self):
        conv = self.getConversation(mio.getResourcesPath() + PlottingTestCase.TEST_FILE)
        data = conv.stats.generateAgglomeratedStatsByYearAndMonth(IConvStats.STATS_NAME_LEXICAL)
        mplot.plotRichnessVariation(data)

    def test_WordUsage(self):
        word = "the"
        conv = self.getConversation(mio.getResourcesPath() + PlottingTestCase.TEST_FILE)
        data = conv.stats.generateAgglomeratedStatsByYearAndMonth(IConvStats.STATS_NAME_WORDCOUNT)
        print(data)
        #data = conv.stats.generateDataFrameSingleWordCountBy(word)
        data = data[data.sender != 'total']

        #mplot.plotWordUsage(data, word)

if __name__ == '__main__':
    unittest.main()
