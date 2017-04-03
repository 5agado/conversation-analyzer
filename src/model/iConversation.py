import os
from abc import ABCMeta, abstractmethod


class IConversation(metaclass=ABCMeta):
    def __init__(self, filepath):
        self.filepath = filepath
        self.messages = None
        self.senders = None
        self.stats = None

    @abstractmethod
    def loadMessages(self, limit=0, startDate=None, endDate=None):
        pass