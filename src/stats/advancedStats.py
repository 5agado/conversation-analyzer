import numpy as np
import pandas as pd

from model.message import Message
from stats.iConvStats import IConvStats
from util import statsUtil

class AdvancedStats:
    def __init__(self, conversation):
        self.conversation = conversation
        self.df = self.conversation.messages

    def getSentimentStats(self, sentimentExtractionFun):
        values = self.df.apply(sentimentExtractionFun, axis=1)
        names = values.columns.values
        sentimentStats = self.df.join(values)

        return sentimentStats, names