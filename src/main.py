import argparse
import configparser
import sys
import os

import util.io as mio
from model.conversation import Conversation
from model.conversationDataframe import ConversationDataframe
from stats.iConvStats import IConvStats

def main(_):
    parser = argparse.ArgumentParser(description='Conversation Analyzer')
    parser.add_argument('-p', metavar='conversationFilepath', dest='filepath', required=True)
    parser.add_argument('-n', metavar='numberOfMessages', type=int, dest='numMsgs', default=0,
                        help='number of conversation messages to be analyzed')
    baseFolderPath = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    parser.add_argument('--conf', metavar='configFilepath', dest='configFilepath', default= baseFolderPath+'\\config.ini')

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
    P_WORDS_USEDJUSTBY = config.getboolean(STATS_SECTION, "P_WORDS_USEDJUSTBY")
    P_DELAY_STATS = config.getboolean(STATS_SECTION, "P_DELAY_STATS")
    P_EMOTICONS_STATS = config.getboolean(STATS_SECTION, "P_EMOTICONS_STATS")
    P_LEXICAL_STATS = config.getboolean(STATS_SECTION, "P_LEXICAL_STATS")

    #conv = Conversation(filepath)
    conv = ConversationDataframe(filepath)
    conv.loadMessages(numMsgs)

    if P_BASIC_LENGTH_STATS:
        stats = conv.stats.generateStats(IConvStats.STATS_NAME_BASICLENGTH)
        mio.printBasicLengthStats(stats)

    if P_INTERVAL_STATS:
        start, end, interval = conv.stats.getIntervalStats()
        days = conv.stats.getDaysWithoutMessages()
        mio.printIntervalStatsFor(start, end, interval, days)

    if P_LEXICAL_STATS:
        stats = conv.stats.generateStats(IConvStats.STATS_NAME_LEXICAL)
        mio.printLexicalStats(stats)

    if P_WORDS_COUNT:
        filepath = conv.statsFolder + '\\' + 'wordCount.txt'
        stats = conv.stats.generateStats(IConvStats.STATS_NAME_WORDCOUNT)
        mio.printDataFrameToFile(stats, filepath)

    #Works just with two senders
    if P_WORDS_USEDJUSTBY:
        mio.printWordsUsedJustByToFile(conv)

    if P_EMOTICONS_STATS:
        stats = conv.stats.generateStats(IConvStats.STATS_NAME_EMOTICONS)
        mio.printEmoticonsStats(stats)

    #Not tested
    #if P_DELAY_STATS:
    #    mio.printDelayStatsFor(conv)


if __name__ == "__main__":
    main(sys.argv[1:])