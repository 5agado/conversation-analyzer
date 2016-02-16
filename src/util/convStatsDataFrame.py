from util.iConvStats import IConvStats
import pandas as pd
import collections
import numpy as np
from model.message import Message
from datetime import datetime, timedelta
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

    def generateAgglomeratedStatsOverall(self, statsType, **kwargs):
        return self._generateAgglomeratedStats(statsType, **kwargs)

    def generateAgglomeratedStatsByHour(self, statsType, **kwargs):
        return self._generateAgglomeratedStats(statsType, ['hour'], **kwargs)

    def generateAgglomeratedStatsByMonth(self, statsType, **kwargs):
        return self._generateAgglomeratedStats(statsType, ['month'], **kwargs)

    def generateAgglomeratedStatsByYearAndMonth(self, statsType, **kwargs):
        return self._generateAgglomeratedStats(statsType, ['year', 'month'], **kwargs)

    def generateAgglomeratedStatsByYearMonthDay(self, statsType, **kwargs):
        return self._generateAgglomeratedStats(statsType, ['year', 'month', 'day'], **kwargs)

    def _generateAgglomeratedStats(self, statsType, groupByColumns=[], **kwargs):
        if statsType == IConvStats.STATS_NAME_BASICLENGTH:
            res = self._generateBasicLengthAgglomeratedStatsBy(groupByColumns)
        if statsType == IConvStats.STATS_NAME_LEXICAL:
            res = self._generateLexicalAgglomeratedStatsBy(groupByColumns)
        if statsType == IConvStats.STATS_NAME_WORDCOUNT:
            res = self._generateWordCountStatsBy(groupByColumns, **kwargs)
        return res

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

    def _generateWordCountStatsBy(self, groupByColumns=[], word=None):
        if word:
            fun = lambda x: ConvStatsDataFrame.getWordsCount(" ".join(x))[word]
        else:
            fun = lambda x: sorted(ConvStatsDataFrame.getWordsCount(" ".join(x)).items(), key=lambda y: y[1], reverse=True)
        res = self.df.rename(columns={'text':'wordCount'})
        res['total'] = 'total'
        tot = res.groupby(['total'] + groupByColumns, as_index=False).agg({'wordCount' : fun})
        tot = tot.rename(columns = {'total':'sender'})
        res = res.groupby(['sender'] + groupByColumns, as_index=False).agg({'wordCount' : fun})

        if groupByColumns:
            res = pd.concat([res, tot])
            return res
        else:
            res = pd.concat([res, tot])
            res.set_index(['sender'], inplace=True)
            #res.loc['total'] = res.sum()
            return res

    #TODO just reuse wordCount df
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

    @staticmethod
    def getWordsCount(text):
        wordsCount = collections.Counter(statsUtil.getWords(text))
        return wordsCount

    def generateDataFrameAgglomeratedStatsByHour(self):
        self.generateAgglomeratedStatsByHour(IConvStats.STATS_NAME_BASICLENGTH)

    def getWordCountStats(self, limit=0, word=None):
        def extractWordCount(df, sender, limit):
            wCount = df.loc[sender]['wordCount']
            if limit == 0 or np.isscalar(wCount):
                return wCount
            else:
                return wCount[:limit]

        if word:
            wordsCountStatsDf = self.generateAgglomeratedStatsOverall(IConvStats.STATS_NAME_WORDCOUNT, word=word)
        else:
            wordsCountStatsDf = self.generateAgglomeratedStatsOverall(IConvStats.STATS_NAME_WORDCOUNT)

        wCountS1 = extractWordCount(wordsCountStatsDf, self.conversation.sender1, limit)
        wCountS2 = extractWordCount(wordsCountStatsDf, self.conversation.sender2, limit)
        wCount = extractWordCount(wordsCountStatsDf, 'total', limit)

        return wCount, wCountS1, wCountS2

    def getBasicLengthStats(self, sender=None):
        basicLengthStatsDf = self.generateAgglomeratedStatsOverall(IConvStats.STATS_NAME_BASICLENGTH)
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

    def getEmoticonsStats(self, sender=None):
        emoticonStatsDf = self.generateAgglomeratedStatsOverall(IConvStats.STATS_NAME_EMOTICONS)
        if not sender:
            numEmoticons, emoticonsRatio, lenMsgs = emoticonStatsDf.loc['total'].tolist()
        else:
            numEmoticons, emoticonsRatio, lenMsgs = emoticonStatsDf.loc[sender].tolist()
        return  numEmoticons, emoticonsRatio, lenMsgs

    def getIntervalStats(self):
        start, end, interval = self._getIntervalStatsFor()
        return start, end, interval

    @staticmethod
    def _getIntervalStatsFor(self):
        startDatetime = ' '.join(self.df.iloc[0][['date','time']].values)
        endDatetime = ' '.join(self.df.iloc[-1][['date','time']].values)
        start = datetime.strptime(startDatetime, Message.DATE_TIME_FORMAT)
        end = datetime.strptime(endDatetime, Message.DATE_TIME_FORMAT)
        interval = end - start

        return startDatetime, endDatetime, interval

    def getDaysWithoutMessages(self):
        days = self._getDaysWithoutMessages()
        return days

    def _getDaysWithoutMessages(self):
        """Generate a date-range between the date of the first and last message
        and returns those dates for which there is no corresponding message in messages"""
        daysWithMsgs = self.df['date'].drop_duplicates()

        datelist = pd.Series(pd.date_range(self.df.iloc[0]['date'], self.df.iloc[-1]['date']))
        datelist = datelist.apply(lambda x:x.date().strftime(Message.DATE_FORMAT))
        # data.index = pd.DatetimeIndex(data.index)
        # data = data.reindex(datelist, fill_value=0)

        daysWithoutMsgs = np.setdiff1d(datelist, daysWithMsgs)
        return daysWithoutMsgs

    def getWordsMentioningStats(self):
        wordsSaidByBoth, wordsSaidJustByS1, wordsSaidJustByS2 = \
            self._getWordsMentioningStats()
        return wordsSaidByBoth, wordsSaidJustByS1, wordsSaidJustByS2

    def _getWordsMentioningStats(self):
        df = self._getWordFrequency()

        wordsSaidJustByS1 = df[df[self.conversation.sender2]==0].index.values
        wordsSaidJustByS2 = df[df[self.conversation.sender1]==0].index.values

        return wordsSaidJustByS1, wordsSaidJustByS2

    def _getWordFrequency(self):
        wCount, wCountS1, wCountS2 = self.getWordCountStats()
        print(wCount)
        print(wCountS1)
        print(wCountS2)

        wCount = dict(wCount)
        wCountS1 = dict(wCountS1)
        wCountS2 = dict(wCountS2)
        df = pd.DataFrame(index=[x[0] for x in wCount.items()],
                          columns=[self.conversation.sender1, self.conversation.sender2, 'total'])
        for word, totalCount in wCount.items():
            s1Count = 0 if (word not in wCountS1) else wCountS1[word]
            s2Count = 0 if (word not in wCountS2) else wCountS2[word]
            df.loc[word] = [s1Count, s2Count, totalCount]

        df[self.conversation.sender1 + '_ratio'] = df[self.conversation.sender1]/df['total']
        df[self.conversation.sender2 + '_ratio'] = df[self.conversation.sender2]/df['total']
        return df
