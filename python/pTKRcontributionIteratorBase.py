## @package pTKRcontributionIteratorBase
## @brief Package defining the functions for iterating over the TKR event
#  contribution.

import logging
import LDF

from copy import copy


## @brief Base TKR contribution iterator.

class pTKRcontributionIteratorBase(LDF.TKRcontributionIterator):

    ## @brief Contructor.
    ## @param self
    #  The class instance.
    ## @param event
    #  The event.
    ## @param contribution
    #  The contribution.
    ## @param treeMaker
    #  The pRootTreeMaker object responsible for managing the root tree.

    def __init__(self, event, contribution, treeMaker):

        ## @var TemId
        ## @brief The TEM number.

        ## @var TreeMaker
        ## @brief The pRootTreeMaker object.
        
        LDF.TKRcontributionIterator.__init__(self, event, contribution)
        self.TemId     = LDF.LATPcellHeader.source(contribution.header())
        self.TreeMaker = treeMaker

    ## @brief Iterate over the event contribution.
    ## @param self
    #  The class instance.

    def iterate(self):
        self.iterateStrips()
        self.iterateTOTs()

    ## @brief Return a variable from the pRootTreeMaker object.
    ## @todo Make a setVariable method in pRootTreeMaker and change all the
    #  iterators.
    ## @param self
    #  The class instance.
    ## @param name
    #  The variable name.

    def getVariable(self, name):
        return self.TreeMaker.VariablesDictionary[name]

    ## @brief Function filling the tkr_strip_count variable.
    ## @param self
    #  The class instance.
    
    def tkr_strip_count(self):
        self.getVariable("tkr_strip_count")[0] += copy(self.stripCount())

    ## @brief Function filling the tkr_tower_strip_count variable.
    ## @param self
    #  The class instance.
    
    def tkr_tower_strip_count(self):
        self.getVariable("tkr_tower_strip_count")[self.TemId] =\
                                          copy(self.stripCount())

    ## @brief Function filling the tkr_layer_end_strip_count variable in the
    #  strip() iterator method.
    ## @param self
    #  The class instance.

    def tkr_layer_end_strip_count__strip__(self, tower, layerEnd, hit):
        self.getVariable("tkr_layer_end_strip_count")[self.TemId][layerEnd/2][layerEnd%2] += 1

    ## @brief Function filling the tkr_layer_end_tot variable in the
    #  strip() iterator method.
    ## @param self
    #  The class instance.

    def tkr_layer_end_tot__TOT__(self, tower, layerEnd, tot):
        self.getVariable("tkr_layer_end_tot")[self.TemId][layerEnd/2][layerEnd%2] = tot

