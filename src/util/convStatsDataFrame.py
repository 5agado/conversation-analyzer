from util.iConvStats import IConvStats
import pandas as pd
import collections
from util import statsUtil

class ConvStatsDataFrame(IConvStats):
    def __init__(self, conversation):
        super().__init__(conversation)
        self.df = self._getConversationAsDataFrame()

    def _getConversationAsDataFrame(self):
        if len(self.conversation.messages) == 0:
            raise Exception("No messages found for conversation " + self.filepath)
        df = pd.DataFrame([[msg.date, msg.time, msg.sender, msg.text] for msg in self.conversation.messages],
                          columns=['date', 'time', 'sender', 'text'])
        return df

    def getMessagesTotalLength(self):
        msgsLen = self.df['text'].apply(lambda x: len(x))
        totalLength = msgsLen.sum()
        return totalLength

    def getBasicLengthStats(self, sender=None):
        basicLengthStatsDf = self._getBasicLengthStats()
        if not sender:
            totalNum, totalLength, avgLegth = basicLengthStatsDf.loc['total'].tolist()
        else:
            totalNum, totalLength, avgLegth = basicLengthStatsDf.loc[sender].tolist()
        return totalNum, totalLength, avgLegth

    def _getBasicLengthStats(self):
        res = self.df.rename(columns={'text':'numMsgs'})
        res['lenMsgs'] = res['numMsgs'].apply(lambda x: len(x))
        res = res.groupby(['sender']).agg({'numMsgs' : 'count',
                                                       'lenMsgs' : 'sum'})
        res.loc['total'] = res.sum()
        res['avgLen'] = res['lenMsgs']/res['numMsgs']
        #res.reset_index(level=0, inplace=True)
        return res[['numMsgs', 'lenMsgs', 'avgLen']]

    def getLexicalStats(self, sender=None):
        lexicalStatsDf = self._getLexicalStats()
        print(lexicalStatsDf)
        if not sender:
            tokensCount, vocabularyCount, lexicalRichness = lexicalStatsDf.loc['total'].tolist()
        else:
            tokensCount, vocabularyCount, lexicalRichness = lexicalStatsDf.loc[sender].tolist()
        return tokensCount, vocabularyCount, lexicalRichness

    def _getLexicalStats(self):
        res = self.df.rename(columns={'text':'text'})
        res['year'] = res['date'].apply(lambda x: str.split(x, '.')[0])
        res['month'] = res['date'].apply(lambda x: str.split(x, '.')[1])
        res = res.groupby(['sender', 'year', 'month'], as_index=False).agg({'text' : lambda x: statsUtil.getWords(" ".join(x))})
        res['tokensCount'] = res['text'].apply(lambda x: len(x))
        res['vocabularyCount'] = res['text'].apply(lambda x: len(set(x)))

        res.drop('text', axis=1, inplace=True)
        tot = res.groupby(['year', 'month'], as_index=False).sum()
        tot['sender'] = "total"
        res = pd.concat([res, tot])

        #TODO Missing tokencount = zero case
        res['lexicalRichness'] = res['vocabularyCount']/res['tokensCount']

        return res

    def generateDataFrameAgglomeratedStatsByHour(self):
        res = self._generateDataFrameAgglomeratedStatsBy('time', lambda x: str.split(x, ':')[0], 'hour')
        return res

    def generateDataFrameAgglomeratedStatsByMonth(self):
        res = self._generateDataFrameAgglomeratedStatsBy('date', lambda x: str.split(x, '.')[1], 'month')
        return res

    def generateDataFrameAgglomeratedStatsByYearAndMonth(self):
        res = self.df.rename(columns={'text':'numMsgs'})
        res['lenMsgs'] = res['numMsgs'].apply(lambda x: len(x))

        res['year'] = res['date'].apply(lambda x: str.split(x, '.')[0])
        res['month'] = res['date'].apply(lambda x: str.split(x, '.')[1])
        res = res.groupby(['sender', 'year', 'month'], as_index=False).agg({'numMsgs' : 'count',
                                                       'lenMsgs' : 'sum'})

        tot = res.groupby(['year', 'month'], as_index=False).sum()
        tot['sender'] = "total"
        res = pd.concat([res, tot])
        res['avgLen'] = res['lenMsgs']/res['numMsgs']
        return res

    def _generateDataFrameAgglomeratedStatsBy(self, colName, mFun, aggName):
        res = self.df.rename(columns={'text':'numMsgs'})
        res['lenMsgs'] = res['numMsgs'].apply(lambda x: len(x))
        res[aggName] = res[colName].apply(mFun)
        res = res.groupby(['sender', aggName], as_index=False).agg({'numMsgs' : 'count',
                                                       'lenMsgs' : 'sum'})

        tot = res.groupby([aggName], as_index=False).sum()
        tot['sender'] = "total"
        res = pd.concat([res, tot])
        res['avgLen'] = res['lenMsgs']/res['numMsgs']
        return res

    def generateDataFrameSingleWordCountBy(self, word):
        fun = lambda x: ConvStatsDataFrame.getWordsCount(" ".join(x))[word]
        res = self.df.rename(columns={'text':'wordCount'})

        res['year'] = res['date'].apply(lambda x: str.split(x, '.')[0])
        res['month'] = res['date'].apply(lambda x: str.split(x, '.')[1])
        res = res.groupby(['sender', 'year', 'month'], as_index=False).agg({'wordCount' : fun})

        tot = res.groupby(['year', 'month'], as_index=False).sum()
        tot['sender'] = "total"
        res = pd.concat([res, tot])
        return res

    @staticmethod
    def getWordsCount(text):
        wordsCount = collections.Counter(statsUtil.getWords(text))
        return wordsCount