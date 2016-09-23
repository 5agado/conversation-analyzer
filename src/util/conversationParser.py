import argparse
import json
import sys
import os
import time

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from util import logger


def parseMessage(msgData, authors):
    """Parse the message contained in msgData.

     Authors should be a dict to provide a correspondence between the IDs as present in the msgData
     and eventually preferred aliases. If a key is not present, the ID itself is used as alias for all
     successive messages.

    :return: A string representing the parsed messages, or None if the value for
    a specific key was not found
    """
    try:
        localTimestamp = time.localtime(msgData["timestamp"]/1000)
        dateAndTime = time.strftime("%Y.%m.%d %H:%M:%S", localTimestamp)
        body = msgData["body"].replace("\n", " ")
        authorId = msgData["author"].split(":")[1]
        if authorId not in authors:
            logger.warning("Missing value for author ID {}. Using directly the ID for all successive messages".format(authorId))
            authors[authorId] = str(authorId)
        author = authors[authorId]
        message = str(dateAndTime) + " " + author + " " + body
        return message
    except KeyError:
        logger.error("Parsing message. KeyError")
        logger.error(msgData)
        return None

def parseConversation(convPath, out, authors):
    """ Parse all "relevant" messages and related attributes, for then saving them to a text file.

    Current message format result example:
    2012.06.17 15:27:42 SENDER_1 Message text from sender1

    Authors should be a dict to provide a correspondence between the IDs as present in the msgData
    and eventually preferred aliases. If a key is not present, the ID itself is used as alias for all
    successive messages.
    """
    with open(convPath, encoding='utf-8') as data_file:
        actions = json.load(data_file)

    f = open(out, "w", encoding='utf-8')
    #TODO consider different type of messages, like when a call or Stickers
    #Stickes leaves and empty message given that there is no textual content
    #log:phone-call, log:video-call
    messages = []
    for action in actions:
        if "log_message_type" in action:
            logger.info("Skipping message of type: " + action["log_message_type"])
            continue
        msg = parseMessage(action, authors)
        if msg:
            messages.append(msg)
    #FIXME happened that number of lines exceeds previously reported number of messages retrieved
    for msg in messages:
        f.write(msg + "\n")

def main(_):
    parser = argparse.ArgumentParser(description='Conversation Parser')
    parser.add_argument('--in', metavar='conversationPath', dest='convPath', required=True)
    parser.add_argument('--out', metavar='outputFile', dest='out', required=True)
    parser.add_argument('--authors', metavar='authors', dest='authors', type=json.loads,
                        default={},
                        help=""" dict to provide a correspondence between the profile IDs
                                and eventually preferred aliases""")

    args = parser.parse_args()
    convPath = args.convPath
    out = args.out
    authors = args.authors

    parseConversation(convPath, out, authors)

if __name__ == "__main__":
    main(sys.argv[1:])
