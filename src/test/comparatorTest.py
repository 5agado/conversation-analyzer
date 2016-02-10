import logging
import argparse
from model.conversation import Conversation
from util import conversationsComparator
from util import conversationGenerator
from util import io as mio
import sys
import os

def initLogger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)s - %(message)s",
                                  "%Y-%m-%d %H:%M:%S")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

def init(_):
    # parser = argparse.ArgumentParser(description='Conversation Analyzer')
    # parser.add_argument('-p1', metavar='conversation1filePath', dest='filepath1', required=True)
    # parser.add_argument('-p2', metavar='conversation2filePath', dest='filepath2', required=True)
    # parser.add_argument('-s', metavar='startDate', dest='startDate', required=True)
    # parser.add_argument('-s', metavar='endDate', dest='endDate', required=True)
    #
    # args = parser.parse_args()
    # filepath1 = args.filepath1
    # filepath2 = args.filepath2
    # startDate = args.startDate
    # endDate = args.endDate

    conv = conversationGenerator.generateNewConversation(100, "2014.01.30 06:01:57", "2014.12.30 06:01:57", ["s1", "s2"])
    mio.printListToFile(conv, os.path.join(mio.getResourcesPath(), "test.txt"))
    initLogger()
    #conv1 = Conversation(filepath1)
    #conv2 = Conversation(filepath2)
    #conversationsComparator.compare(conv1, conv2, startDate, endDate)

init(sys.argv[1:])
