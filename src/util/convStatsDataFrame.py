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

        msgs = []
        for msg in self.conversation.messages:
            year, month, day = str.split(msg.date, '.')
            hour = str.split(msg.time, ':')[0]
            msgs.append([year, month, day, msg.date, hour, msg.time, msg.sender, msg.text])
        df = pd.DataFrame(msgs, columns=['year', 'month', 'day', 'date', 'hour', 'time', 'sender', 'text'])
        return df

    def getMessagesTotalLength(self):
        msgsLen = self.df['text'].apply(lambda x: len(x))
        totalLength = msgsLen.sum()
        return totalLength

    def generateAgglomeratedStatsOverall(self, statsType):
        return self._generateAgglomeratedStats(statsType)

    def generateAgglomeratedStatsByHour(self, statsType):
        return self._generateAgglomeratedStats(statsType, ['hour'])

    def generateAgglomeratedStatsByMonth(self, statsType):
        return self._generateAgglomeratedStats(statsType, ['month'])

    def generateAgglomeratedStatsByYearAndMonth(self, statsType):
        return self._generateAgglomeratedStats(statsType, ['year', 'month'])

    def generateAgglomeratedStatsByYearMonthDay(self, statsType):
        return self._generateAgglomeratedStats(statsType, ['year', 'month', 'day'])

    def _generateAgglomeratedStats(self, statsType, groupByColumns=[]):
        if statsType == IConvStats.STATS_NAME_BASICLENGTH:
            res = self._generateBasicLengthAgglomeratedStatsBy(groupByColumns)
        if statsType == IConvStats.STATS_NAME_LEXICAL:
            res = self._generateLexicalAgglomeratedStatsBy(groupByColumns)
        if statsType == IConvStats.STATS_NAME_WORDCOUNT:
            res = self._generateWordCountStatsBy(groupByColumns)
        return res

    def _generateLexicalAgglomeratedStatsBy(self, groupByColumns=[]):
        res = self.df.rename(columns={'text':'text'})
        #TODO make it quicker. No need to clean words or check emoticons, lower case should be
        #enough, probably the best is to make another simpler method in statsUtil
        res = res.groupby(['sender'] + groupByColumns, as_index=False).agg({'text' : lambda x: statsUtil.getWords(" ".join(x))})
        res['tokensCount'] = res['text'].apply(lambda x: len(x))
        res['vocabularyCount'] = res['text'].apply(lambda x: len(set(x)))

        res.drop('text', axis=1, inplace=True)

        if groupByColumns:
            tot = res.groupby(groupByColumns, as_index=False).sum()
            tot['sender'] = "total"
            res = pd.concat([res, tot])
            #TODO Missing tokencount = zero case
            res['lexicalRichness'] = res['vocabularyCount']/res['tokensCount']
            return res
        else:
            res.set_index(['sender'], inplace=True)
            res.loc['total'] = res.sum()
            res['lexicalRichness'] = res['vocabularyCount']/res['tokensCount']
            return res[['tokensCount', 'vocabularyCount', 'lexicalRichness']]

    def _generateEmoticonsStatsBy(self, groupByColumns=[]):
        res = self.df.rename(columns={'text':'text'})
        grouped = res.groupby(['sender'] + groupByColumns, as_index=False)
        res['numEmoticons'] = grouped['text'].apply(lambda x: len(x))
        res['lenMsgs'] = grouped['text'].apply(lambda x: statsUtil.getEmoticonsFromText(x))

        res.drop('text', axis=1, inplace=True)

        if groupByColumns:
            tot = res.groupby(groupByColumns, as_index=False).sum()
            tot['sender'] = "total"
            res = pd.concat([res, tot])
            res['emoticonsRatio'] = res['numEmoticons']/res['lenMsgs']
            return res
        else:
            res.set_index(['sender'], inplace=True)
            res.loc['total'] = res.sum()
            res['emoticonsRatio'] = res['numEmoticons']/res['lenMsgs']
            return res

    def _generateBasicLengthAgglomeratedStatsBy(self, groupByColumns=[]):
        res = self.df.rename(columns={'text':'numMsgs'})
        res['lenMsgs'] = res['numMsgs'].apply(lambda x: len(x))
        res = res.groupby(['sender'] + groupByColumns, as_index=False).agg({'numMsgs' : 'count',
                                                       'lenMsgs' : 'sum'})
        print(res)
        if groupByColumns:
            tot = res.groupby(groupByColumns, as_index=False).sum()
            tot['sender'] = "total"
            res = pd.concat([res, tot])
            res['avgLen'] = res['lenMsgs']/res['numMsgs']
            return res
        else:
            res.set_index(['sender'], inplace=True)
            res.loc['total'] = res.sum()
            res['avgLen'] = res['lenMsgs']/res['numMsgs']
            return res[['numMsgs', 'lenMsgs', 'avgLen']]

    def _generateWordCountStatsBy(self, groupByColumns=[]):
        fun = lambda x: ConvStatsDataFrame.getWordsCount(" ".join(x))
        res = self.df.rename(columns={'text':'wordCount'})

        res = res.groupby(['sender'] + groupByColumns, as_index=False).agg({'wordCount' : fun})

        #tot = res.groupby(groupByColumns, as_index=False).sum()
        #tot['sender'] = "total"
        #res = pd.concat([res, tot])
        return res

    def generateSingleWordCountBy(self, word, groupByColumns=[]):
        res = self._generateWordCountStatsBy(groupByColumns)
        res['wordCount'].apply(lambda x: x[word])

        tot = res.groupby(groupByColumns, as_index=False).sum()
        tot['sender'] = "total"
        res = pd.concat([res, tot])
        return res

    @staticmethod
    def getWordsCount(text):
        wordsCount = collections.Counter(statsUtil.getWords(text))
        return wordsCount

    def generateDataFrameAgglomeratedStatsByHour(self):
        self.generateAgglomeratedStatsByHour(IConvStats.STATS_NAME_BASICLENGTH)

    def getBasicLengthStats(self, sender=None):
        basicLengthStatsDf = self.generateAgglomeratedStatsOverall(IConvStats.STATS_NAME_BASICLENGTH)
        print(basicLengthStatsDf)
        if not sender:
            totalNum, totalLength, avgLegth = basicLengthStatsDf.loc['total'].tolist()
        else:
            totalNum, totalLength, avgLegth = basicLengthStatsDf.loc[sender].tolist()
        return totalNum, totalLength, avgLegth

    def getLexicalStats(self, sender=None):
        lexicalStatsDf = self.generateAgglomeratedStatsOverall(IConvStats.STATS_NAME_LEXICAL)
        if not sender:
            tokensCount, vocabularyCount, lexicalRichness = lexicalStatsDf.loc['total'].tolist()
        else:
            tokensCount, vocabularyCount, lexicalRichness = lexicalStatsDf.loc[sender].tolist()
        return tokensCount, vocabularyCount, lexicalRichness