import logging
import sys

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
