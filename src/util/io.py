import logging
import os
from datetime import datetime

from pandas import read_csv

from model.message import Message


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

def printBasicLengthStats(basicLengthStatsDf):
    logging.info("##BASIC LENGTH STATS")

    for sender, vals in basicLengthStatsDf.iterrows():
        totalNum, totalLength, avgLegth = vals.tolist()
        logging.info("#" + sender)
        logging.info("Number of messages: {}".format(totalNum))
        logging.info("Total length: {}".format(totalLength))
        logging.info("Average length: {0:.2f}".format(avgLegth))

    logging.info('-'*10)

def printLexicalStats(lexicalStatsDf):
    logging.info("##LEXICAL STATS")

    for sender, vals in lexicalStatsDf.iterrows():
        tokensCount, vocabularyCount, lexicalRichness = vals.tolist()
        logging.info("#" + sender)
        logging.info("Tokens count: {}".format(tokensCount))
        logging.info("Distinct tokens count: {}".format(vocabularyCount))
        logging.info("Lexical diversity: {0:.5f}".format(lexicalRichness))

    logging.info('-'*10)

def printIntervalStatsFor(start, end, interval, days):
    logging.info("##Conv Interval")
    logging.info("Conversation started: {}".format(str(start)))
    logging.info("Conversation ended: {}".format(str(end)))
    logging.info("Conversation overall duration: {}".format(interval))

    logging.info("{} days without messages".format(len(days)))
    percentage = (len(days)/(interval.days+1))*100
    logging.info("{0:.2f}% out of the conversation overall days-interval".format(percentage))
    #logging.info(days)

    logging.info('-'*10)

def printEmoticonsStats(emoticonsStatsDf):
    logging.info("##EMOTICONS STATS")

    for sender, vals in emoticonsStatsDf.iterrows():
        numEmoticons, emoticonsRatio, lenMsgs = vals.tolist()
        logging.info("#" + sender)
        logging.info("Emoticons count: {}".format(numEmoticons))
        logging.info("Messages total length: {}".format(lenMsgs))
        logging.info("Ratio: {0:.5f}".format(emoticonsRatio))

    logging.info('-'*10)

def printWordsBySender(conv):
    data = conv.stats.getWordsBySender()
    for sender in conv.senders:
        words = data[sender]
        printListToFile(words, conv.statsFolder + "\\wordsUsedBy" + sender + ".txt",
                    "#Words by Relevance")

def printWordsUsedJustByToFile(conv):
    data = conv.stats.getWordsBySender(usedJustBy=True)
    for sender in conv.senders:
        wordsSaidJustBySender = data[sender]
        printListToFile(wordsSaidJustBySender, conv.statsFolder + "\\wordsSaidJustBy" + sender + ".txt",
                    "#Words said just by " + sender)

def printDelayStatsFor(conv):
    delay = conv.stats.getDelayStats()
    logging.info("##Reply Delay Stats")
    logging.info("Reply delay by sender: ")
    for s, d in delay.items():
        msg = "Between {} and {}".format(s.split(':')[0], s.split(':')[1])
        logging.info('{} : {}'.format(msg, d))
    logging.info('-'*10)

def printDataFrameToFile(df, filepath):
    #df.index.name = aggType
    #df.sort_index(inplace=True)
    df.to_csv(filepath)

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