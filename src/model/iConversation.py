import os
from abc import ABCMeta, abstractmethod


class IConversation(metaclass=ABCMeta):
    def __init__(self, filepath):
        self.filepath = filepath
        self.statsFolder = os.path.dirname(filepath) + '\\stats'
        if not os.path.exists(self.statsFolder):
            os.makedirs(self.statsFolder)
        self.messages = None
        self.senders = None
        self.stats = None

    @abstractmethod
    def loadMessages(self, limit=0, startDate=None, endDate=None):
        pass