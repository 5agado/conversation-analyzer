from model.message import Message
import logging
import os
from pandas import read_csv
from collections import OrderedDict

def parseMessagesFromFile(filePath, limit = 0):
    messages = []
    senders = set([])
    try:
        with open(filePath, encoding="utf8") as f:
            for line in f:
                date, time, sender, text = line.split(' ', 3)
                messages.append(Message(date, time, sender, text.strip()))
                senders.add(sender)
                if limit != 0 and len(messages) >= limit:
                    break
    except IOError:
        logging.warning("No such file: " + filePath)
    return messages, senders

# def loadData(filePath):
#     try:
#         #TODO is r standard
#         with open(filePath, 'r') as f:
#             data = f.read().split("\n")
#             description = data[0]
#             labels = data[1].split(", ")
#     except IOError:
#         print("No such file: " + filePath)
#     return description, labels, data[2:-1]

def loadDataFromFile(filepath):
    data = read_csv(filepath)
    return data

def getSetFromFile(filePath):
    theSet = set([])
    try:
        with open(filePath) as f:
            theSet = {line.strip() for line in f}
    except IOError:
        logging.warning("No such file " + filePath)
    return theSet

def printWordsCountToFile(conv, limit=0):
    wCount, wCountS1, wCountS2 = conv.getWordsCountStats(limit)

    printDictToFile(OrderedDict(wCount), "#Words Count", conv.folder + "\\wordsCount.txt")
    printDictToFile(OrderedDict(wCountS1), "#Words Count" + conv.sender1, conv.folder + "\\wordsCount" + conv.sender1 + ".txt")
    printDictToFile(OrderedDict(wCountS2), "#Words Count" + conv.sender2, conv.folder + "\\wordsCount" + conv.sender2 + ".txt")

def printWordsMentioningToFile(conv):
    wordsSaidByBoth, wordsSaidJustByS1, wordsSaidJustByS2 = conv.getWordsMentioningStats()
    printListToFile(wordsSaidByBoth, "#Words said by both", conv.folder + "\wordsSaidByBoth.txt")
    printListToFile(wordsSaidJustByS1, "#Words said just by " + conv.sender1, conv.folder + "\\wordsSaidJustBy" + conv.sender1 + ".txt")
    printListToFile(wordsSaidJustByS2, "#Words said just by " + conv.sender2, conv.folder + "\\wordsSaidJustBy" + conv.sender2 + ".txt")


def printAgglomeratedStatsToFile(mFun, aggType, conv):
    filepath = conv.folder + '\\' + aggType + 'Stats.txt'
    df = conv.generateDataFrameAgglomeratedStatsBy(mFun)
    df.index.name = aggType
    df.to_csv(filepath)

def printBasicLengthStats(conv, sender=None):
    totalNum, totalLength, avgLegth = conv.getBasicLengthStats(sender)

    print("Total number of messages: {}".format(totalNum))
    print("Total length: {}".format(totalLength))
    print("Average length: {0:.2f}".format(avgLegth))

def printAllBasicLengthStats(conv):
    print("##Basic length stats")
    print("#Overall")
    printBasicLengthStats(conv)
    print("#" + conv.sender1)
    printBasicLengthStats(conv, conv.sender1)
    print("#" + conv.sender2)
    printBasicLengthStats(conv, conv.sender2)
    print('-'*10)

def printIntervalStatsFor(conv):
    start, end, interval = conv.getIntervalStats()

    print("##Conv Interval")
    print("Conversation started: {}".format(start))
    print("Conversation ended: {}".format(end))
    print("Conversation overall duration: {}".format(interval))
    print('-'*10)

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