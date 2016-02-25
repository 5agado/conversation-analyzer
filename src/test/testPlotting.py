import unittest
from model.conversation import Conversation
import util.plotting as mplot
import util.io as mio
import seaborn as sns
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

    def test_basicLengthStatsPie(self):
        conv = self.getConversation(mio.getResourcesPath() + PlottingTestCase.TEST_FILE)
        mplot.plotBasicLengthStatsPie(conv)

    def test_basicLengthStatsByYearAndMonth(self):
        conv = self.getConversation(mio.getResourcesPath() + PlottingTestCase.TEST_FILE)
        data = conv.stats.generateStatsByYearAndMonth(IConvStats.STATS_NAME_BASICLENGTH)
        data = data[data.sender != 'total']
        mplot.plotBasicLengthStatsByYearAndMonth(data, ['2015'])

    def test_singleLengthStatByHour(self):
        conv = self.getConversation(mio.getResourcesPath() + PlottingTestCase.TEST_FILE)
        data = conv.stats.generateStatsByHour(IConvStats.STATS_NAME_BASICLENGTH)
        #data = conv.stats.generateStatsByYearAndHour(IConvStats.STATS_NAME_BASICLENGTH)
        data = data[data.sender != 'total']
        mplot.plotSingleBasicLengthStatByHour(data, 'lenMsgs')
        #mplot.plotSingleBasicLengthStatByYearAndHour(data, 'lenMsgs')

    def test_basicLengthStatsByMonthAndHourForYear(self):
        conv = self.getConversation(mio.getResourcesPath() + PlottingTestCase.TEST_FILE)
        data = conv.stats.generateStatsByYearMonthHour(IConvStats.STATS_NAME_BASICLENGTH)
        data = data[data.sender != 'total']
        mplot.plotBasicLengthStatsByMonthAndHourForYear(data, '2015')

    def test_singleBasicLengthStatByYearAndMonth(self):
        conv = self.getConversation(mio.getResourcesPath() + PlottingTestCase.TEST_FILE)
        data = conv.stats.generateStatsByYearAndMonth(IConvStats.STATS_NAME_BASICLENGTH)
        data = data[data.sender != 'total']
        mplot.plotSingleBasicLengthStatByYearAndMonth(data, 'lenMsgs')

    def test_singleBasicLengthStatHeatmap(self):
        conv = self.getConversation(mio.getResourcesPath() + PlottingTestCase.TEST_FILE)
        data = conv.stats.generateStatsByYearMonthDay(IConvStats.STATS_NAME_BASICLENGTH)

        data.drop('avgLen', axis=1, inplace=True)
        data.drop('numMsgs', axis=1, inplace=True)
        data = data.loc[data['sender'] == 'total']
        data.drop('sender', axis=1, inplace=True)

        mplot.plotSingleBasicLengthStatHeatmap(data, 'lenMsgs', ['2015'])

    def test_richnessVariation(self):
        conv = self.getConversation(mio.getResourcesPath() + PlottingTestCase.TEST_FILE)
        data = conv.stats.generateStatsByYearAndMonth(IConvStats.STATS_NAME_LEXICAL)
        mplot.plotRichnessVariation(data)

    def test_singleWordUsage(self):
        word = "the"
        conv = self.getConversation(mio.getResourcesPath() + PlottingTestCase.TEST_FILE)
        data = conv.stats.generateStatsByYearMonthDay(IConvStats.STATS_NAME_WORDCOUNT, word=word)
        data = data.reset_index()
        mplot.plotSingleWordUsage(data, word, ['2014'])

    def test_wordUsage(self):
        words = ['the', 'hello', 'a', 'when']
        conv = self.getConversation(mio.getResourcesPath() + PlottingTestCase.TEST_FILE)
        #data = conv.stats.generateAgglomeratedStatsByHour(IConvStats.STATS_NAME_WORDCOUNT)
        data = conv.stats.generateStatsByYearMonthDay(IConvStats.STATS_NAME_WORDCOUNT)
        #data = data.drop(['sender', 'count', 'frequency'], 1)
        data = data.reset_index()
        mplot.plotWordsUsage(data, words, ['2014'])
        #mplot.plotWordsUsageByHour(data, words, ['2014'])

    def test_wordFrequency(self):
        conv = self.getConversation(mio.getResourcesPath() + PlottingTestCase.TEST_FILE)
        df = conv.stats.generateStatsByHour(IConvStats.STATS_NAME_WORDCOUNT)
        df = df.reset_index()
        sns.violinplot(y="word", x="frequency", hue='sender', data=df.head(10));
        sns.plt.show()

if __name__ == '__main__':
    unittest.main()
