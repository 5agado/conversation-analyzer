import util.io as mio
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
    parser.add_argument('-p', metavar='conversationFilePath', dest='filepath', required=True)
    parser.add_argument('-n', metavar='numberOfMessages', type=int,
                        dest='numMsgs', default=110)
    parser.add_argument('-l', metavar='wordsCountLimit', type=int,
                        dest='wCountLimit', default=20)

    args = parser.parse_args()
    filepath = args.filepath
    numMsgs = args.numMsgs
    wCountLimit = args.wCountLimit

    CONFIG_FILEPATH = "..\\config.ini"
    STATS_SECTION = "Stats"
    config = configparser.ConfigParser()
    config.read(CONFIG_FILEPATH)

    P_BASIC_LENGTH_STATS = config.get(STATS_SECTION, "P_BASIC_LENGTH_STATS")
    P_INTERVAL_STATS = config.get(STATS_SECTION, "P_INTERVAL_STATS")
    P_WORDS_COUNT = config.get(STATS_SECTION, "P_WORDS_COUNT")
    P_WORDS_MENTIONING = config.get(STATS_SECTION, "P_WORDS_MENTIONING")
    P_AGG_STATS = config.get(STATS_SECTION, "P_AGG_STATS")
    P_DELAY_STATS = config.get(STATS_SECTION, "P_DELAY_STATS")
    P_EMOTICONS_STATS = config.get(STATS_SECTION, "P_EMOTICONS_STATS")
    P_LEXICAL_STATS = config.get(STATS_SECTION, "P_LEXICAL_STATS")

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
        mio.printWordsCountToFile(conv, wCountLimit)

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
        mio.printEmoticonStatsToFile(lambda m: m.date, 'EmoticonDay', conv)

if __name__ == "__main__":
    main(sys.argv[1:])