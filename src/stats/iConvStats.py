from abc import ABCMeta, abstractmethod


class IConvStats(metaclass=ABCMeta):
    STATS_NAME_BASICLENGTH = 'basicLengthStats'
    STATS_NAME_LEXICAL = 'lexicalStats'
    STATS_NAME_WORDCOUNT = 'wordCountStats'
    STATS_NAME_EMOTICONCOUNT = 'emoticonCountStats'
    STATS_NAME_EMOTICONS = 'emoticonsStats'
    STATS_NAME_DELAY = 'delayStats'

    def __init__(self, conversation):
        self.conversation = conversation

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

    def generateStatsByYearMonthDayHour(self, statsType, **kwargs):
        return self._generateStats(statsType, ['year', 'month', 'day', 'hour'], **kwargs)

    def _generateStats(self, statsType, groupByColumns=None, **kwargs):
        if groupByColumns is None: groupByColumns = []
        if statsType == IConvStats.STATS_NAME_BASICLENGTH:
            res = self._generateBasicLengthStatsBy(groupByColumns)
        elif statsType == IConvStats.STATS_NAME_LEXICAL:
            res = self._generateLexicalStatsBy(groupByColumns)
        elif statsType == IConvStats.STATS_NAME_WORDCOUNT:
            res = self._generateWordCountStatsBy(groupByColumns, **kwargs)
        elif statsType == IConvStats.STATS_NAME_EMOTICONS:
            res = self._generateEmoticonsStatsBy(groupByColumns)
        elif statsType == IConvStats.STATS_NAME_EMOTICONCOUNT:
            res = self._generateEmoticonCountStatsBy(groupByColumns, **kwargs)
        elif statsType == IConvStats.STATS_NAME_DELAY:
            res = self._generateDelayStats()
        else:
            raise Exception(statsType + ' Stat not implemented')
        return res

    @abstractmethod
    def getBasicLengthStats(self, sender=None):
        pass

    @abstractmethod
    def getEmoticonsStats(self):
        pass

    @abstractmethod
    def getLexicalStats(self, sender=None):
        pass

    def getIntervalStats(self):
        start, end, interval = self._getIntervalStatsFor()
        return start, end, interval

    def getDaysWithoutMessages(self):
        days = self._getDaysWithoutMessages()
        return days