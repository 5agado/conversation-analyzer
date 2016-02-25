import util.io as mio
import util.plotting as mplot
from model.conversation import Conversation
from util.iConvStats import IConvStats
import argparse
import sys
import configparser
import logging

def initLogger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)s - %(message)s",
                                  "%Y-%m-%d %H:%M:%S")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

def main(_):
    parser = argparse.ArgumentParser(description='Conversation Analyzer')
    parser.add_argument('-p', metavar='conversationFilepath', dest='filepath', required=True)
    parser.add_argument('-n', metavar='numberOfMessages', type=int, dest='numMsgs', default=0,
                        help='number of conversation messages to be analyzed')
    parser.add_argument('--conf', metavar='configFilepath', dest='configFilepath', default='..\\config.ini')

    args = parser.parse_args()
    filepath = args.filepath
    numMsgs = args.numMsgs
    CONFIG_FILEPATH = args.configFilepath

    STATS_SECTION = "Stats"
    config = configparser.ConfigParser()
    config.read(CONFIG_FILEPATH)

    P_BASIC_LENGTH_STATS = config.getboolean(STATS_SECTION, "P_BASIC_LENGTH_STATS")
    P_INTERVAL_STATS = config.getboolean(STATS_SECTION, "P_INTERVAL_STATS")
    P_WORDS_COUNT = config.getboolean(STATS_SECTION, "P_WORDS_COUNT")
    WORDS_COUNT_LIMIT = config.getint(STATS_SECTION, "WORDS_COUNT_LIMIT")
    P_WORDS_MENTIONING = config.getboolean(STATS_SECTION, "P_WORDS_MENTIONING")
    P_AGG_STATS = config.getboolean(STATS_SECTION, "P_AGG_STATS")
    P_DELAY_STATS = config.getboolean(STATS_SECTION, "P_DELAY_STATS")
    P_EMOTICONS_STATS = config.getboolean(STATS_SECTION, "P_EMOTICONS_STATS")
    P_LEXICAL_STATS = config.getboolean(STATS_SECTION, "P_LEXICAL_STATS")

    initLogger()
    conv = Conversation(filepath)
    conv.loadMessages(numMsgs)

    if P_BASIC_LENGTH_STATS:
        stats = conv.stats.generateStats(IConvStats.STATS_NAME_BASICLENGTH)
        mio.printBasicLengthStats(stats)

    if P_LEXICAL_STATS:
        stats = conv.stats.generateStats(IConvStats.STATS_NAME_LEXICAL)
        mio.printLexicalStats(stats)

    if P_INTERVAL_STATS:
        start, end, interval = conv.stats.getIntervalStats()
        days = conv.stats.getDaysWithoutMessages()
        mio.printIntervalStatsFor(start, end, interval, days)

    if P_WORDS_COUNT:
        filepath = conv.statsFolder + '\\' + 'WordCount.txt'
        stats = conv.stats.generateStats(IConvStats.STATS_NAME_WORDCOUNT)
        mio.printDataFrameToFile('Words Count', stats, filepath)

    if P_WORDS_MENTIONING:
        mio.printWordsMentioningToFile(conv)

    if P_AGG_STATS:
        mio.printAgglomeratedStatsToFile(lambda m: m.getHour(), 'Hours', conv)
        mio.printAgglomeratedStatsToFile(lambda m: m.date, 'Day', conv)
        mio.printAgglomeratedStatsToFile(lambda m: m.getMonth(), 'Month', conv)
        mio.printAgglomeratedStatsToFile(lambda m: m.getYear(), 'Year', conv)
        mio.printAgglomeratedStatsToFile(lambda m: m.getWeekDay(), 'WeekDay', conv)

    if P_DELAY_STATS:
        mio.printDelayStatsFor(conv)

    if P_EMOTICONS_STATS:
        filepath = conv.statsFolder + '\\' + 'EmoticonStats.txt'
        stats = conv.stats.generateDataFrameEmoticonsStatsBy(mFun)
        mio.printDataFrameToFile('EmoticonHours', stats, filepath)
        #mio.printEmoticonStatsToFile(lambda m: m.getHour(), 'EmoticonHours', conv)
        #mio.printEmoticonStatsToFile(lambda m: m.date, 'EmoticonDay', conv)
        #mio.printEmoticonStatsToFile(lambda m: m.getMonth(), 'EmoticonMonth', conv)

if __name__ == "__main__":
    main(sys.argv[1:])