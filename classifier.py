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
	'''
	Loads global array ignoreList with words to ignore, from filePath

	@params(filePath) -- (string) The path of the file that contains the words to ignore, separated by a new line.
	@return void
	'''
	with open(filePath) as file:
		for line in file:
			# Axiom: 1 line = 1 word
			ignoreList.append(line.strip())

def generateTaggedFileIterator(filePath, ignoreList = []):
    with open(filePath) as file:
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

def training(positiveList, negativeList):
	'''
	Trains the Bayes classifier with all the files provided in the parameters.
	Fills global dictionaries positiveDict and negativeDict with probabilities for each word found in the files.

	@params(positiveList, negativeList) -- (array of string, array of string) Arrays with positive/negative file paths
	@return void
	'''

	nPositive = 0
	nNegative = 0

	for f in negativeList:
		for w in generateTaggedFileIterator(f, ignoreList):
			negativeDict[w] += 1
			nNegative += 1

	for f in positiveList:
		for w in generateTaggedFileIterator(f, ignoreList):
			positiveDict[w] += 1
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
	'''
	Classifies the files given in the parameters and returns the success rate of the classification for each class, positive and negative.

	@params(positiveFilesForTesting, negativeFilesForTesting) -- (array of string, array of string) Arrays with positive/negative file paths
	@return(int) -- The average success rate of the positive and negative classification
	'''
	classifiedNegativeFiles = defaultdict(bool)
	classifiedPositiveFiles = defaultdict(bool)

	for f in positiveFilesForTesting:
		file = open(f, 'r')

		fileIsNegative = float(1.0)
		fileIsPositive = float(1.0)

		for w in generateTaggedFileIterator(f, ignoreList):
			negProb = negativeDict[w]
			posProb = positiveDict[w]

			fileIsNegative *= 1 if negProb == 0 else negProb
			fileIsPositive *= 1 if posProb == 0 else posProb

		positive = fileIsPositive >= fileIsNegative
		positiveText = "positive" if positive else "negative"
		#print("file " + f + " is " + positiveText)

		classifiedPositiveFiles[f] = positive

	successRatePositive = len([i for i in classifiedPositiveFiles.values() if i]) / float(len(positiveFilesForTesting))

	print("Success with positive files : " + str(successRatePositive*100))

	for f in negativeFilesForTesting:
		file = open(f, 'r')

		fileIsNegative = 1.0
		fileIsPositive = 1.0

		for w in generateTaggedFileIterator(f, ignoreList):
			negProb = negativeDict[w]
			posProb = positiveDict[w]

			fileIsNegative *= 1 if negProb == 0 else negProb
			fileIsPositive *= 1 if posProb == 0 else posProb

		positive = fileIsPositive >= fileIsNegative
		positiveText = "positive" if positive else "negative"
		#print("file " + f + " is " + positiveText)
		
		classifiedNegativeFiles[f] = positive
	successRateNegative= len([i for i in classifiedNegativeFiles.values() if not i]) / float(len(classifiedNegativeFiles))
	
	print("Success with negative files : " + str(successRateNegative*100))

	return (successRatePositive + successRateNegative) / 2


baseDir = os.path.dirname(os.path.realpath(__file__))
positiveFiles = [os.path.join('tagged/pos', f) for f in os.listdir('tagged/pos')]
negativeFiles = [os.path.join('tagged/neg', f) for f in os.listdir('tagged/neg')]

random.shuffle(positiveFiles)
random.shuffle(negativeFiles)

positiveFilesForTraining = positiveFiles[:int(len(positiveFiles)*0.8)]
negativeFilesForTraining = negativeFiles[:int(len(negativeFiles)*0.8)]

positiveFilesForTesting = list(set(positiveFiles) - set(positiveFilesForTraining))
negativeFilesForTesting = list(set(negativeFiles) - set(negativeFilesForTraining))

loadIgnoreList("frenchST.txt")

training(positiveFilesForTraining, negativeFilesForTraining)

success = classify(positiveFilesForTesting, negativeFilesForTesting)

print("The average success rate is : " + str(success*100))

#print(negativeDict)
#print(positiveDict)