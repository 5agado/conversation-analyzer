import collections
import math

import numpy as np
import pandas as pd

from model.message import Message
from stats.iConvStats import IConvStats
from util import statsUtil


class ConvStatsDataframe(IConvStats):
    def __init__(self, conversation):
        super().__init__(conversation)
        self.df = self.conversation.messages

    def getMessagesTotalLength(self):
        msgsLen = self.df['text'].apply(lambda x: len(x))
        totalLength = msgsLen.sum()
        return totalLength

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
        fun = lambda x: tuple(sorted(
            statsUtil.getWordsCount(" ".join(x)).items(), key=lambda y: y[1], reverse=True))
        label = 'wordCount'
        countId = 'word'
        results = self._generateCountStatsBy(fun, label, countId, groupByColumns, word)
        return results

    def _generateEmoticonCountStatsBy(self, groupByColumns=[], emoticon=None):
        fun = lambda x: tuple(sorted(
            statsUtil.getEmoticonsCount(" ".join(x)).items(), key=lambda y: y[1], reverse=True))
        label = 'emoticonCount'
        countId = 'emoticon'
        results = self._generateCountStatsBy(fun, label, countId, groupByColumns, emoticon)
        return results

    def _generateBigramCountStatsBy(self, groupByColumns=[], bigram=None):
        fun = lambda x: sorted(statsUtil.getBigramsCount(" ".join(x)).items(), key=lambda y: y[1], reverse=True)
        label = 'bigramCount'
        countId = 'bigram'
        results = self._generateCountStatsBy(fun, label, countId, groupByColumns, bigram).sort_values("tf-isf", ascending=False)
        return results

    def _generateTrigramCountStatsBy(self, groupByColumns=[], trigram=None):
        fun = lambda x: sorted(statsUtil.getTrigramsCount(" ".join(x)).items(), key=lambda y: y[1], reverse=True)
        label = 'trigramCount'
        countId = 'trigram'
        results = self._generateCountStatsBy(fun, label, countId, groupByColumns, trigram).sort_values("tf-isf", ascending=False)
        return results

    def _generateCountStatsBy(self, aggFun, label, countId, groupByColumns=[], token=None):
        res = self.df.rename(columns={'text':label})
        res = res.groupby(['sender'] + groupByColumns, as_index=False).agg({label : aggFun})
        grouped = res.groupby(['sender'] + groupByColumns, as_index=False)
        groupDfs = []
        for name, group in grouped:
            count = group[label].values[0]

            #name is a tuple
            if groupByColumns:
                groupData = [[x[0], x[1]] + [n for n in name] for x in count if (not token or x[0]==token)]
            #name is a single value
            else:
                groupData = [[x[0], x[1], name] for x in count if (not token or x[0]==token)]
            df = pd.DataFrame(groupData, columns=[countId, 'count', 'sender']+groupByColumns)
            groupDfs.append(df)

        results = pd.concat(groupDfs)
        results['total'] = results['count']
        results['usageCount'] = results['sender']
        tmp = results.groupby([countId]+groupByColumns, as_index=True).agg({'total' : 'sum',
                                                                           'usageCount' : lambda x : x.nunique()})
        results.set_index([countId]+groupByColumns, inplace=True)
        results['total'] = tmp['total']
        results['usageCount'] = tmp['usageCount']
        results['frequency'] = results['count']/results['total']
        results['inverseSenderFrequency'] = (results['sender'].nunique()/results['usageCount']).apply(math.log)
        results['tf-isf'] = results['frequency']*results['inverseSenderFrequency']
        #results.set_index([countId, 'sender']+groupByColumns, inplace=True)
        results.drop('usageCount', axis=1, inplace=True)
        return results

    #TODO need to optimize performances
    def _generateLexicalStatsBy(self, groupByColumns=[]):
        res = self.df.rename(columns={'text':'text'})
        #enough, probably the best is to make another simpler method in statsUtil
        res = res.groupby(['sender'] + groupByColumns, as_index=False).agg(
            {'text' : lambda x: tuple(statsUtil.getWords(" ".join(x)))})
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
        #grouped = res.groupby(['sender'] + groupByColumns, as_index=False)
        res = res.groupby(['sender'] + groupByColumns, as_index=False).agg({'text' : lambda x: " ".join(x)})
        res['lenMsgs'] = res['text'].apply(lambda x: len(x))
        res['numEmoticons'] = res['text'].apply(lambda x: len(statsUtil.getEmoticonsFromText(x)))

        res.drop('text', axis=1, inplace=True)
        if groupByColumns:
            tot = res.groupby(groupByColumns, as_index=False).sum()
            tot['sender'] = "total"
            res = pd.concat([res, tot])
            res['emoticonsRatio'] = res['numEmoticons']/res['lenMsgs']
            return res[['numEmoticons', 'emoticonsRatio', 'lenMsgs']]
        else:
            res.set_index(['sender'], inplace=True)
            res.loc['total'] = res.sum()
            res['emoticonsRatio'] = res['numEmoticons']/res['lenMsgs']
            return res[['numEmoticons', 'emoticonsRatio', 'lenMsgs']]

    #TODO add delay threshold, do not sum too big delays
    def _generateDelayStats(self):
        """Calculates the delays between the messages of the conversation.
        senderDelay consider the time that passed between a sender message and the successive reply
        from another sender. The result value is the sum of such time for each message.
        Notice that if the same sender sends many message, only the last one (before another sender message)
        is taken into consideration"""

        def computeDelay(messages):
            data = messages[['datetime', 'sender']]
            delay = np.insert(data['datetime'].iloc[1:].values -data['datetime'].iloc[:-1].values, 0, 0)
            data['delay'] = delay
            return data

        #sender of current message must be different from sender previous message
        def removeConsecutiveMessages(messages):
            return messages[messages['sender'] != messages['sender'].shift()]

        res = removeConsecutiveMessages(computeDelay(self.df))
        res = res.groupby('sender').sum()
        return res

    def _getIntervalStatsFor(self):
        startDatetime = self.df.iloc[0]['datetime']
        endDatetime = self.df.iloc[-1]['datetime']
        interval = self.df.iloc[-1]['datetime'] - self.df.iloc[0]['datetime']

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
        if not sender:
            tokensCount, vocabularyCount, lexicalRichness = lexicalStatsDf.loc['total'].tolist()
        else:
            tokensCount, vocabularyCount, lexicalRichness = lexicalStatsDf.loc[sender].tolist()
        return tokensCount, vocabularyCount, lexicalRichness

    def getWordCountStats(self, sender=None, limit=0, word=None):
        wordsCountStatsDf = self.generateStats(IConvStats.STATS_NAME_WORDCOUNT, word=word)
        if sender:
            wCount = wordsCountStatsDf[wordsCountStatsDf['sender']==sender]
        else:
            wCount = pd.DataFrame(wordsCountStatsDf['total']).drop_duplicates(keep='last')
        if word:
            val = wCount['count' if sender else 'total'].values
            return 0 if not val else val[0]
        else:
            if limit != 0:
                return [(w, row[0]) for w, row in wCount.iterrows()][:limit]
            else:
                return [(w, row[0]) for w, row in wCount.iterrows()]
        return  wCount

    def getEmoticonsStats(self, sender=None):
        emoticonStatsDf = self.generateStats(IConvStats.STATS_NAME_EMOTICONS)
        if not sender:
            numEmoticons, emoticonsRatio, lenMsgs = emoticonStatsDf.loc['total'].tolist()
        else:
            numEmoticons, emoticonsRatio, lenMsgs = emoticonStatsDf.loc[sender].tolist()
        return  numEmoticons, emoticonsRatio, lenMsgs

    def getWordsBySender(self, limit=0, usedJustBy=False):
        df = self.generateStats(IConvStats.STATS_NAME_WORDCOUNT)
        df = df.reset_index()
        grouped = df.groupby(['sender'])
        words = collections.defaultdict(list)

        for sender, group in grouped:
            group = group.sort_values("tf-isf", ascending=False)
            if usedJustBy:
                #Select words said by sender, but not by the others.
                #For such case, sender count should be equal to total count
                words[sender] = set(group[
                                        (group['sender']==sender) & (group['count']==group['total'])
                                    ]['word'].values)
            else:
                words[sender] = [tuple(x) for x in group[group['sender']==sender][['word','tf-isf']].values]

        return words

    def getIntervalStats(self):
        start, end, interval = self._getIntervalStatsFor()
        return start, end, interval

    def getDaysWithoutMessages(self):
        days = self._getDaysWithoutMessages()
        return days