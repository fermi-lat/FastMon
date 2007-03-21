import logging
import LDF

from copy import copy

## @brief Base Class for the CAL contribution iterator

class pCALcontributionIteratorBase(LDF.CALcontributionIterator):

    def __init__(self, event, contribution, treeMaker):
        LDF.CALcontributionIterator.__init__(self, event, contribution)
        self.TemId = LDF.LATPcellHeader.source(contribution.header())
        self.TreeMaker = treeMaker

    def getVariable(self, name):
        return self.TreeMaker.VariablesDictionary[name]
    
    def cal_log_count(self):
        self.getVariable("cal_log_count")[self.TemId] = copy(self.contribution().numLogAccepts())

    ## @brief Fill cal_tower_count tree branch
    ## cal_tower_count is the number of calorimeters with at least one log hit
    ## @param self
    #  The class instance.
    def cal_tower_count(self):
        if self.contribution().numLogAccepts() > 0:
	    self.getVariable("cal_tower_count")[0] += 1

    def cal_hit_map__log__(self, tower, layer, calLog):
        self.getVariable("cal_hit_map")[tower][layer][calLog.column()]  = 1
