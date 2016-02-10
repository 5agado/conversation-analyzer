from model.message import Message
from util import io as mio
from datetime import datetime
from datetime import timedelta
from random import randrange
import random

def generateNewConversation(numMsgs, startDate, endDate, senders):
    words = ["hello", "nice", "bad", "baloon", "jojo"]

    messages = []
    start = datetime.strptime(startDate, Message.DATE_TIME_FORMAT)
    end = datetime.strptime(endDate, Message.DATE_TIME_FORMAT)
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    for _ in range(numMsgs):
        randTime = start + timedelta(seconds=randrange(int_delta))
        date = datetime.strftime(randTime, Message.DATE_FORMAT)
        time = datetime.strftime(randTime, Message.TIME_FORMAT)
        sender = random.choice(senders)
        text = ' '.join([random.choice(words) for _ in range(random.randint(1, 20))])
        messages.append(Message(date, time, sender, text))
    messages.sort(key=lambda x: x.datetime)
    return messages

def generateAndSaveNewConversation(filepath):
    conversation = generateNewConversation()
    mio.printListToFile(conversation, filepath)


