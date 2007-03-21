import logging
import LDF

from copy import copy

## @brief Base Class for the ACD contribution iterator

class pAEMcontributionIteratorBase(LDF.AEMcontributionIterator):

    def __init__(self, event, contribution, treeMaker):
        LDF.AEMcontributionIterator.__init__(self, event, contribution)
        self.TreeMaker = treeMaker

    def getVariable(self, name):
        return self.TreeMaker.VariablesDictionary[name]
    
