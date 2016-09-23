import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import logging
import argparse
from model.conversation import Conversation

def compare(conv1, conv2, startDate, endDate):
    try:
        conv1.loadMessages(0, startDate, endDate)
        conv2.loadMessages(0, startDate, endDate)
    except Exception as e:
        logging.error(str(e))
        logging.error("Terminating program")
        sys.exit(1)

    logging.info("Comparing {} with {}".format(conv1.filepath, conv2.filepath))

    #Interval stats
    start1, end1, interval1 = conv1.getIntervalStats()
    start2, end2, interval2 = conv1.getIntervalStats()
    days1 = conv1.getDaysWithoutMessages()
    days2 = conv2.getDaysWithoutMessages()

    logging.info("Conversation started: {} against {}".format(start1, start2))
    logging.info("Conversation ended: {} against {}".format(end1, end2))
    logging.info("Conversation overall duration: {} against {}. Ratio = {}".format(interval1, interval2, interval1/interval2))

    logging.info("Days without messages: {} against {}".format(len(days1), len(days2)))
    percentage1 = (len(days1)/(interval1.days+1))*100
    percentage2 = (len(days2)/(interval2.days+1))*100
    logging.info("{0:.2f}% out of the conversation overall days-interval, against {0:.2f}%".format(percentage1, percentage2))

    #Basic length stats
    totalNum1, totalLength1, avgLegth1 = conv1.getBasicLengthStats()
    totalNum2, totalLength2, avgLegth2 = conv2.getBasicLengthStats()

    logging.info("Total number of messages: {} against {}. Ratio = {}".format(totalNum1, totalNum2, totalNum1/totalNum2))
    logging.info("Total length: {} against {}. Ratio = {}".format(totalLength1, totalLength2, totalLength1/totalLength2))
    logging.info("Average length: {0:.2f} against {}. Ratio = {}".format(avgLegth1, avgLegth2, avgLegth1/avgLegth2))

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
    parser = argparse.ArgumentParser(description='Conversations Comparator')
    parser.add_argument('-p1', metavar='conversation1filePath', dest='filepath1', required=True)
    parser.add_argument('-p2', metavar='conversation2filePath', dest='filepath2', required=True)
    parser.add_argument('-s', metavar='startDate', dest='startDate', required=True)
    parser.add_argument('-e', metavar='endDate', dest='endDate', required=True)

    args = parser.parse_args()
    filepath1 = args.filepath1
    filepath2 = args.filepath2
    startDate = args.startDate
    endDate = args.endDate

    initLogger()
    conv1 = Conversation(filepath1)
    conv2 = Conversation(filepath2)
    compare(conv1, conv2, startDate, endDate)

init(sys.argv[1:])
