import unittest
from model.conversation import Conversation
import util.plotting as mplot
import util.io as mio
import seaborn as sns
import pandas as pd
import numpy as np
from util.convStats import ConvStats
from util.convStatsDataFrame import ConvStatsDataFrame

class PlottingTestCase(unittest.TestCase):
    def getConversation(self, filepath):
        conv = Conversation(filepath)
        conv.loadMessages(0)
        conv.stats = ConvStatsDataFrame(conv)
        #conv.stats = ConvStats(conv)
        return conv

    def test_basicLengthStats(self):
        conv = self.getConversation(mio.getResourcesPath() + "\\unittest\\test_nltk_conv.txt")
        mplot.plotBasicLengthStats(conv)

    def test_hoursStats(self):
        conv = self.getConversation(mio.getResourcesPath() + "\\unittest\\test.txt")
        data = conv.stats.generateDataFrameAgglomeratedStatsByHour()
        mplot.plotHoursStats(data)

    def test_monthStats(self):
        conv = self.getConversation(mio.getResourcesPath() + "\\unittest\\test.txt")
        data = conv.stats.generateDataFrameAgglomeratedStatsByYearAndMonth()
        mplot.plotMonthStats(data)

    def test_MsgsLen(self):
        conv = self.getConversation(mio.getResourcesPath() + "\\unittest\\test.txt")
        # aggMesgs = conv.stats.getMessagesByYear(conv.messages)
        # d= {}
        # for year, messages in aggMesgs.items():
        #     print(year)
        #     aggMesgsByMonth = conv.stats.getMessagesByMonth(messages)
        #     values = []
        #     index = set([])
        #     for month, messagesByMonth in aggMesgsByMonth.items():
        #         values.append(conv.stats.getTotalLengthOf(messagesByMonth))
        #         index.add(int(month))
        #     d[year] = pd.Series(values, index)
        #
        # df = pd.DataFrame(d).transpose()
        # print(df)
        df = conv.stats.generateDataFrameAgglomeratedStatsByYearAndMonth()
        #data = conv.testGenerateDataFrameAgglomeratedStatsBy(lambda m: m.getHour())
        #data.index.name = "Hours"
        df.drop('avg', axis=1, inplace=True)
        df.drop('text', axis=1, inplace=True)
        df = df.loc[df['sender'] == 'total']
        df.drop('sender', axis=1, inplace=True)
        res = df.pivot('year', 'month', 'len')
        print(res)
        sns.heatmap(res)
        sns.plt.show()

    def test_RichnessVariation(self):
        conv = self.getConversation(mio.getResourcesPath() + "\\unittest\\test_nltk_conv.txt")
        aggMesgs = conv.stats.getMessagesByMonth(conv.messages)
        values = []
        index = set([])
        for month, messagesByMonth in aggMesgs.items():
            values.append(conv.stats._getLexicalStats(messagesByMonth)[2])
            index.add(month)
        res = pd.Series(values, index)
        print(res)
        df = pd.DataFrame(res)
        sns.barplot(data=df.transpose())
        sns.plt.show()

    def test_WordUsage(self):
        word = "hello"
        conv = self.getConversation(mio.getResourcesPath() + "\\unittest\\test.txt")
        aggMesgs = conv.stats.getMessagesByMonth(conv.messages)
        values = []
        index = set([])
        for month, messagesByMonth in aggMesgs.items():
            wordsCount = conv.stats.getWordsCount(messagesByMonth)
            values.append(wordsCount.get(word, 0))
            index.add(month)
        sns.boxplot(x=list(index), y=values)
        sns.despine(offset=10, trim=True)
        sns.plt.show()

if __name__ == '__main__':
    unittest.main()
