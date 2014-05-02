#!/usr/bin/env python
# -*- coding: latin-1 -*-

#------------------------------------------------------------------------------#
# Positive or negative text classifier with the Bayes method                   #
# ============================================================================ #
# Organization: HE-Arc Engineering                                             #
# Developer(s): Danick Fort                                                    #
#               Dany Jupille                                                   #
#                                                                              #
# Filename:     classifier.py                                                  #
# Description:  This is a simple Bayes classifier. The code in the global      #
#               section can be used for other modules purpose, when the main   #
#               section gives you a general idea of how to use this module.    #
# Version:      1.0                                                            #
#------------------------------------------------------------------------------#

#------------------------------------------------------------------------------#
#                                                                              #
# ------------------------------ GLOBAL SECTION ------------------------------ #
#                                                                              #
#------------------------------------------------------------------------------#

#------------------------------------------------------------------------------#
#                                                                              #
#                               LIBRARIES IMPORT                               #
#                                                                              #
#------------------------------------------------------------------------------#

import os
import random
import re
import string
import sys

from collections import defaultdict
from math import log

#------------------------------------------------------------------------------#
#                                                                              #
#                                   CLASSES                                    #
#                                                                              #
#------------------------------------------------------------------------------#

class BayesClass(object):
    """
    BayesClass objects are used by BayesClassifier objects. Their purpose is to
    represent a class of the Bayes classification method.
    """

    def __init__(self):
        """
        BayesClass default constructor.
        """
        self._nbWords = 0
        self._wordsDictionary = defaultdict(int)
        self._wordsDictionaryProbability = defaultdict(float)

    def addWord(self, word):
        """
        Add a word to the BayesClass. This will increase both the total amount
        of words and the amount of this single word.

        @param word: word to add.
        """
        self._nbWords += 1
        self._wordsDictionary[word] += 1

    def getNbWords(self):
        """
        Get the total amount of words of this BayesClass instance.

        @rtype: int
        @return: the amount of words.
        """
        return self._nbWords

    def getWordsDictionary(self):
        """
        Get the dictionary containing words occurrence of this BayesClass
        instance.

        @rtype: defaultdict(int)
        @return: the dictionary of words occurrence.
        """
        return self._wordsDictionary

    def getWordsDictionaryProbability(self):
        """
        Get the dictionary containing words apparition probability of this
        BayesClass instance.

        @rtype: defaultdict(float)
        @return: the dictionary of words apparition probability.
        """
        return self._wordsDictionaryProbability

class BayesClassifier(object):
    """
    BayesClassifer objects are used to do the classification of texts with the
    Bayes method. An instance of BayesClassifier can contain one or more
    BayesClass instances.
    """

    def __init__(self, filesTagged = False):
        """
        BayesClassifier default constructor.

        @param filesTagged: prepare this BayesClassifier to receive tagged texts
        if this argument is True; prepare it to receive untagged texts otherwise
        (default is False).
        """
        self._bayesClasses = {}
        self._ignoreList = set()
        self._vocabularyList = set()
        self._filesTagged = filesTagged

    def setFilesTagged(self, filesTagged):
        """
        Set the flag to tell the bayes classifier if it is working with tagged
        files.

        @param filesTagged: flag to tell if files are tagged or not.
        """
        self._filesTagged = filesTagged

    def addIgnoreListContent(self, filePath):
        """
        Add content to the ignore list. Words in the ignore list are not
        considered in the training or the classification.

        @param filePath: the file path of the ignore list content to add.
        """
        with open(filePath, encoding = 'utf-8') as file:
            for line in file:
                # Axiom: 1 line = 1 word
                self._ignoreList.add(line.strip())

    def emptyIgnoreList(self):
        """
        Empty the ignore list.
        """
        self._ignoreList = set()

    def addTrainingContent(self, className, filePath):
        """
        Add training content to the classifier. The more training it has, the
        more efficient it will be. Be aware that training content should be
        varied.

        @param className: the bayes class name.
        @param filePath: the file path of the training content to add.
        """
        if className not in self._bayesClasses:
            self._bayesClasses[className] = BayesClass()

        for word in generateFileIterator(filePath, self._filesTagged, self._ignoreList):
            self._bayesClasses[className].addWord(word)
            self._vocabularyList.add(word)

    def doTraining(self):
        """
        Train the classifier with the training content added before. You can
        always add training content after, but the bayes classifier will still
        use the old training as long as you didn't recall this method.
        """
        vocabularySize = len(self._vocabularyList)
        
        for word in self._vocabularyList:
            for bayesClass in self._bayesClasses.values():
                numerator = bayesClass.getWordsDictionary()[word] + 1
                denominator = bayesClass.getNbWords() + vocabularySize

                bayesClass.getWordsDictionaryProbability()[word] = log(float(numerator) / float(denominator))

    def emptyTraining(self):
        """
        Empty the training content and the training.
        """
        self._bayesClasses = {}
        self._vocabularyList = set()
        
    def classify(self, filePath):
        """
        Classify a file passed by his path. This will use the last training done
        with the doTraining method.
        """
        fileBayesClassProbability = defaultdict(float)
        
        for word in generateFileIterator(filePath, self._filesTagged, self._ignoreList):
            for bayesClassName, bayesClass in self._bayesClasses.items():
                fileBayesClassProbability[bayesClassName] += bayesClass.getWordsDictionaryProbability()[word]

        return max(fileBayesClassProbability, key = fileBayesClassProbability.get)

#------------------------------------------------------------------------------#
#                                                                              #
#                             UTILITIES FUNCTIONS                              #
#                                                                              #
#------------------------------------------------------------------------------#

def generateFileIterator(filePath, fileTagged, ignoreList = []):
    """
    Generate an iterator to get every important word in a file. A word is
    important when it is not a punctuation and not in the ignore list. In
    addition, when the file is tagged, it ignores names.

    @param filePath: the file path of the file to read.
    @param fileTagged: flag to tell if the file is tagged or not.
    @param ignoreList: list of words to ignore (default empty list).
    """
    if fileTagged:
        with open(filePath, encoding = 'utf-8') as file:
            for line in file:
                # Axiom: 1 line = 3 words separate by whitespace
                # Axiom: wordInfo[0] = original form
                # Axiom: wordInfo[1] = word type
                # Axiom: wordInfo[2] = primitive form
                wordInfo = line.strip().split()

                # Check axioms
                if len(wordInfo) == 3:
                    # Ignore words in ignore list, punctuation and names
                    if wordInfo[2] not in ignoreList and \
                       wordInfo[1] != 'PUN' and \
                       wordInfo[1] != 'SENT' and \
                       wordInfo[1] != 'NAM':
                        yield wordInfo[2]
    else:        
        with open(filePath, encoding = 'utf-8') as file:
            # Prepare a translation table for punctuation removal
            noPunctuationTranstable = str.maketrans('', '', string.punctuation)
            
            for line in file:
                # Remove punctuation
                line = line.translate(noPunctuationTranstable)

                # Split line into words array and remove whitespaces
                words = line.strip().split()
                
                for word in words:
                    # Ignore words in ignore list
                    if word not in ignoreList:
                        yield word.lower()

#------------------------------------------------------------------------------#
#                                                                              #
# ------------------------------- MAIN SECTION ------------------------------- #
#                                                                              #
#------------------------------------------------------------------------------#

# If this is the main module, run this
if __name__ == '__main__':

#------------------------------------------------------------------------------#
#                                                                              #
#                             UTILITIES FUNCTIONS                              #
#                                                                              #
#------------------------------------------------------------------------------#

    def doCrossValidation(classifier, positiveFilePathsList, negativeFilePathsList):
        for i in range(10):
            startSlice = int(len(positiveFilePathsList) * 0.1 * i)
            endSlice = int(len(positiveFilePathsList) * 0.1 * (i + 1))

            positiveFilePathsListForTesting = positiveFilePathsList[startSlice:endSlice]
            negativeFilePathsListForTesting = negativeFilePathsList[startSlice:endSlice]

            positiveFilePathsListForTraining = list(set(positiveFilePathsList) - set(positiveFilePathsListForTesting))
            negativeFilePathsListForTraining = list(set(negativeFilePathsList) - set(negativeFilePathsListForTesting))
        
            print('    -> STARTING TRAINING {0}...'.format(i + 1), end = '')
            for filePath in positiveFilePathsListForTraining:
                myClassifier.addTrainingContent('positive', filePath)

            for filePath in negativeFilePathsListForTraining:
                myClassifier.addTrainingContent('negative', filePath)

            myClassifier.doTraining()
            print(' DONE')

            print('    [CLASSIFICATION {0} STARTED]'.format(i + 1))
            positivesCount = 0
            positivesFound = 0
            
            negativesCount = 0
            negativesFound = 0

            for filePath in positiveFilePathsListForTesting:
                positivesCount += 1
                
                if myClassifier.classify(filePath) == 'positive':
                    positivesFound += 1

            for filePath in negativeFilePathsListForTesting:
                negativesCount += 1
                
                if myClassifier.classify(filePath) == 'negative':
                    negativesFound += 1

            print('      -> POSITIVES FOUND: {:.2%}'.format((float(positivesFound) / float(positivesCount))))
            print('      -> NEGATIVES FOUND: {:.2%}'.format((float(negativesFound) / float(negativesCount))))

            # Reset training
            myClassifier.emptyTraining()
            
            print('    [CLASSIFICATION {0} ENDED]'.format(i + 1))

#------------------------------------------------------------------------------#
#                                                                              #
#                                 INLINE CODE                                  #
#                                                                              #
#------------------------------------------------------------------------------#

    print('[APPLICATION STARTED]')

    print('  -> CREATING BAYES CLASSIFIER...', end = '')
    myClassifier = BayesClassifier(True)
    print(' DONE')

    print('  -> LOADING IGNORE-LIST...', end = '')
    myClassifier.addIgnoreListContent('ignore-list.txt')
    print(' DONE')

    print('  -> PREPARING TAGGED FILES...', end = '')
    positiveTaggedFilePathsList = [os.path.join('tagged-files/pos', filePath) for filePath in os.listdir('tagged-files/pos')]
    negativeTaggedFilePathsList = [os.path.join('tagged-files/neg', filePath) for filePath in os.listdir('tagged-files/neg')]
    print(' DONE')

    print('  -> PREPARING UNTAGGED FILES...', end = '')
    positiveUntaggedFilePathsList = [os.path.join('untagged-files/pos', filePath) for filePath in os.listdir('untagged-files/pos')]
    negativeUntaggedFilePathsList = [os.path.join('untagged-files/neg', filePath) for filePath in os.listdir('untagged-files/neg')]
    print(' DONE')

    print('  [CROSS-VALIDATION WITH ORDERED TAGGED FILES STARTED]')
    doCrossValidation(myClassifier, positiveTaggedFilePathsList, negativeTaggedFilePathsList)
    print('  [CROSS-VALIDATION WITH ORDERED TAGGED FILES ENDED]')

    # Next files are untagged
    myClassifier.setFilesTagged(False)

    print('  [CROSS-VALIDATION WITH ORDERED UNTAGGED FILES STARTED]')
    doCrossValidation(myClassifier, positiveUntaggedFilePathsList, negativeUntaggedFilePathsList)
    print('  [CROSS-VALIDATION WITH ORDERED UNTAGGED FILES ENDED]')

    # Next files are tagged
    myClassifier.setFilesTagged(True)

    # Shuffle files paths for random cross-validation
    random.shuffle(positiveTaggedFilePathsList)
    random.shuffle(negativeTaggedFilePathsList)
    random.shuffle(positiveUntaggedFilePathsList)
    random.shuffle(negativeUntaggedFilePathsList)

    print('  [CROSS-VALIDATION WITH RANDOM TAGGED FILES STARTED]')
    doCrossValidation(myClassifier, positiveTaggedFilePathsList, negativeTaggedFilePathsList)
    print('  [CROSS-VALIDATION WITH RANDOM TAGGED FILES ENDED]')

    # Next files are untagged
    myClassifier.setFilesTagged(False)

    print('  [CROSS-VALIDATION WITH RANDOM UNTAGGED FILES STARTED]')
    doCrossValidation(myClassifier, positiveUntaggedFilePathsList, negativeUntaggedFilePathsList)
    print('  [CROSS-VALIDATION WITH RANDOM UNTAGGED FILES ENDED]')

    print('[APPLICATION ENDED]')
