import nltk
from nltk.corpus import conll2000

def sentenceSegmentation(text):
    sentences = nltk.sent_tokenize(text)
    return sentences

def wordTokenization(text):
    sentences = sentenceSegmentation(text)
    tokenizedSentences = [nltk.word_tokenize(s) for s in sentences]
    return tokenizedSentences

def posTagging(text):
    tokenizedSentences = wordTokenization(text)
    taggedSentences = [nltk.pos_tag(s) for s in tokenizedSentences]
    return taggedSentences

def drawParse(text):
    sentences = posTagging(text)

    #test_sents = conll2000.chunked_sents('test.txt', chunk_types=['NP'])
    train_sents = conll2000.chunked_sents('train.txt', chunk_types =['NP'])
    chunker = ChunkParser(train_sents)

    for s in sentences:
        chunker.parse(s).draw()

class ChunkParser(nltk.ChunkParserI):
    def __init__(self, train_sents):
        train_data = [[(t,c) for w,t,c in nltk.chunk.tree2conlltags(sent)] for sent in train_sents]
        self.tagger = nltk.TrigramTagger(train_data)

    def parse(self, sentence):
        pos_tags= [pos for (word,pos) in sentence]
        tagged_pos_tags = self.tagger.tag(pos_tags)
        chunktags = [chunktag for (pos,chunktag) in tagged_pos_tags]
        conlltags = [(word,pos,chunktag) for ((word,pos), chunktag) in zip(sentence,chunktags)]
        return nltk.chunk.conlltags2tree(conlltags)

def senderClassification(conv):
    messages = [(m.text, m.sender) for m in conv.messages]
    wordFeature = list(conv.stats.getWordsCountStats(conv.messages, 200))

    #featuresets = [(messageFeatures(m, wordFeature), c) for (m,c) in messages]
    featuresets = [(messageFeatures(m, wordFeature), c) for (m,c) in messages]
    train_set, test_set = featuresets[100:], featuresets[:100]
    classifier = nltk.NaiveBayesClassifier.train(train_set)

    print(nltk.classify.accuracy(classifier, test_set))
    classifier.show_most_informative_features(5)

def messageFeatures(message, wordFeature):
    features = {}
    for word in wordFeature:
        features['contains({})'.format(word)] = (word in message)
    return features

def messageFeatures(message, wordFeature):
    features = {}
    for num in [0, 10, 20, 50, 100, 1000]:
        features['contains({})'.format(num)] = (sum(1 for c in message if c.isupper()) > num)
    return features