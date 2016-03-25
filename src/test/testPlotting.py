import unittest

import seaborn as sns

import util.io as mio
import util.plotting as mplot
from model.conversationDataframe import ConversationDataframe
from stats.iConvStats import IConvStats


class PlottingTestCase(unittest.TestCase):
    TEST_FILE = "\\unittest\\test_plotting.txt"
    anonymise = True

    @classmethod
    def setUpClass(cls):
        cls.conv = PlottingTestCase.getConversation(mio.getResourcesPath() + PlottingTestCase.TEST_FILE)

    @staticmethod
    def getConversation(filepath):
        conv = ConversationDataframe(filepath)
        conv.loadMessages(0)

        #anonymise conversation
        if PlottingTestCase.anonymise:
            sendersAliases = ['Donnie', 'Frank']
            if len(sendersAliases) == len(conv.senders):
                aliasesMap = {key:sendersAliases[i] for i, key in enumerate(conv.senders)}
                conv.messages.replace({'sender':aliasesMap}, inplace=True)
                conv.senders = sendersAliases

        return conv

    def test_basicLengthStatsByYearAndMonth(self):
        data = self.conv.stats.generateStatsByYearAndMonth(IConvStats.STATS_NAME_BASICLENGTH)
        data = data[data.sender != 'total']
        mplot.plotBasicLengthStatsByYearAndMonth(data, ['2015'])

    def test_singleLengthStatByHour(self):
        data = self.conv.stats.generateStatsByHour(IConvStats.STATS_NAME_BASICLENGTH)
        #data = mio.loadDataFromFile(self.conv.statsFolder + '\\' + IConvStats.STATS_NAME_BASICLENGTH + 'byHour.txt')
        data = data[data.sender != 'total']
        mplot.plotSingleBasicLengthStatByHour(data, 'lenMsgs')

    def test_basicLengthStatsByMonthAndHourForYear(self):
        data = self.conv.stats.generateStatsByYearMonthHour(IConvStats.STATS_NAME_BASICLENGTH)
        data = data[data.sender != 'total']
        mplot.plotBasicLengthStatsByMonthAndHourForYear(data, '2015')

    def test_singleBasicLengthStatByYearAndMonth(self):
        data = self.conv.stats.generateStatsByYearAndMonth(IConvStats.STATS_NAME_BASICLENGTH)
        data = data[data.sender != 'total']
        mplot.plotSingleBasicLengthStatByYearAndMonth(data, 'lenMsgs')

    def test_singleBasicLengthStatHeatmap(self):
        data = self.conv.stats.generateStatsByYearMonthDay(IConvStats.STATS_NAME_BASICLENGTH)

        data.drop('avgLen', axis=1, inplace=True)
        data.drop('numMsgs', axis=1, inplace=True)
        data = data.loc[data['sender'] == 'total']
        data.drop('sender', axis=1, inplace=True)

        mplot.plotSingleBasicLengthStatHeatmap(data, 'lenMsgs', ['2015'])

    def test_richnessVariation(self):
        data = self.conv.stats.generateStatsByYearAndMonth(IConvStats.STATS_NAME_LEXICAL)
        mplot.plotRichnessVariation(data)

    def test_singleWordUsage(self):
        word = "the"
        data = self.conv.stats.generateStatsByYearMonthDay(IConvStats.STATS_NAME_WORDCOUNT, word=word)
        data = data.reset_index()
        mplot.plotSingleWordUsage(data, word, ['2014'])

    def test_wordUsage(self):
        words = ['the', 'hello', 'a', 'when']
        data = self.conv.stats.generateStatsByYearMonthDay(IConvStats.STATS_NAME_WORDCOUNT)
        #data = data.drop(['sender', 'count', 'frequency'], 1)
        data = data.reset_index()
        mplot.plotWordsUsage(data, words, ['2014'])
        #mplot.plotWordsUsageByHour(data, words, ['2014'])

    def test_wordFrequency(self):
        df = self.conv.stats.generateStatsByHour(IConvStats.STATS_NAME_WORDCOUNT)
        df = df.reset_index()
        sns.violinplot(y="word", x="frequency", hue='sender', data=df.head(10));
        sns.plt.show()

if __name__ == '__main__':
    unittest.main()
