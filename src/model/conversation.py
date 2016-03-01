import logging
import os
import time

import nltk

import util.io as mio
from stats.convStats import ConvStats

#----------------------------#
#         DEPRECATED         #
#----------------------------#
class Conversation:
    def __init__(self, filepath):
        self.sender1 = None
        self.sender2 = None
        self.filepath = filepath
        self.statsFolder = os.path.dirname(filepath) + '\\stats'
        if not os.path.exists(self.statsFolder):
            os.makedirs(self.statsFolder)
        self.messages = None
        self.sender1Messages = None
        self.sender2Messages = None
        self.messagesBySender = {self.sender1:self.sender1Messages, self.sender2:self.sender2Messages}
        self.stats = None

    def loadMessages(self, limit=0, startDate=None, endDate=None):
        logging.info("Start loading messages for conversation " + self.filepath)
        start = time.time()

        self.messages, [self.sender1, self.sender2] = \
            mio.parseMessagesFromFile(self.filepath, limit, startDate, endDate)
        if len(self.messages) == 0:
            raise Exception("No messages found for conversation " + self.filepath)
        self.sender1Messages = list(filter(lambda m: m.sender == self.sender1, self.messages))
        self.sender2Messages = list(filter(lambda m: m.sender == self.sender2, self.messages))
        self.messagesBySender[self.sender1] = self.sender1Messages
        self.messagesBySender[self.sender2] = self.sender2Messages

        end = time.time()
        logging.info("Loading completed in {0:.2f}s".format(end-start))

        self.stats = ConvStats

    def getAsNLTKText(self, sender=None):
        if sender:
            return nltk.Text(self.getConvTextBySender(sender))
        else:
            return nltk.Text(self.getEntireConvText())

    def getEntireConvText(self):
        text = ''
        for m in self.messages:
            text += m.text + '\n'
        return text

    def getConvTextBySender(self, sender):
        text = ''
        for m in self.messages:
            if m.sender == sender:
                text += m.text + '\n'
        return text