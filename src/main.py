import util.io as mio
import util.plotting as mplot
from model.conversation import Conversation
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
        mio.printAllBasicLengthStats(conv)

    if P_LEXICAL_STATS:
        mio.printAllLexicalStats(conv)

    if P_INTERVAL_STATS:
        mio.printIntervalStatsFor(conv)

    if P_WORDS_COUNT:
        mio.printWordsCountToFile(conv, WORDS_COUNT_LIMIT)

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
        mio.printEmoticonStatsToFile(lambda m: m.getHour(), 'EmoticonHours', conv)
        mio.printEmoticonStatsToFile(lambda m: m.date, 'EmoticonDay', conv)
        mio.printEmoticonStatsToFile(lambda m: m.getMonth(), 'EmoticonMonth', conv)

if __name__ == "__main__":
    main(sys.argv[1:])