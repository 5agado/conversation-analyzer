from util.iConvStats import IConvStats
import pandas as pd
import numpy as np
from model.message import Message
from datetime import datetime, timedelta
from util import statsUtil

class ConvStatsDataFrame(IConvStats):
    def __init__(self, conversation):
        super().__init__(conversation)
        self.df = self._getConversationAsDataframe()

    def _getConversationAsDataframe(self):
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

    def generateStats(self, statsType, **kwargs):
        return self._generateStats(statsType, **kwargs)

    def generateStatsByHour(self, statsType, **kwargs):
        return self._generateStats(statsType, ['hour'], **kwargs)

    def generateStatsByYearAndHour(self, statsType, **kwargs):
        return self._generateStats(statsType, ['year', 'hour'], **kwargs)

    def generateStatsByMonth(self, statsType, **kwargs):
        return self._generateStats(statsType, ['month'], **kwargs)

    def generateStatsByYearAndMonth(self, statsType, **kwargs):
        return self._generateStats(statsType, ['year', 'month'], **kwargs)

    def generateStatsByYearMonthDay(self, statsType, **kwargs):
        return self._generateStats(statsType, ['year', 'month', 'day'], **kwargs)

    def generateStatsByYearMonthHour(self, statsType, **kwargs):
        return self._generateStats(statsType, ['year', 'month', 'hour'], **kwargs)

    def _generateStats(self, statsType, groupByColumns=[], **kwargs):
        if statsType == IConvStats.STATS_NAME_BASICLENGTH:
            res = self._generateBasicLengthStatsBy(groupByColumns)
        if statsType == IConvStats.STATS_NAME_LEXICAL:
            res = self._generateLexicalStatsBy(groupByColumns)
        if statsType == IConvStats.STATS_NAME_WORDCOUNT:
            res = self._generateWordCountStatsBy(groupByColumns, **kwargs)
        return res

    def _generateBasicLengthStatsBy(self, groupByColumns=[]):
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

    #TODO consider option of having 0 if the word does not appear for a specific sender
    def _generateWordCountStatsBy(self, groupByColumns=[], word=None):
        fun = lambda x: sorted(statsUtil.getWordsCount(" ".join(x)).items(), key=lambda y: y[1], reverse=True)
        res = self.df.rename(columns={'text':'wordCount'})
        res = res.groupby(['sender'] + groupByColumns, as_index=False).agg({'wordCount' : fun})
        grouped = res.groupby(['sender'] + groupByColumns, as_index=False)
        groupDfs = []
        for name, group in grouped:
            wordCount = group['wordCount'].values[0]

            #name is a tuple
            if groupByColumns:
                groupData = [[x[0], x[1]] + [n for n in name] for x in wordCount if (not word or x[0]==word)]
            #name is a single value
            else:
                groupData = [[x[0], x[1], name] for x in wordCount if (not word or x[0]==word)]
            df = pd.DataFrame(groupData, columns=['word', 'count', 'sender']+groupByColumns)
            groupDfs.append(df)

        results = pd.concat(groupDfs)
        results['total'] = results['count']
        tmp = results.groupby(['word']+groupByColumns, as_index=True).agg({'total' : 'sum'})
        results.set_index(['word']+groupByColumns, inplace=True)
        results['total'] = tmp['total']
        results['frequency'] = results['count']/results['total']
        #results.set_index(['word', 'sender']+groupByColumns, inplace=True)
        return results

    #TODO ??option of just reuse wordCount df ??
    def _generateLexicalStatsBy(self, groupByColumns=[]):
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

    @staticmethod
    def _getIntervalStatsFor(self):
        startDatetime = ' '.join(self.df.iloc[0][['date','time']].values)
        endDatetime = ' '.join(self.df.iloc[-1][['date','time']].values)
        start = datetime.strptime(startDatetime, Message.DATE_TIME_FORMAT)
        end = datetime.strptime(endDatetime, Message.DATE_TIME_FORMAT)
        interval = end - start

        return startDatetime, endDatetime, interval

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

    #----------------------------#
    # CONVERSATION OVERALL STATS #
    #----------------------------#
    #Extract and return single values from more generic methods
    #(mostly from dataframe generated for the entire conversation)

    def getBasicLengthStats(self, sender=None):
        basicLengthStatsDf = self.generateStats(IConvStats.STATS_NAME_BASICLENGTH)
        if not sender:
            totalNum, totalLength, avgLegth = basicLengthStatsDf.loc['total'].tolist()
        else:
            totalNum, totalLength, avgLegth = basicLengthStatsDf.loc[sender].tolist()
        return totalNum, totalLength, avgLegth

    def getLexicalStats(self, sender=None):
        lexicalStatsDf = self.generateStats(IConvStats.STATS_NAME_LEXICAL)
        print(lexicalStatsDf)
        if not sender:
            tokensCount, vocabularyCount, lexicalRichness = lexicalStatsDf.loc['total'].tolist()
        else:
            tokensCount, vocabularyCount, lexicalRichness = lexicalStatsDf.loc[sender].tolist()
        return tokensCount, vocabularyCount, lexicalRichness

    def getWordCountStats(self, limit=0, word=None):
        def extractWordCount(df, sender, limit):
            wCount = df[df['sender']==sender]
            #print(wCount)
            if word:
                val = wCount['count'].values
                return 0 if not val else val[0]
            else:
                if limit != 0:
                    return [(w, row[0]) for w, row in wCount.iterrows()][:limit]
                else:
                    return [(w, row[0]) for w, row in wCount.iterrows()]

        if word:
            wordsCountStatsDf = self.generateStats(IConvStats.STATS_NAME_WORDCOUNT, word=word)
        else:
            wordsCountStatsDf = self.generateStats(IConvStats.STATS_NAME_WORDCOUNT)
        wCountS1 = extractWordCount(wordsCountStatsDf, self.conversation.sender1, limit)
        wCountS2 = extractWordCount(wordsCountStatsDf, self.conversation.sender2, limit)
        wCount = wCountS1 + wCountS2

        return wCount, wCountS1, wCountS2

    def getEmoticonsStats(self, sender=None):
        emoticonStatsDf = self.generateStats(IConvStats.STATS_NAME_EMOTICONS)
        if not sender:
            numEmoticons, emoticonsRatio, lenMsgs = emoticonStatsDf.loc['total'].tolist()
        else:
            numEmoticons, emoticonsRatio, lenMsgs = emoticonStatsDf.loc[sender].tolist()
        return  numEmoticons, emoticonsRatio, lenMsgs

    def getIntervalStats(self):
        start, end, interval = self._getIntervalStatsFor()
        return start, end, interval

    def getDaysWithoutMessages(self):
        days = self._getDaysWithoutMessages()
        return days

    #TODO rename
    def getWordsMentioningStats(self):
        df = self.generateStats(IConvStats.STATS_NAME_WORDCOUNT)
        df = df.reset_index()
        wordsSaidByBoth = set(df['word'].values)
        wordsSaidJustByS1 = set(df[df['sender']==self.conversation.sender2]['word'].values)
        wordsSaidJustByS2 = set(df[df['sender']==self.conversation.sender1]['word'].values)
        return wordsSaidByBoth, wordsSaidJustByS1, wordsSaidJustByS2
