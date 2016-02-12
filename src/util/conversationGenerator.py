import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from model.message import Message
from util import io as mio
from datetime import datetime
from datetime import timedelta
from random import randrange
import random
import nltk
import logging
import argparse

#Need to download the gutenberg corpus via nltk.download()
def generateNewConversation(numMsgs, startDate, endDate, senders, minWords, maxWords):
    words = nltk.corpus.gutenberg.words(random.choice(nltk.corpus.gutenberg.fileids()))
    #text = nltk.corpus.gutenberg.raw(random.choice(nltk.corpus.gutenberg.fileids()))
    #print(words[:10])

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
        text = ' '.join([random.choice(words) for _ in range(random.randint(minWords, maxWords))])
        messages.append(Message(date, time, sender, text))
    messages.sort(key=lambda x: x.datetime)
    return messages

def main(_):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    parser = argparse.ArgumentParser(description='Conversation Generator')
    parser.add_argument('--out', metavar='conversationPath', dest='filepath', required=True)
    parser.add_argument('--size', metavar='numMessages', type=int, dest='numMsgs', required=True,
                        help="number of messages to generate for the conversation")
    parser.add_argument('--minWords', metavar='minWords', type=int, dest='minWords', default=1,
                        help="minimum number of words per message")
    parser.add_argument('--maxWords', metavar='maxWords', type=int, dest='maxWords', default=20,
                        help="maximum number of words per message")
    parser.add_argument('--startDate', metavar='startDate', dest='startDate', required=True,
                        help="earliest possible date for first generated message")
    parser.add_argument('--endDate', metavar='endDate', dest='endDate', required=True,
                        help="latest possible date of last generated message")
    parser.add_argument('--authors', metavar='authors', dest='authors', type=list,
                        default=["s1", "s2"],
                        help=""" list of senders' aliases""")

    args = parser.parse_args()
    filepath = args.filepath
    numMsgs = args.numMsgs
    startDate = args.startDate
    endDate = args.endDate
    minWords = args.minWords
    maxWords = args.maxWords
    authors = args.authors
    conv = generateNewConversation(numMsgs, startDate, endDate, authors, minWords, maxWords)
    mio.printListToFile(conv, filepath)

if __name__ == "__main__":
    main(sys.argv[1:])


