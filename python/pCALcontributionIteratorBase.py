import logging
import LDF

from copy import copy

class pCALcontributionIteratorBase(LDF.CALcontributionIterator):

    def __init__(self, event, contribution, treeMaker):
        LDF.CALcontributionIterator.__init__(self, event, contribution)
        self.TemId = LDF.LATPcellHeader.source(contribution.header())
        self.TreeMaker = treeMaker

    def getVariable(self, name):
        return self.TreeMaker.VariablesDictionary[name]
    
    def cal_log_count(self):
        self.getVariable("cal_log_count")[self.TemId] = copy(self.contribution().numLogAccepts())
