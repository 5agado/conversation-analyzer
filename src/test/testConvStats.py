import unittest
from src.model.conversation import Conversation
import util.io as mio

class BasicStatsTestCase(unittest.TestCase):
    # def setUp(self):
    #     self.conv = Conversation(mio.getResourcesPath() + "\\unittest\\test_emoticons_conv.txt")
    #     self.conv.loadMessages(0)

    def test_basicLengthStats(self):
        conv = self.getConversation(mio.getResourcesPath() + "\\unittest\\test_basic_conv.txt")
        testSet = set(['S1', 'S2'])
        convSet = set([conv.sender1, conv.sender2])
        self.assertEqual(testSet, convSet)

        totalNumS1, totalLengthS1, avgLegthS1 = conv.getBasicLengthStats('S1')
        self.assertEqual(totalNumS1, 3)
        self.assertEqual(totalLengthS1, 110)
        self.assertEqual(avgLegthS1, 110/3)
        totalNumS2, totalLengthS2, avgLegthS2 = conv.getBasicLengthStats('S2')
        self.assertEqual(totalNumS2, 3)
        self.assertEqual(totalLengthS2, 56)
        self.assertEqual(avgLegthS2, 56/3)
        totalNum, totalLength, avgLegth = conv.getBasicLengthStats()
        self.assertEqual(totalNum, 6)
        self.assertEqual(totalLength, 166)
        self.assertEqual(avgLegth, 166/6)

    def test_emoticonStats(self):
        conv = self.getConversation(mio.getResourcesPath() + "\\unittest\\test_emoticons_conv.txt")
        numEmoticons, numEmoticonsS1, numEmoticonsS2 = conv.getEmoticonsStats()
        sender = {'S1': 3, 'S2': 2}

        self.assertEqual(numEmoticons, 5)
        self.assertEqual(numEmoticonsS1, sender[conv.sender1])
        self.assertEqual(numEmoticonsS2, sender[conv.sender2])

    #todo test other combinations of S1 and S2
    def test_delayStats(self):
        conv = self.getConversation(mio.getResourcesPath() + "\\unittest\\test_delay_conv.txt")
        _, senderDelay = conv.getDelayStatsByLength()

        self.assertEqual(senderDelay['S1:S2'], [(24, 8), (86, 2)])
        self.assertEqual(senderDelay['S2:S1'], [(24, 36007), (4, 1)])

    def getConversation(self, filepath):
        conv = Conversation(filepath)
        conv.loadMessages(0)
        return conv

if __name__ == '__main__':
    unittest.main()
