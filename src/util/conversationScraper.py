import urllib.parse
import urllib.request
import gzip
import os
import json
import sys
import time
import io
import argparse
import configparser
import logging

#TODO find way to merge messages if already present
#in order to avoid to scrape all the conversation every time
class ConversationScraper:
    """Scraper that retrieves, manipulates and stores all messages belonging to a specific Faceboo conversation"""

    REQUEST_WAIT = 10
    ERROR_WAIT = 30
    CONVERSATION_ENDMARK = "end_of_history"

    def __init__(self, convID, offset, chunkSize, cookie, fb_dtsg, userID, outDir):
        self._directory = outDir + "/" + str(convID) + "/"
        self._convID = convID
        self._timestamp = ""
        self._offset = offset
        self._chunkSize = chunkSize
        self._cookie = cookie
        self._fb_dtsg = fb_dtsg
        self._userID = userID


    """
    POST Request full form data:

    "messages[user_ids][][offset]": "",
    "messages[user_ids][][timestamp]": "",
    "messages[user_ids][][]": "",
    "client": "",
    "__user": "",
    "__a": "",
    "__dyn": "",
    "__req": "",
    "fb_dtsg": "",
    "ttstamp": "",
    "__rev": ""

    """
    def generateRequestData(self):
        """Generate the data for the POST request.
         :return: the generated data
        """
        dataForm = {"messages[user_ids][" + str(self._convID) + "][offset]": str(self._offset),
                     "messages[user_ids][" + str(self._convID) + "][timestamp]": self._timestamp,
                     "messages[user_ids][" + str(self._convID) + "][limit]": str(self._chunkSize),
                     "client": "web_messenger",
                     "__a": "",
                     "__dyn": "",
                     "__req": "",
                     "fb_dtsg": self._fb_dtsg}
        data = urllib.parse.urlencode(dataForm)
        data = data.encode('utf-8')
        return data

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
        The request headers are generate here
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
        req = urllib.request.Request(url, requestData, headers)
        with urllib.request.urlopen(req) as response:
            with gzip.GzipFile(fileobj=response) as uncompressed:
                decompressedFile = uncompressed.read()
        end = time.time()
        logging.info("Retrieved in {}s".format(end-start))
        return  decompressedFile.decode("utf-8")

    def scrapeConversation(self, merge):
        """Retrieves all conversation messages and stores them in a JSON file
        If merge is specified, then new messages are merged the the previously already scraped conversation
        """

        if not os.path.exists(self._directory):
            if merge:
                logging.error("Conversation not present. Merge operation not possible")
                return
            os.makedirs(self._directory)

        logging.info("Starting scraping of conversation {}".format(self._convID))

        messages = []
        if merge:
            with open(self._directory + "conversation.json") as conv:
                convMessages = json.load(conv)
        msgsData = ""
        while self.CONVERSATION_ENDMARK not in msgsData:
            reqData = self.generateRequestData()
            #TODO remove timestamp info
            print("Retrieving messages " + str(self._offset) + "-" + str(self._chunkSize+self._offset) + ", timestamp " + self._timestamp)
            responseData = self.executeRequest(reqData)
            #Remove additional leading characters
            msgsData = responseData[9:]
            jsonData = json.loads(msgsData)

            numMsgs = 0
            if jsonData and jsonData['payload']:
                try:
                    actions = jsonData['payload']['actions']
                    numMsgs += len(actions)

                    #case when the last message already present in the conversation
                    #is older newer than the first one of the current retrieved chunk
                    #print(str(convMessages[-1]["timestamp"]) + " > " + str(actions[0]["timestamp"]))
                    if merge and convMessages[-1]["timestamp"] > actions[0]["timestamp"]:
                        print(str(convMessages[-1]["timestamp"]) + " > " + str(actions[0]["timestamp"]))
                        for i, action in enumerate(actions):
                            if convMessages[-1]["timestamp"] == actions[i]["timestamp"]:
                                print("Found same message: " + actions[i]["timestamp"])
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
                    try:
                        self._timestamp = str(actions[0]["timestamp"])
                    except KeyError:
                        print(actions[0])
                except KeyError:
                    logging.warning("No payload or actions in response")
                    pass
            else:
                logging.error("Response error. Empty data or payload")
                logging.info("Retrying in " + str(self.ERROR_WAIT) + " seconds")
                time.sleep(self.ERROR_WAIT)
                continue

            # outPath = directory + str(self._offset) + "-" + str(self._chunkSize+self._offset) + ".json"
            # with open(outPath, 'w') as out:
            #     out.write(msgsData)
            # command = "python -mjson.tool " + outPath + " > " + pretty_directory + str(self._offset) + "-" + str(self._chunkSize+self._offset) + ".pretty.json"
            # os.system(command)

            self._offset += self._chunkSize
            logging.info("Waiting {}s for the next request".format(self.REQUEST_WAIT))
            time.sleep(self.REQUEST_WAIT)

        logging.info("Conversation scraped successfully. {} messages retrieved".format(numMsgs))

        with open(self._directory + "conversation.json", 'w') as conv:
            conv.write(json.dumps(messages))
        command = "python -mjson.tool " + self._directory + "conversation.json > " + self._directory + "conversation.pretty.json"
        os.system(command)

def main(_):
    parser = argparse.ArgumentParser(description='Conversation Scraper')
    parser.add_argument('-id', metavar='conversationID', dest='convID', required=True)
    parser.add_argument('-sz', metavar='chunkSize', type=int, dest='chunkSize', default=2000)
    parser.add_argument('-off', metavar='offset', type=int, dest='offset', default=0)
    #Tells the program to try to merge the new messages of a previously already scraped conversation
    #avoid the need to scrape it all from the beginning
    parser.add_argument('-m', dest='merge', action='store_true')
    parser.set_defaults(merge=False)
    parser.add_argument('-out', metavar='outputDir', dest='outDir', default='..\\..\\Messages')
    parser.add_argument('-conf', metavar='configFilepath', dest='configFilepath', default='..\\..\\config.ini')

    args = parser.parse_args()
    convID = args.convID
    chunkSize = args.chunkSize
    offset = args.offset
    merge = args.merge
    outDir = args.outDir
    configFilepath = args.configFilepath

    DATA_SECTION = "User Data"
    config = configparser.ConfigParser(interpolation=None)
    config.read(configFilepath)

    cookie = config.get(DATA_SECTION, "Cookie")
    fb_dtsg = config.get(DATA_SECTION, "Fb_dtsg")
    userID = config.get(DATA_SECTION, "UserID")

    scraper = ConversationScraper(convID, offset, chunkSize, cookie, fb_dtsg, userID, outDir)
    scraper.scrapeConversation(merge)

if __name__ == "__main__":
    main(sys.argv[1:])