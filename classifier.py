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
#                               LIBRARIES IMPORT                               #
#                                                                              #
#------------------------------------------------------------------------------#

import math
import sys

#------------------------------------------------------------------------------#
#                                                                              #
#                                   CLASSES                                    #
#                                                                              #
#------------------------------------------------------------------------------#

class Classifier(object):

    def __init__(self):
        self._ignoreList = list()

    def loadIgnoreList(self, filepath):
        with open(filepath) as file:
            for line in file:
                # Axiom: 1 line = 1 word
                self._ignoreList.append(line.strip())

    def classify(self, filepath):
        with open(filepath) as file:
            for line in file:
                # Axiom: 1 line = 3 words separate by whitespace
                # Axiom: the 3rd word is the primitive form of the 3 words
                word = line.split()[2]

                if word not in self._ignoreList:
                    pass
                #TODO

#------------------------------------------------------------------------------#
#                                                                              #
#                             UTILITIES FUNCTIONS                              #
#                                                                              #
#------------------------------------------------------------------------------#

# Nothin' :(

#------------------------------------------------------------------------------#
#                                                                              #
#                               "MAIN" FUNCTION                                #
#                                                                              #
#------------------------------------------------------------------------------#

# If this is the main module, run this
if __name__ == '__main__':

    myClassifier = Classifier()
    myClassifier.loadIgnoreList('frenchST.txt')

    print("IGNORE LIST")
    print (myClassifier._ignoreList)
