import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

from util import statsUtil

class WordsCountStats:
    def __init__(self, conversation):
        self.conversation = conversation
        self.msgs = self.conversation.messages
        self.wordsCount = None

    def loadWordsCount(self, groupByColumns=None, ngram_range=(1,1)):
        """
        Generates dataframe with words count for each group-by entry and stores it internally.
        Successive calls on this method will overwrite the stored data with the new results.

        :param ngram_range: ngram to use for count vectorization
        :param groupByColumns: names of features to use to group messages
        :return: none. Results are stored internally
        """
        if not groupByColumns:
            groupByColumns = []
        groupByColumns = groupByColumns + ['sender']

        self.wordsCount = WordsCountStats._computeWordsCount(self.msgs, groupByColumns, ngram_range)

    def loadWordsCountFromFile(self, filepath, indexCols=None):
        """
        Load previously exported words count in this stats instance.
        :param indexCols: columns to set as index
        :param filepath: filepath of the csv words count file
        :return: none. words-count data is stored in this stats instance
        """
        self.wordsCount = pd.read_csv(filepath, index_col=indexCols)

    def getWordsCount(self, words=None, sender=None, stopWords=None):
        """
        Returns count for specified words.
        :param stopWords: words to ignore
        :param words: lookup words, if none return all present words
        :param sender: if specified, just consider words occurrences for such sender, otherwise consider all senders (total)
        :return: a wordsCount dataframe
        """
        if not stopWords: stopWords = []

        # if no words have been specified considering all present ones not in stopwords
        if not words:
            words = list(filter(lambda x : x not in stopWords, self.wordsCount.columns.values))
        # Consider only words that are present and not in stopwords
        else:
            words = list(filter(lambda x : ((x not in stopWords)and(x in words)),
                                self.wordsCount.columns.values))

        # If no word is present, return None
        if not words:
            return None

        count = WordsCountStats._transformWordsCountBasedOnSender(self.wordsCount[words], sender)

        return count

    def getWordsUsedJustBy(self, originSender, referenceSender):
        # collect words
        wordsCount = self.wordsCount.ix[:,(self.wordsCount.loc[referenceSender]==0)
                          &(self.wordsCount.loc[originSender]!=0)]

        #transpose to have sender count as columns, and words as rows
        words = wordsCount.transpose().rename(columns={'sender':'word'})\
                            .sort_values(originSender, ascending=False)

        return words

    def getWordFirstAndLastOccurences(self, word, sender=None):
        """
        Returns when word has been used (non-zero count) for the first and last time.
        :param word: target word
        :param sender: if specified, just consider words used by such sender, otherwise consider all senders
        :return: two indexes, for which word firstly and lastly appears, or -1 if the word has never been used
        """
        res = WordsCountStats._getFirstAndLastOccurences(self.wordsCount, word, sender)
        if not res:
            return -1, -1
        else:
            return res

    #TODO add total option
    def getLexicalStats(self, sender=None):
        wordsCount = self.wordsCount
        #wordsCount = WordsCountStats._transformWordsCountBasedOnSender(self.wordsCount, sender)
        res = pd.DataFrame(wordsCount.apply(lambda x : WordsCountStats.lexicalStatsFun(x), axis=1))
        if sender:
            if isinstance(res.index, pd.core.index.MultiIndex):
                res = res.xs(sender, level='sender')
            else:
                res = res.loc[sender]
        return res

    @staticmethod
    # TODO Add options of filter out stopwords
    def _computeWordsCount(msgs, groupByColumns, ngram_range=(1,1)):
        """
        Generates dataframe with words count for each group-by entry.
        Grouping is done on passed columns plus the sender one.
        """
        # Group messages by sender and specified feature, concatenating text field
        grouped_msgs = msgs.groupby(groupByColumns).agg({'text': lambda x: " ".join(x)})

        # Count-vectorize msgs, using own defined analyzer (tokenizer)
        vectorizer = CountVectorizer(tokenizer=lambda x: statsUtil.getWords(x),
                                     ngram_range=ngram_range)
        X = vectorizer.fit_transform(grouped_msgs['text'].values)

        # Create count matrix using words as columns
        countMatrix = pd.DataFrame(X.toarray(), index=grouped_msgs.index,columns=vectorizer.get_feature_names())

        # Join data while dropping text column
        wordsCount = grouped_msgs.drop('text', axis=1).join(countMatrix)

        return wordsCount

    @staticmethod
    def _getFirstAndLastOccurences(wordsCount, word, sender=None):
        """
        Returns when word has been used (non-zero count) for the first and last time, based on the provided words counts.
        :param wordsCount: dataframe with words count for each group-by entry.
        :param word: target word
        :param sender: if specified, just consider words used by such sender, otherwise consider all senders
        :return: tuple with wordsCount indexes for which word firstly and lastly appears, or none if the word has never been used
        """
        # If word not present return -1
        if word not in wordsCount.columns:
            return None

        wordsCount = WordsCountStats._transformWordsCountBasedOnSender(wordsCount, sender)
        # (notice word column will still be present, even if sender never used it)
        count = wordsCount[word]

        # Being a series nonzero return always a tuple with just one array
        # collect it and return df indexes using first and last elements of the array, or -1 if array is empty
        nonZeroIdxs = count.nonzero()[0]
        if len(nonZeroIdxs) == 0:
            return None
        else:
            return wordsCount.index[nonZeroIdxs[0]], wordsCount.index[nonZeroIdxs[-1]]

    @staticmethod
    def _transformWordsCountBasedOnSender(wordsCount, sender=None):
        """
        Transforms wordsCount. If sender extract data only for specified sender, if not sum over all senders.
        Sender is check both on single and multi-index, if not present None is returned
        """
        # If sender, get words count for the specified sender
        if sender:
            try:
                if isinstance(wordsCount.index, pd.core.index.MultiIndex):
                    res = wordsCount.xs(sender, level='sender')
                else:
                    res = wordsCount.loc[sender]
            except KeyError:
                print("Key error for " + sender)
                return None
        # If no sender is specified, regroup by index (ignoring sender) and aggregate by sum
        else:
            indexNames = list(wordsCount.index.names)
            indexNames.remove('sender')
            # If only index was sender, we simply sum
            if not indexNames:
                res = wordsCount.sum()
            # Otherwise we sum by other indexes
            else:
                res = wordsCount.groupby(level=indexNames).sum()

        return res

    @staticmethod
    def _normalizeWordsCount(wordsCount):
        df = wordsCount.apply(lambda x : x/sum(x), axis=0)
        return df

    @staticmethod
    def _computeWordsTrend(wordsCount, sender=None):
        wordsCount = WordsCountStats._transformWordsCountBasedOnSender(wordsCount, sender)
        wordsTrend = wordsCount.apply(lambda x: (x - x.shift(1))).dropna().astype(np.int8)

        return wordsTrend

    @staticmethod
    def lexicalStatsFun(row):
        tokensCount = sum(row)
        vocabularyCount = len(row[row>0])
        return pd.Series({'tokensCount':tokensCount,'vocabularyCount':vocabularyCount,
                'lexicalRichness':vocabularyCount/tokensCount})

