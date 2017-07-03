import os
import sys
from datetime import datetime

from pandas import read_csv

from model.message import Message

from os.path import dirname
sys.path.append(dirname(__file__)+"\\..")
from util import logger

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
        logger.warning("No such file: " + filePath)
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
        logger.warning("No such file " + filePath)
    return theSet

def displayDispersionPlot(conv, words):
    text = conv.getAsNLTKText()
    text.dispersion_plot(words)

def showConcordance(conv, word):
    text = conv.getAsNLTKText()
    text.concordance(word)

def printBasicLengthStats(basicLengthStatsDf):
    logger.info("##BASIC LENGTH STATS")

    for sender, vals in basicLengthStatsDf.iterrows():
        totalNum, totalLength, avgLegth = vals.tolist()
        logger.info("#" + sender)
        logger.info("Number of messages: {:.0f}".format(totalNum))
        logger.info("Total length: {:.0f}".format(totalLength))
        logger.info("Average length: {0:.2f}".format(avgLegth))

    logger.info('-'*10)

def printLexicalStats(lexicalStatsDf):
    logger.info("##LEXICAL STATS")

    for sender, vals in lexicalStatsDf.iterrows():
        tokensCount, vocabularyCount, lexicalRichness = vals.tolist()
        logger.info("#" + sender)
        logger.info("Tokens count: {:.0f}".format(tokensCount))
        logger.info("Distinct tokens count: {:.0f}".format(vocabularyCount))
        logger.info("Lexical diversity: {0:.5f}".format(lexicalRichness))

    logger.info('-'*10)

def printIntervalStatsFor(start, end, interval, days):
    logger.info("##Conv Interval")
    logger.info("Conversation started: {}".format(str(start)))
    logger.info("Conversation ended: {}".format(str(end)))
    logger.info("Conversation overall duration: {}".format(interval))

    logger.info("{:.0f} days without messages".format(len(days)))
    percentage = (len(days)/(interval.days+1))*100
    logger.info("{0:.2f}% out of the conversation overall days-interval".format(percentage))
    #logger.info(days)

    logger.info('-'*10)

def printEmoticonsStats(emoticonsStatsDf):
    logger.info("##EMOTICONS STATS")

    for sender, vals in emoticonsStatsDf.iterrows():
        numEmoticons, emoticonsRatio, lenMsgs = vals.tolist()
        logger.info("#" + sender)
        logger.info("Emoticons count: {:.0f}".format(numEmoticons))
        logger.info("Messages total length: {:.0f}".format(lenMsgs))
        logger.info("Ratio: {0:.5f}".format(emoticonsRatio))

    logger.info('-'*10)

def saveDfToStatsFolder(conv, df, filename, saveIndex=True):
    statsFolder = os.path.join(os.path.dirname(conv.filepath), 'stats')
    if not os.path.exists(statsFolder):
        os.makedirs(statsFolder)
    df.to_csv(os.path.join(statsFolder, filename), index=saveIndex)

def printDelayStatsFor(conv):
    delay = conv.stats.getDelayStats()
    logger.info("##Reply Delay Stats")
    logger.info("Reply delay by sender: ")
    for s, d in delay.items():
        msg = "Between {} and {}".format(s.split(':')[0], s.split(':')[1])
        logger.info('{} : {}'.format(msg, d))
    logger.info('-'*10)

def printDictToFile(d, title, filepath):
    with open(filepath, "w+", encoding="utf8") as f:
        if title:
            f.write(title + "\n")
        for k, v in d.items():
            f.write('{} : {}\n'.format(k, v))

def printListToFile(l, filepath, title=None):
    with open(filepath, "w+", encoding="utf8") as f:
        if title:
            f.write(title + "\n")
        for e in l:
            f.write(str(e)+"\n")

def getResourcesPath():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'resources'))