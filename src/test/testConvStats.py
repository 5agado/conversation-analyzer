import unittest
from model.conversation import Conversation
import util.io as mio
from util.convStatsDataFrame import ConvStatsDataFrame
from util.convStats import ConvStats

class BasicStatsTestCase(unittest.TestCase):
    def getConversation(self, filepath):
        conv = Conversation(filepath)
        conv.loadMessages(0)
        conv.stats = ConvStatsDataFrame(conv)
        #conv.stats = ConvStats(conv)
        return conv

    def test_basicLengthStats(self):
        conv = self.getConversation(mio.getResourcesPath() + "\\unittest\\test_basic_conv.txt")
        testSet = set(['S1', 'S2'])
        convSet = set([conv.sender1, conv.sender2])
        self.assertEqual(testSet, convSet)

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

    def test_emoticonStats(self):
        conv = self.getConversation(mio.getResourcesPath() + "\\unittest\\test_emoticons_conv.txt")
        numEmoticons, numEmoticonsS1, numEmoticonsS2 = conv.stats.getEmoticonsStats()
        sender = {'S1': 3, 'S2': 3}

        self.assertEqual(numEmoticons, 6)
        self.assertEqual(numEmoticonsS1, sender[conv.sender1])
        self.assertEqual(numEmoticonsS2, sender[conv.sender2])

    def test_singleWordCount(self):
        conv = self.getConversation(mio.getResourcesPath() + "\\unittest\\test_word_count.txt")
        totalCount, s1Count, s2Count = conv.stats.getWordCountStats(word='hello')

        sender = {'S1': 2, 'S2': 1}
        self.assertEqual(totalCount, 3)
        self.assertEqual(s1Count, sender[conv.sender1])
        self.assertEqual(s2Count, sender[conv.sender2])

    def test_mentionedWordsStats(self):
        conv = self.getConversation(mio.getResourcesPath() + "\\unittest\\test_word_count.txt")
        wordsSaidByBoth, wordsSaidJustByS1, wordsSaidJustByS2 = conv.stats.getWordsMentioningStats()

        sender = {'S1': {'name', 'fine', 'my', 'hello', 'is', 'sender2', 'xd', ':d'},
                  'S2': {'name', 'my', 'are', 'how', 'hello', 'is', 'you', 'sender1', 'bye'}}
        self.assertEqual(wordsSaidByBoth, {'my', 'is', 'are', 'how', 'xd', 'you', 'hello',
                                           'sender1', ':d', 'bye', 'sender2', 'name', 'fine'})
        self.assertEqual(wordsSaidJustByS1, sender[conv.sender1])
        self.assertEqual(wordsSaidJustByS2, sender[conv.sender2])

    def test_lexicalStats(self):
        conv = self.getConversation(mio.getResourcesPath() + "\\unittest\\test_word_count.txt")
        tokensCount, vocabularyCount, lexicalRichness = conv.stats.getLexicalStats()
        print((tokensCount, vocabularyCount, lexicalRichness))

        self.assertEqual(tokensCount, 18)
        self.assertEqual(vocabularyCount, 17)
        self.assertEqual(lexicalRichness, vocabularyCount/tokensCount)

    #todo test other combinations of S1 and S2
    def test_delayStats(self):
        conv = self.getConversation(mio.getResourcesPath() + "\\unittest\\test_delay_conv.txt")
        _, senderDelay = conv.stats.getDelayStatsByLength()

        self.assertEqual(senderDelay['S1:S2'], [(24, 8), (86, 2)])
        self.assertEqual(senderDelay['S2:S1'], [(24, 36007), (4, 1)])

if __name__ == '__main__':
    unittest.main()
