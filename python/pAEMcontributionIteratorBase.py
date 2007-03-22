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
	#print cable, channel, pha.ADCrange(), pha.ADCvalue() 
	self.getVariable('acd_tile_count')[0] += 1
   
    def acd_tile_hitmap__header__(self, cable, header):
	#print cable, hex(header.hitMap())
	self.getVariable('acd_tile_hitmap')[0] = header.hitMap()

    def acd_cable_tile_count__pha__(self, cable, channel, pha):
	#print cable, channel, pha.ADCrange(), pha.ADCvalue() 
	self.getVariable('acd_cable_tile_count')[cable] += 1

