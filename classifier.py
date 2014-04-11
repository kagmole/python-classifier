import os
import random
from collections import defaultdict
from math import log

negativeDict = defaultdict(int)
positiveDict = defaultdict(int)
positiveProbabilities = defaultdict(int)
negativeProbabilities = defaultdict(int)


def training(positiveList, negativeList, negativeFile, positiveFile):
	'''
	positiveFolder, negativeFolder -- (string) folders where positive and negative comments are
	positiveFile, negativeFile -- (string) filenames where the values of each word will be written
	'''

	nPositive = 0
	nNegative = 0

	for f in negativeList:
		file = open(f, 'r')

		for l in file:
			for w in l.split(" "):
				negativeDict[w.rstrip('\r\n')] += 1
				nNegative += 1

	for f in positiveList:
		file = open(f, 'r')

		for l in file:
			for w in l.split(" "):
				positiveDict[w.rstrip('\r\n')] += 1
				nPositive += 1

	# Used for calculating probabilities
	uniqueWordsList = set(positiveDict.keys()) | set(negativeDict.keys())
	vocabularySize = len(uniqueWordsList)

	# Iterating over all words.
	for k in list(uniqueWordsList):
		posNumerator = positiveDict[k] + 1 # Zero frequency problem solve
		print posNumerator,'\n','pn'
		posDenominator = nPositive + vocabularySize
		print posDenominator,'\n','pd'

		positiveProbabilities[k] = log(float(posNumerator)/float(posDenominator))

		negNumerator = negativeDict[k] + 1
		negDenominator = nNegative + vocabularySize

		negativeProbabilities[k] = log(float(negNumerator)/float(negDenominator))

baseDir = os.path.dirname(os.path.realpath(__file__))
positiveFiles = [os.path.join('pos', f) for f in os.listdir('pos')]
negativeFiles = [os.path.join('neg', f) for f in os.listdir('neg')]

random.shuffle(positiveFiles)
random.shuffle(negativeFiles)

positiveFilesForTraining = positiveFiles[:int(len(positiveFiles)*0.8)]
negativeFilesForTraining = negativeFiles[:int(len(negativeFiles)*0.8)]

positiveFilesForTesting = list(set(positiveFiles) - set(positiveFilesForTraining))
negativeFilesForTesting = list(set(negativeFiles) - set(negativeFilesForTraining))

training(positiveFilesForTraining, negativeFilesForTraining,'t','t')
#print(negativeDict)
#print(positiveDict)