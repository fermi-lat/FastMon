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
    
    ## @brief Fill cal_log_count tree branch
    ## Number of logs hit in the LAT
    ## @param self
    #  The class instance.

    def cal_log_count(self):
        self.getVariable("cal_log_count")[0] += copy(self.contribution().numLogAccepts())

    ## @brief Fill cal_tower_log_count tree branch
    ## Number of logs hit in each tower of the LAT
    ## @param self
    #  The class instance.

    def cal_tower_log_count(self):
        self.getVariable("cal_tower_log_count")[self.TemId] = copy(self.contribution().numLogAccepts())

    ## @brief Fill cal_layer_log_count tree branch
    ## Number of logs hit per layer for each tower of the LAT
    ## @param self
    #  The class instance.

    def cal_layer_log_count__log__(self, tower, layer, calLog):
        self.getVariable("cal_layer_log_count")[tower][layer] += 1

    ## @brief Fill cal_layer_column_log_count tree branch
    ## Number of logs hit per column per layer for each tower of the LAT
    ## @param self
    #  The class instance.

    def cal_layer_column_log_count__log__(self, tower, layer, calLog):
        self.getVariable("cal_hit_map")[tower][layer][calLog.column()]  = 1


    ## @brief Fill cal_tower_count tree branch
    ## Number of calorimeters with at least one log hit
    ## @param self
    #  The class instance.

    def cal_tower_count(self):
        if self.contribution().numLogAccepts() > 0:
	    self.getVariable("cal_log_count")[0] += 1



