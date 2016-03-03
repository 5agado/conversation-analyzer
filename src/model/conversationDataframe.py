import logging
import time

import pandas as pd

import util.io as mio
from model.iConversation import IConversation
from model.message import Message
from stats.convStatsDataframe import ConvStatsDataframe


class ConversationDataframe(IConversation):
    def __init__(self, filepath):
        super().__init__(filepath)

    def loadMessages(self, limit=0, startDate=None, endDate=None):
        logging.info("Start loading messages for conversation " + self.filepath)
        start = time.time()

        messages, self.senders = \
            mio.parseMessagesFromFile(self.filepath, limit, startDate, endDate)
        if len(messages) == 0:
            raise Exception("No messages found for conversation " + self.filepath)

        #TODO load directly with pandas
        #dateparse = lambda x: pd.datetime.strptime(x, Message.DATE_TIME_FORMAT)
        #self.messages = pd.read_csv(self.filepath, parse_dates=[0], date_parser=dateparse)
        self.messages = ConversationDataframe._getMessagesAsDataframe(messages)

        end = time.time()
        logging.info("Loading completed in {0:.2f}s".format(end-start))

        self.stats = ConvStatsDataframe(self)

    @staticmethod
    def _getMessagesAsDataframe(messages):
        msgs = []
        for msg in messages:
            year, month, day = str.split(msg.date, Message.DATE_SEPARATOR)
            hour = str.split(msg.time, Message.TIME_SEPARATOR)[0]
            msgs.append([year, month, day, msg.date, hour, msg.time, msg.datetime, msg.sender, msg.text])
        df = pd.DataFrame(msgs, columns=['year', 'month', 'day', 'date', 'hour', 'time', 'datetime', 'sender', 'text'])
        df['datetime'] = pd.to_datetime(df.datetime, format=Message.DATE_TIME_FORMAT)
        return df