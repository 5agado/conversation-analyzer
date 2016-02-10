from util.iConvStats import IConvStats
import pandas as pd

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

    def _getBasicLengthStats(self):
        res = self.df.rename(columns={'text':'numMsgs'})
        res['lenMsgs'] = res['numMsgs'].apply(lambda x: len(x))
        res = res.groupby(['sender']).agg({'numMsgs' : 'count',
                                                       'lenMsgs' : 'sum'})
        res.loc['total'] = res.sum()
        res['avgLen'] = res['lenMsgs']/res['numMsgs']
        #res.reset_index(level=0, inplace=True)
        return res[['numMsgs', 'lenMsgs', 'avgLen']]

    def getBasicLengthStats(self, sender=None):
        basicLengthStatsDf = self._getBasicLengthStats()
        if not sender:
            totalNum, totalLength, avgLegth = basicLengthStatsDf.loc['total'].tolist()
        else:
            totalNum, totalLength, avgLegth = basicLengthStatsDf.loc[sender].tolist()
        return totalNum, totalLength, avgLegth

    def getMessagesTotalLength(self):
        msgsLen = self.df['text'].apply(lambda x: len(x))
        totalLength = msgsLen.sum()
        return totalLength

    def generateDataFrameAgglomeratedStatsByHour(self):
        res = self._generateDataFrameAgglomeratedStatsBy('time', lambda x: str.split(x, ':')[0], 'hour')
        return res

    def generateDataFrameAgglomeratedStatsByMonth(self):
        res = self._generateDataFrameAgglomeratedStatsBy('date', lambda x: str.split(x, '.')[1], 'month')
        return res

    def generateDataFrameAgglomeratedStatsByYearAndMonth(self):
        self.df['len'] = self.df['text'].apply(lambda x: len(x))
        self.df['year'] = self.df['date'].apply(lambda x: str.split(x, '.')[0])
        self.df['month'] = self.df['date'].apply(lambda x: str.split(x, '.')[1])
        res = self.df.groupby(['sender', 'year', 'month'], as_index=False).agg({'text' : 'count',
                                                       'len' : 'sum'})
        print(res.head(10))
        tot = res.groupby(['year', 'month'], as_index=False).sum()
        tot['sender'] = "total"
        res = pd.concat([res, tot])
        res['avg'] = res['len']/res['text']
        return res

    def _generateDataFrameAgglomeratedStatsBy(self, colName, mFun, aggName):
        self.df['len'] = self.df['text'].apply(lambda x: len(x))
        self.df[aggName] = self.df[colName].apply(mFun)
        res = self.df.groupby(['sender', aggName], as_index=False).agg({'text' : 'count',
                                                       'len' : 'sum'})
        print(res.head(10))
        tot = res.groupby([aggName], as_index=False).sum()
        tot['sender'] = "total"
        res = pd.concat([res, tot])
        res['avg'] = res['len']/res['text']
        print(res.head(10))
        return res

        # if not agglomeratedMessages:
        #     agglomeratedMessages = self._getMessagesBy(mFun, self.conversation.messages)
        #
        # tot = []
        # tuples = []
        # for k, a in agglomeratedMessages.items():
        #     tot.append(list(self.getBasicLengthStats(self.conversation.sender1)))
        #     tot.append(list(self.getBasicLengthStats(self.conversation.sender2)))
        #     tuples.append((k, self.conversation.sender1))
        #     tuples.append((k, self.conversation.sender2))
        #
        # print(tot)
        # index = pd.MultiIndex.from_tuples(tuples, names=['hours', 'sender'])
        # df = pd.DataFrame(tot, index=index, columns=["numMsgs", "lenMsgs", "avgMsgs"])
        # stacked = df.stack()
        # df.columns = df.columns.get_level_values(0)
        # print(df)
        #
        # return df