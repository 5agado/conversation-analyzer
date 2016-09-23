import argparse
import configparser
import json
import os
import sys
import time

import requests

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from util import logger


class ConversationScraper:
    """Scraper that retrieves, process and stores all messages belonging to a specific Facebook conversation"""

    REQUEST_WAIT = 10
    ERROR_WAIT = 30
    CONVERSATION_ENDMARK = "end_of_history"

    def __init__(self, convID, cookie, fb_dtsg, outDir):
        self._directory = outDir + "/" + str(convID) + "/"
        self._convID = convID
        self._cookie = cookie
        self._fb_dtsg = fb_dtsg

    """
    POST Request full form data
    (<ids_type> is "thread_fbids" for group conversations, "user_ids" otherwise)

    "messages[<ids_type>][][offset]": "",
    "messages[<ids_type>][][timestamp]": "",
    "messages[<ids_type>][][]": "",
    "client": "",
    "__user": "",
    "__a": "",
    "__dyn": "",
    "__req": "",
    "fb_dtsg": "",
    "ttstamp": "",
    "__rev": ""

    """
    def generateRequestData(self, offset, timestamp, chunkSize, isGroupConversation=False):
        """Generate the data for the POST request.
         :return: the generated data
        """
        ids_type = "thread_fbids" if isGroupConversation else "user_ids"

        dataForm = {"messages[{}][{}][offset]".format(ids_type, self._convID) : str(offset),
                    "messages[{}][{}][timestamp]".format(ids_type, self._convID): timestamp,
                    "messages[{}][{}][limit]".format(ids_type, self._convID): str(chunkSize),
                     "client": "web_messenger",
                     "__a": "",
                     "__dyn": "",
                     "__req": "",
                     "fb_dtsg": self._fb_dtsg}
        return dataForm

    """
    POST Request all header:

    "Host": "www.facebook.com",
    "Origin": "http://www.facebook.com",
    "Referer": "https://www.facebook.com",
    "accept-encoding": "gzip,deflate",
    "accept-language": "en-US,en;q=0.8",
    "cookie": "",
    "pragma": "no-cache",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.122 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded",
    "accept": "*/*",
    "cache-control": "no-cache"

    """
    def executeRequest(self, requestData):
        """Executes the POST request and retrieves the correspondent response content.
        Request headers are generated here
        :return: the response content
        """
        headers = {"Host": "www.facebook.com",
                   "Origin":"http://www.facebook.com",
                   "Referer":"https://www.facebook.com",
                   "accept-encoding": "gzip,deflate",
                   "accept-language": "en-US,en;q=0.8",
                   "cookie": self._cookie,
                   "pragma": "no-cache",
                   "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.122 Safari/537.36",
                   "content-type": "application/x-www-form-urlencoded",
                   "accept": "*/*",
                   "cache-control": "no-cache"}

        url = "https://www.facebook.com/ajax/mercury/thread_info.php"

        start = time.time()
        response = requests.post(url, data=requestData, headers=headers)
        end = time.time()
        logger.info("Retrieved in {0:.2f}s".format(end-start))

        #Remove additional leading characters
        msgsData = response.text[9:]
        return  msgsData

    def writeMessages(self, messages):
        with open(self._directory + "conversation.json", 'w') as conv:
            conv.write(json.dumps(messages))
        command = "python -mjson.tool " + self._directory + "conversation.json > " + self._directory + "conversation.pretty.json"
        os.system(command)

    def scrapeConversation(self, merge, offset, timestampOffset, chunkSize, limit, isGroupConversation):
        """Retrieves conversation messages and stores them in a JSON file
        If merge is specified, the new messages will be merged with the previous version of the conversation, if present
        """

        if merge:
            if not os.path.exists(self._directory + "conversation.json"):
                logger.error("Conversation not present. Merge operation not possible")
                return
            with open(self._directory + "conversation.json") as conv:
                convMessages = json.load(conv)
                numMergedMsgs = 0

        if not os.path.exists(self._directory):
            os.makedirs(self._directory)

        logger.info("Starting scraping of conversation {}".format(self._convID))

        messages = []
        msgsData = ""
        timestamp = "" if timestampOffset == 0 else str(timestampOffset)
        while self.CONVERSATION_ENDMARK not in msgsData:
            requestChunkSize = chunkSize if limit <= 0 else min(chunkSize, limit-len(messages))
            reqData = self.generateRequestData(offset, timestamp, requestChunkSize, isGroupConversation)
            logger.info("Retrieving messages " + str(offset) + "-" + str(requestChunkSize+offset))
            msgsData = self.executeRequest(reqData)
            jsonData = json.loads(msgsData)

            if jsonData and ('payload' in jsonData) and jsonData['payload']:
                if ('actions' in jsonData['payload']) and jsonData['payload']['actions']:
                    actions = jsonData['payload']['actions']

                    #case when the last message already present in the conversation
                    #is older newer than the first one of the current retrieved chunk
                    if merge and convMessages[-1]["timestamp"] > actions[0]["timestamp"]:
                        for i, action in enumerate(actions):
                            if convMessages[-1]["timestamp"] == actions[i]["timestamp"]:
                                numMergedMsgs = len(actions[i+1:-1]) + len(messages)
                                messages = convMessages + actions[i+1:-1] + messages
                                break
                        break

                    #We retrieve one message two times, as the first one of the previous chunk
                    #and as the last one of the new one. So we here remove the duplicate,
                    #but only once we already retrieved at least one chunk
                    if len(messages) == 0:
                        messages = actions
                    else:
                        messages = actions[:-1] + messages

                    #update timestamp
                    timestamp = str(actions[0]["timestamp"])
                else:
                    if 'errorSummary' in jsonData:
                        logger.error("Response error: " + jsonData['errorSummary'])
                    else:
                        logger.error("Response error. No messages found")
                        logger.error(msgsData)
                    return
            else:
                logger.error("Response error. Empty data or payload")
                logger.error(msgsData)
                logger.info("Retrying in " + str(self.ERROR_WAIT) + " seconds")
                time.sleep(self.ERROR_WAIT)
                continue

            offset += chunkSize
            if limit!= 0 and len(messages) >= limit:
                break

            time.sleep(self.REQUEST_WAIT)

        if merge:
            logger.info("Successfully merged {} new messages".format(numMergedMsgs))
            logger.info("Conversation total message count = {}".format(len(messages)))
        else:
            logger.info("Conversation scraped successfully. {} messages retrieved".format(len(messages)))

        self.writeMessages(messages)

def main(_):
    parser = argparse.ArgumentParser(description='Conversation Scraper')
    parser.add_argument('--id', metavar='conversationID', dest='convID', required=True)
    parser.add_argument('--size', metavar='chunkSize', type=int, dest='chunkSize', default=2000,
                        help="number of messages to retrieve for each request")
    #TODO not working, the timestamp seems the only relevant parameter
    parser.add_argument('--off', metavar='offset', type=int, dest='offset', default=0,
                        help="messages number scraping offset")
    #TODO to test, ??better single var
    parser.add_argument('--date', metavar='offset', type=int, dest='timestampOffset', default=0,
                        help="messages timestamp scraping offset, has precedence over messages number offset")
    parser.add_argument('--limit', type=int, dest='limit', default=0,
                        help="number of messages to be retrieved")
    #Tells the program to try to merge the new messages with the previously scraped conversation
    #avoid the need to scrape it all from the beginning
    parser.add_argument('-m', dest='merge', action='store_true',
                        help="merge the new messages with previously scraped conversation")
    parser.add_argument('-g', dest='isGroupConversation', action='store_true',
                        help="specify if you want to scrape a group conversation")
    parser.set_defaults(merge=False)
    baseFolderPath = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
    parser.add_argument('--out', metavar='outputDir', dest='outDir', default= baseFolderPath+'\\Messages')
    parser.add_argument('--conf', metavar='configFilepath', dest='configFilepath', default= baseFolderPath+'\\config.ini')

    args = parser.parse_args()
    convID = args.convID
    chunkSize = args.chunkSize
    timestampOffset = args.timestampOffset
    offset = args.offset
    limit = args.limit
    merge = args.merge
    isGroupConversation = args.isGroupConversation
    outDir = args.outDir
    configFilepath = args.configFilepath

    DATA_SECTION = "User Data"
    config = configparser.ConfigParser(interpolation=None)
    config.read(configFilepath)

    cookie = config.get(DATA_SECTION, "Cookie")
    fb_dtsg = config.get(DATA_SECTION, "Fb_dtsg")

    scraper = ConversationScraper(convID, cookie, fb_dtsg, outDir)
    scraper.scrapeConversation(merge, offset, timestampOffset, chunkSize, limit, isGroupConversation)

if __name__ == "__main__":
    main(sys.argv[1:])