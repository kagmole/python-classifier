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
# Description:  #N/A                                                           #
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

    def __init__(self):
        self._nbWords = 0
        self._wordsDictionary = defaultdict(int)
        self._wordsDictionaryProbability = defaultdict(float)

    def addWord(self, word):
        self._nbWords += 1
        self._wordsDictionary[word] += 1

    def getNbWords(self):
        return self._nbWords

    def getWordsDictionary(self):
        return self._wordsDictionary

    def getWordsDictionaryProbability(self):
        return self._wordsDictionaryProbability

class BayesClassifier(object):

    def __init__(self, filesTagged = False):
        self._bayesClasses = {}
        self._ignoreList = set()
        self._vocabularyList = set()
        self._filesTagged = filesTagged

    def addIgnoreListContent(self, filePath):
        self._ignoreList = []
        
        with open(filePath, encoding = "utf-8") as file:
            for line in file:
                # Axiom: 1 line = 1 word
                self._ignoreList.append(line.strip())

    def emptyIgnoreList(self):
        self._ignoreList = set()

    def addTrainingContent(self, className, filePath):
        if className not in self._bayesClasses:
            self._bayesClasses[className] = BayesClass()

        for word in generateTaggedFileIterator(filePath, self._filesTagged, self._ignoreList):
            self._bayesClasses[className].addWord(word)
            self._vocabularyList.add(word)

    def doTraining(self):
        vocabularySize = len(self._vocabularyList)
        
        for word in self._vocabularyList:
            for bayesClass in self._bayesClasses.values():
                numerator = bayesClass.getWordsDictionary()[word] + 1
                denominator = bayesClass.getNbWords() + vocabularySize

                bayesClass.getWordsDictionaryProbability()[word] = log(float(numerator) / float(denominator))

    def emptyTraining(self):
        self._bayesClasses = {}
        self._vocabularyList = set()
        
    def classify(self, filePath):
        fileBayesClassProbability = defaultdict(float)
        
        for word in generateTaggedFileIterator(filePath, self._filesTagged, self._ignoreList):
            for bayesClassName, bayesClass in self._bayesClasses.items():
                fileBayesClassProbability[bayesClassName] += bayesClass.getWordsDictionaryProbability()[word]

        return max(fileBayesClassProbability, key = fileBayesClassProbability.get)

#------------------------------------------------------------------------------#
#                                                                              #
#                             UTILITIES FUNCTIONS                              #
#                                                                              #
#------------------------------------------------------------------------------#

def generateTaggedFileIterator(filePath, filesTagged, ignoreList = []):
    if filesTagged:
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
                    yield word

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

    def crossValidation(positiveFilePathsList, negativeFilePathsList):
        successes = []

        for i in range(0,10):
            myClassifier = BayesClassifier(True)
            myClassifier.addIgnoreListContent('ignore-list.txt')

            random.shuffle(positiveFilePathsList)
            random.shuffle(negativeFilePathsList)

            startSlice = int(len(positiveFilePathsList) * 0.1 * i)
            endSlice = int(len(positiveFilePathsList) * 0.1 * (i+1))
            print(startSlice, endSlice)

            positiveFilePathsListForTesting = positiveFilePathsList[startSlice:endSlice]
            negativeFilePathsListForTesting = negativeFilePathsList[startSlice:endSlice]

            positiveFilePathsListForTraining = list(set(positiveFilePathsList) - set(positiveFilePathsListForTesting))
            negativeFilePathsListForTraining = list(set(negativeFilePathsList) - set(negativeFilePathsListForTesting))

            for filePath in positiveFilePathsListForTraining:
                myClassifier.addTrainingContent('positive', filePath)

            for filePath in negativeFilePathsListForTraining:
                myClassifier.addTrainingContent('negative', filePath)

            myClassifier.doTraining()

            positivesCount = 0
            positivesFound = 0
            
            negativesCount = 0
            negativesFound = 0
            
            for filePath in positiveFilePathsListForTesting:
                classificationResult = myClassifier.classify(filePath)

                positivesCount += 1
                
                if classificationResult == 'positive':
                    positivesFound += 1

                #print('-> "{0}" SHOULD BE "positive", GOT "{1}"'.format(filePath, classificationResult))

            for filePath in negativeFilePathsListForTesting:
                classificationResult = myClassifier.classify(filePath)

                negativesCount += 1
                
                if classificationResult == 'negative':
                    negativesFound += 1

                #print('-> "{0}" SHOULD BE "negative", GOT "{1}"'.format(filePath, classificationResult))

            print(str(i) + '-> Positives found: {:.2%}'.format((positivesFound / positivesCount)))
            print(str(i) + '-> Negatives found: {:.2%}'.format((negativesFound / negativesCount)))
            successes.append((float(positivesFound / positivesCount) + float(negativesFound / negativesCount))/2)
        print (sum(successes)/float(len(successes)))
        return sum(successes)/float(len(successes))


#------------------------------------------------------------------------------#
#                                                                              #
#                                    #NAME?                                    #
#                                                                              #
#------------------------------------------------------------------------------#

    print('[APPLICATION STARTED]')

    print('-> CREATING BAYES CLASSIFIER...', end = '')
    myClassifier = BayesClassifier(True)
    print('DONE')

    print('-> LOADING IGNORE-LIST...', end = '')
    myClassifier.addIgnoreListContent('ignore-list.txt')
    print('DONE')

    print('-> CHOOSING TRAINING AND TESTING FILES...', end = '')
    positiveFilePathsList = [os.path.join('tagged-files/pos', filePath) for filePath in os.listdir('tagged-files/pos')]
    negativeFilePathsList = [os.path.join('tagged-files/neg', filePath) for filePath in os.listdir('tagged-files/neg')]

    crossValidation(positiveFilePathsList, negativeFilePathsList)

    random.shuffle(positiveFilePathsList)
    random.shuffle(negativeFilePathsList)

    positiveFilePathsListForTraining = positiveFilePathsList[:int(len(positiveFilePathsList) * 0.8)]
    negativeFilePathsListForTraining = negativeFilePathsList[:int(len(negativeFilePathsList) * 0.8)]

    positiveFilePathsListForTesting = list(set(positiveFilePathsList) - set(positiveFilePathsListForTraining))
    negativeFilePathsListForTesting = list(set(negativeFilePathsList) - set(negativeFilePathsListForTraining))
    print('DONE')

    print('-> STARTING TRAINING...', end = '')
    for filePath in positiveFilePathsListForTraining:
        myClassifier.addTrainingContent('positive', filePath)

    for filePath in negativeFilePathsListForTraining:
        myClassifier.addTrainingContent('negative', filePath)

    myClassifier.doTraining()
    print('DONE')

    print('[CLASSIFICATION STARTED]')

    positivesCount = 0
    positivesFound = 0
    
    negativesCount = 0
    negativesFound = 0
    
    for filePath in positiveFilePathsListForTesting:
        classificationResult = myClassifier.classify(filePath)

        positivesCount += 1
        
        if classificationResult == 'positive':
            positivesFound += 1

        #print('-> "{0}" SHOULD BE "positive", GOT "{1}"'.format(filePath, classificationResult))

    for filePath in negativeFilePathsListForTesting:
        classificationResult = myClassifier.classify(filePath)

        negativesCount += 1
        
        if classificationResult == 'negative':
            negativesFound += 1

        #print('-> "{0}" SHOULD BE "negative", GOT "{1}"'.format(filePath, classificationResult))
        
    print('[CLASSIFICATION ENDED]')

    print('-> Positives found: {:.2%}'.format((positivesFound / positivesCount)))
    print('-> Negatives found: {:.2%}'.format((negativesFound / negativesCount)))

    print('[APPLICATION ENDED]')
