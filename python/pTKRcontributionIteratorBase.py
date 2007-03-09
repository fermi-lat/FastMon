
import logging
import LDF

from copy import copy

class pTKRcontributionIteratorBase(LDF.TKRcontributionIterator):

    def __init__(self, event, contribution, treeMaker):
        LDF.TKRcontributionIterator.__init__(self, event, contribution)
        self.TemId     = LDF.LATPcellHeader.source(contribution.header())
        self.TreeMaker = treeMaker

    def iterate(self):
        self.iterateStrips()
        self.iterateTOTs()

    def getVariable(self, name):
        return self.TreeMaker.VariablesDictionary[name]
    
    def tkr_strip_count(self):
        self.getVariable("tkr_strip_count")[self.TemId] =\
                                                        copy(self.stripCount())

    def tkr_layer_strip_count__strip__(self, tower, layerEnd, hit):
        self.getVariable("tkr_layer_strip_count")[self.TemId][layerEnd/2] += 1

    def tkr_layer_tot__TOT__(self, tower, layerEnd, tot):
        self.getVariable("tkr_layer_tot")[self.TemId][layerEnd/2] = tot

