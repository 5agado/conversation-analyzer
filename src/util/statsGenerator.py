import argparse
import sys

from os.path import dirname
sys.path.append(dirname(__file__)+"\\..")
from util import logger

from model.conversationDataframe import ConversationDataframe
from util import io as mio

def main(_):
    parser = argparse.ArgumentParser(description='Statistics Generator')
    parser.add_argument('--in', metavar='conversationPath', dest='convPath', required=True)
    parser.add_argument('--out', metavar='outputFile', dest='out', required=True)
    parser.add_argument('--stats', metavar='statsType', dest='statsType', required=True,
                        help='type of statistic to generate')
    parser.add_argument('--groupby', metavar='groupbyColumns', dest='groupbyColumns', nargs='+', default=[],
                        help='List of features to use for the aggregation of messages prior to the analysis')

    args = parser.parse_args()
    convPath = args.convPath
    out = args.out
    statsType = args.statsType
    groupbyColumns = args.groupbyColumns

    conv = ConversationDataframe(convPath)
    conv.loadMessages()

    stats = conv.stats._generateStats(statsType, groupbyColumns)
    mio.printDataFrameToFile(stats, out)

if __name__ == "__main__":
    main(sys.argv[1:])