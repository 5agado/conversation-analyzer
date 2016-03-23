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

    @abstractmethod
    def getBasicLengthStats(self, sender=None):
        pass

    @abstractmethod
    def getEmoticonsStats(self):
        pass

    @abstractmethod
    def getLexicalStats(self, sender=None):
        pass

    @abstractmethod
    def getIntervalStats(self):
        pass

    @abstractmethod
    def getDaysWithoutMessages(self):
        pass