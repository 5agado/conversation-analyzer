from model.message import Message
import logging
from datetime import datetime
import os
import pandas as pd
from pandas import read_csv
import numpy as np
from collections import OrderedDict

def parseMessagesFromFile(filePath, limit=0, startDate=None, endDate=None):
    messages = []
    senders = set([])
    if startDate:
        startDate = datetime.strptime(startDate, Message.DATE_FORMAT)
    if endDate:
        endDate = datetime.strptime(endDate, Message.DATE_FORMAT)
    try:
        with open(filePath, 'r', encoding="utf8") as f:
            for line in f:
                date, time, sender, text = line.split(' ', 3)
                if startDate or endDate:
                    thisDate = datetime.strptime(date, Message.DATE_FORMAT)
                    if (not startDate or thisDate>=startDate) and (not endDate or thisDate<=endDate):
                        messages.append(Message(date, time, sender, text.strip()))
                else:
                    messages.append(Message(date, time, sender, text.strip()))
                senders.add(sender)
                if limit != 0 and len(messages) >= limit:
                    break
    except IOError:
        logging.warning("No such file: " + filePath)
    return messages, senders

def loadDataFromFile(filepath):
    data = read_csv(filepath)
    return data

def getSetFromFile(filePath):
    theSet = set([])
    try:
        with open(filePath, 'r') as f:
            theSet = {line.strip() for line in f}
    except IOError:
        logging.warning("No such file " + filePath)
    return theSet

def displayDispersionPlot(conv, words):
    text = conv.getAsNLTKText()
    text.dispersion_plot(words)

def showConcordance(conv, word):
    text = conv.getAsNLTKText()
    text.concordance(word)

def printWordsCountToFile(conv, limit=0):
    wCount, wCountS1, wCountS2 = conv.getWordsCountStats(limit)

    printDictToFile(OrderedDict(wCount), "#Words Count", conv.statsFolder + "\\wordsCount.txt")
    printDictToFile(OrderedDict(wCountS1), "#Words Count" + conv.sender1,
                    conv.statsFolder + "\\wordsCount" + conv.sender1 + ".txt")
    printDictToFile(OrderedDict(wCountS2), "#Words Count" + conv.sender2,
                    conv.statsFolder + "\\wordsCount" + conv.sender2 + ".txt")

def printWordsMentioningToFile(conv):
    wordsSaidByBoth, wordsSaidJustByS1, wordsSaidJustByS2 = conv.getWordsMentioningStats()
    printListToFile(wordsSaidByBoth, "#Words said by both", conv.statsFolder + "\wordsSaidByBoth.txt")
    printListToFile(wordsSaidJustByS1, "#Words said just by " + conv.sender1,
                    conv.statsFolder + "\\wordsSaidJustBy" + conv.sender1 + ".txt")
    printListToFile(wordsSaidJustByS2, "#Words said just by " + conv.sender2,
                    conv.statsFolder + "\\wordsSaidJustBy" + conv.sender2 + ".txt")

def printSingleWordCountToFile(mFun, aggType, word, conv):
    filepath = conv.statsFolder + '\\' + word + "_" + aggType + 'Stats.txt'
    df = conv.generateDataFrameSingleWordCountBy(mFun, word)
    printDataFrameToFile(aggType, df, filepath)

def printAgglomeratedStatsToFile(mFun, aggType, conv):
    filepath = conv.statsFolder + '\\' + aggType + 'Stats.txt'
    df = conv.generateDataFrameAgglomeratedStatsBy(mFun)
    printDataFrameToFile(aggType, df, filepath)

def printEmoticonStatsToFile(mFun, aggType, conv):
    filepath = conv.statsFolder + '\\' + aggType + 'Stats.txt'
    df = conv.generateDataFrameEmoticoStatsBy(mFun)
    printDataFrameToFile(aggType, df, filepath)

def printDataFrameToFile(aggType, df, filepath):
    df.index.name = aggType
    df.sort_index(inplace=True)
    df.to_csv(filepath)

def printBasicLengthStats(conv, sender=None):
    totalNum, totalLength, avgLegth = conv.getBasicLengthStats(sender)

    logging.info("Total number of messages: {}".format(totalNum))
    logging.info("Total length: {}".format(totalLength))
    logging.info("Average length: {0:.2f}".format(avgLegth))

def printAllBasicLengthStats(conv):
    logging.info("##Basic length stats")
    logging.info("#Overall")
    printBasicLengthStats(conv)
    logging.info("#" + conv.sender1)
    printBasicLengthStats(conv, conv.sender1)
    logging.info("#" + conv.sender2)
    printBasicLengthStats(conv, conv.sender2)
    logging.info('-'*10)

def printBasicLengthStatsToFile(conv):
    filepath = conv.statsFolder + '\\' + 'BasicLength' + 'Stats.txt'
    totalNum, totalLength, avgLegth = conv.getBasicLengthStats()
    totalNumS1, totalLengthS1, avgLegthS1 = conv.getBasicLengthStats(conv.sender1)
    totalNumS2, totalLengthS2, avgLegthS2 = conv.getBasicLengthStats(conv.sender2)
    data = np.array([[totalNumS1], [totalNumS2], [totalLengthS1],
                     [totalLengthS2], [avgLegthS1], [avgLegthS2],
                     [totalNum], [totalLength], [avgLegth]]).T
    c = [conv.sender1 + '_numMsgs', conv.sender2 + '_numMsgs',
         conv.sender1 + '_lenMsgs', conv.sender2 + '_lenMsgs',
         conv.sender1 + '_avgLen', conv.sender2 + '_avgLen',
         'totNumMsgs', 'totLenMsgs', 'totAvgLen']
    df = pd.DataFrame(data, columns=c)
    printDataFrameToFile('Basic Length', df, filepath)

def printLexicalStats(conv, sender=None):
    tokensCount, vocabularyCount, lexicalRichness = conv.getLexicalStats(sender)

    logging.info("Tokens count: {}".format(tokensCount))
    logging.info("Distinct tokens count: {}".format(vocabularyCount))
    logging.info("Lexical diversity: {0:.5f}".format(lexicalRichness))

def printAllLexicalStats(conv):
    logging.info("##Lexical stats")
    logging.info("#Overall")
    printLexicalStats(conv)
    logging.info("#" + conv.sender1)
    printLexicalStats(conv, conv.sender1)
    logging.info("#" + conv.sender2)
    printLexicalStats(conv, conv.sender2)
    logging.info('-'*10)

def printIntervalStatsFor(conv):
    start, end, interval = conv.getIntervalStats()

    logging.info("##Conv Interval")
    logging.info("Conversation started: {}".format(start))
    logging.info("Conversation ended: {}".format(end))
    logging.info("Conversation overall duration: {}".format(interval))

    days = conv.getDaysWithoutMessages()
    logging.info("{} days without messages".format(len(days)))
    percentage = (len(days)/(interval.days+1))*100
    logging.info("{0:.2f}% out of the conversation overall days-interval".format(percentage))
    #logging.info(days)

    logging.info('-'*10)

def printDelayStatsFor(conv):
    delay = conv.getDelayStats()
    logging.info("##Reply Delay Stats")
    logging.info("Reply delay by sender: ")
    for s, d in delay.items():
        msg = "Between {} and {}".format(s.split(':')[0], s.split(':')[1])
        logging.info('{} : {}'.format(msg, d))
    logging.info('-'*10)

def printDictToFile(d, title, filepath):
    with open(filepath, "w+", encoding="utf8") as f:
        f.write(title + "\n")
        for k, v in d.items():
            f.write('{} : {}\n'.format(k, v))

def printListToFile(l, title, filepath):
    with open(filepath, "w+", encoding="utf8") as f:
        f.write(title + "\n")
        for e in l:
            f.write(e+"\n")

def getResourcesPath():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'resources'))