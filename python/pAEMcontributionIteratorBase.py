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

    def acd_tile_count__pha__(self, cable, channel, pha):
	self.getVariable('acd_tile_count')[0] += 1
   
