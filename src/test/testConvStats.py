import datetime
import unittest

from pandas import Timestamp

import util.io as mio
from model.conversationDataframe import ConversationDataframe
from stats.iConvStats import IConvStats
import numpy as np


class BasicStatsTestCase(unittest.TestCase):
    def getConversation(self, filepath):
        #conv = Conversation(filepath)
        conv = ConversationDataframe(filepath)
        conv.loadMessages(0)
        return conv

    def test_basicLengthStats(self):
        conv = self.getConversation(mio.getResourcesPath() + "\\unittest\\test_basic_conv.txt")
        testSet = set(['S1', 'S2'])
        self.assertEqual(testSet, conv.senders)

        totalNumS1, totalLengthS1, avgLegthS1 = conv.stats.getBasicLengthStats('S1')
        self.assertEqual(totalNumS1, 3)
        self.assertEqual(totalLengthS1, 110)
        self.assertEqual(avgLegthS1, 110/3)
        totalNumS2, totalLengthS2, avgLegthS2 = conv.stats.getBasicLengthStats('S2')
        self.assertEqual(totalNumS2, 3)
        self.assertEqual(totalLengthS2, 56)
        self.assertEqual(avgLegthS2, 56/3)
        totalNum, totalLength, avgLegth = conv.stats.getBasicLengthStats()
        self.assertEqual(totalNum, 6)
        self.assertEqual(totalLength, 166)
        self.assertEqual(avgLegth, 166/6)

    def test_intervalStats(self):
        conv = self.getConversation(mio.getResourcesPath() + "\\unittest\\test_interval_conv.txt")
        start, end, interval = conv.stats.getIntervalStats()
        days = conv.stats.getDaysWithoutMessages()

        self.assertEqual(start, Timestamp('2014-01-01 00:00:00'))
        self.assertEqual(end, Timestamp('2014.01.07 00:10:00'))
        self.assertEqual(interval, datetime.timedelta(6, 600))
        self.assertTrue(set(days) == set(['2014.01.02', '2014.01.06']))

    def test_emoticonStats(self):
        conv = self.getConversation(mio.getResourcesPath() + "\\unittest\\test_emoticons_conv.txt")
        numEmoticons = conv.stats.getEmoticonsStats()[0]
        numEmoticonsS1 = conv.stats.getEmoticonsStats(sender='S1')[0]
        numEmoticonsS2 = conv.stats.getEmoticonsStats(sender='S2')[0]

        self.assertEqual(numEmoticons, 6)
        self.assertEqual(numEmoticonsS1, 3)
        self.assertEqual(numEmoticonsS2, 3)

    def test_singleWordCount(self):
        conv = self.getConversation(mio.getResourcesPath() + "\\unittest\\test_word_count.txt")
        totalCount = conv.stats.getWordCountStats(word='hello')
        s1Count = conv.stats.getWordCountStats(word='hello', sender='S1')
        s2Count = conv.stats.getWordCountStats(word='hello', sender='S2')

        self.assertEqual(totalCount, 3)
        self.assertEqual(s1Count, 2)
        self.assertEqual(s2Count, 1)

    def test_wordsUsedJustByStats(self):
        conv = self.getConversation(mio.getResourcesPath() + "\\unittest\\test_word_count.txt")
        wordsUsedBy = conv.stats.getWordsBySender(usedJustBy=True)
        wordsSaidJustByS1 = wordsUsedBy['S1']
        wordsSaidJustByS2 = wordsUsedBy['S2']

        sender = {'S2': {'fine', 'sender2', 'xd', ':d'},
                  'S1': {'are', 'how', 'you', 'sender1', 'bye'}}
        self.assertEqual(wordsSaidJustByS1, sender['S1'])
        self.assertEqual(wordsSaidJustByS2, sender['S2'])

    def test_lexicalStats(self):
        conv = self.getConversation(mio.getResourcesPath() + "\\unittest\\test_word_count.txt")
        tokensCount, vocabularyCount, lexicalRichness = conv.stats.getLexicalStats()

        self.assertEqual(tokensCount, 18)
        self.assertEqual(vocabularyCount, 17)
        self.assertEqual(lexicalRichness, vocabularyCount/tokensCount)

    def test_delayStats(self):
       conv = self.getConversation(mio.getResourcesPath() + "\\unittest\\test_delay_conv.txt")
       df = conv.stats.generateStats(IConvStats.STATS_NAME_DELAY)

       self.assertEqual(df.loc['S1'].values[0], (np.timedelta64(10, 'h')+np.timedelta64(8, 's')))
       self.assertEqual(df.loc['S2'].values[0], np.timedelta64(10, 's'))

if __name__ == '__main__':
    unittest.main()
