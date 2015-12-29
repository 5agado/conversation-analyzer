import logging
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import json
import random
import argparse
import configparser
from model.conversation import Conversation
from bluemixClient import BluemixClient
import util.io as mio

#from watson_developer_cloud import LanguageTranslationV2 as LanguageTranslation

def initLogger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)s - %(message)s",
                                  "%Y-%m-%d %H:%M:%S")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

def init(_):
    parser = argparse.ArgumentParser(description='Bluemix Test')
    parser.add_argument('-p', metavar='conversationFilepath', dest='filepath', required=True)
    parser.add_argument('-n', metavar='numberOfMessages', type=int, dest='numMsgs', default=0,
                        help='number of conversation messages to be analyzed')
    parser.add_argument('--conf', metavar='configFilepath', dest='configFilepath', default='..\\..\\config.ini')

    args = parser.parse_args()
    filepath = args.filepath
    numMsgs = args.numMsgs
    CONFIG_FILEPATH = args.configFilepath

    BLUEMIX_SECTION = "Bluemix"
    config = configparser.ConfigParser()
    config.read(CONFIG_FILEPATH)

    BLUEMIX_USERNAME = config.get(BLUEMIX_SECTION, "USERNAME")
    BLUEMIX_PASSWORD = config.get(BLUEMIX_SECTION, "PASSWORD")

    initLogger()
    #conv = Conversation(mio.getResourcesPath() + "\\unittest\\test_nltk_conv.txt")
    conv = Conversation(filepath)
    conv.loadMessages(numMsgs)

    try:
        randMsgs = [msg.text for msg in random.sample(conv.sender2Messages, 500)]
        text = ' '.join(randMsgs)
    except ValueError:
        print('Sample size exceeded population size.')

    #language_translation = LanguageTranslation(username=BLUEMIX_USERNAME,
    #                                           password=BLUEMIX_PASSWORD)

    #print(json.dumps(language_translation.get_models(), indent=2))
    #print(json.dumps(language_translation.translate('Hola', source='es', target='en'), indent=2,
    #                 ensure_ascii=False))

    client = BluemixClient(BLUEMIX_USERNAME, BLUEMIX_PASSWORD,
                                        "https://gateway.watsonplatform.net/personality-insights/api")
    #                                   "https://gateway.watsonplatform.net/language-translation/api")
    #print(translate(client, "hello", "en", "es"))

    #print(translate(client, text,'en', 'es'))
    with open("tmp", "w+", encoding="utf8") as f:
        f.write(personalityInsights(client, text))
    print(conv.sender2)


def translate(client, text, source, target):
    REQUEST_URL = "https://gateway.watsonplatform.net/language-translation/api/v2/translate"
    postData={"source": source,
              "target": target,
              "text": text}

    return client.request(REQUEST_URL, postData)

def personalityInsights(client, text):
    REQUEST_URL = "https://gateway.watsonplatform.net/personality-insights/api/v2/profile"

    return  client.request(REQUEST_URL, text)

init(sys.argv[1:])