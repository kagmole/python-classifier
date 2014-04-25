import os
import random
from collections import defaultdict
from math import log

negativeDict = defaultdict(int)
positiveDict = defaultdict(int)
positiveProbabilities = defaultdict(int)
negativeProbabilities = defaultdict(int)
ignoreList = []

def loadIgnoreList(filePath):
	ignoreList = []
	
	with open(filePath) as file:
		for line in file:
			# Axiom: 1 line = 1 word
			ignoreList.append(line.strip())

def generateTaggedFileIterator(filePath, ignoreList = []):
    with open(filePath, encoding = "utf-8") as file:
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
		posDenominator = nPositive + vocabularySize

		positiveProbabilities[k] = log(float(posNumerator)/float(posDenominator))

		negNumerator = negativeDict[k] + 1
		negDenominator = nNegative + vocabularySize

		negativeProbabilities[k] = log(float(negNumerator)/float(negDenominator))

def classify(positiveFilesForTesting, negativeFilesForTesting):

	classifiedNegativeFiles = defaultdict(bool)
	classifiedPositiveFiles = defaultdict(bool)

	for f in positiveFilesForTesting:
		file = open(f, 'r')

		fileIsNegative = float(1.0)
		fileIsPositive = float(1.0)

		for l in file:
			for w in l.split(" "):
				negProb = negativeDict[w.rstrip('\r\n')]
				posProb = positiveDict[w.rstrip('\r\n')]
				fileIsNegative *= 1 if negProb == 0 else negProb
				fileIsPositive *= 1 if posProb == 0 else posProb
		positive = fileIsPositive >= fileIsNegative
		positiveText = "positive" if positive else "negative"
		#print("file " + f + " is " + positiveText)

		classifiedPositiveFiles[f] = positive

	size = len([i for i in classifiedPositiveFiles.values() if i]) / float(len(positiveFilesForTesting))

	print("Succes avec les fichiers positif : " + str(size*100))

	for f in negativeFilesForTesting:
		file = open(f, 'r')

		fileIsNegative = 1.0
		fileIsPositive = 1.0

		for l in file:
			for w in l.split(" "):
				negProb = negativeDict[w.rstrip('\r\n')]
				posProb = positiveDict[w.rstrip('\r\n')]
				fileIsNegative *= 1 if negProb == 0 else negProb
				fileIsPositive *= 1 if posProb == 0 else posProb
		positive = fileIsPositive >= fileIsNegative
		positiveText = "positive" if positive else "negative"
		#print("file " + f + " is " + positiveText)
		classifiedNegativeFiles[f] = positive
	size = len([i for i in classifiedNegativeFiles.values() if not i]) / float(len(classifiedNegativeFiles))
	
	print("Succes avec les fichiers negatif : " + str(size*100))

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

classify(positiveFilesForTesting, negativeFilesForTesting)

#print(negativeDict)
#print(positiveDict)