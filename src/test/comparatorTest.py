import logging
import argparse
from model.conversation import Conversation
from util import conversationsComparator

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
    parser = argparse.ArgumentParser(description='Conversation Analyzer')
    parser.add_argument('-p1', metavar='conversation1filePath', dest='filepath1', required=True)
    parser.add_argument('-p2', metavar='conversation2filePath', dest='filepath2', required=True)
    parser.add_argument('-s', metavar='startDate', dest='startDate', required=True)
    parser.add_argument('-s', metavar='endDate', dest='endDate', required=True)

    args = parser.parse_args()
    filepath1 = args.filepath1
    filepath2 = args.filepath2
    startDate = args.startDate
    endDate = args.endDate

    initLogger()
    conv1 = Conversation(filepath1)
    conv2 = Conversation(filepath2)
    conversationsComparator.compare(conv1, conv2, startDate, endDate)
