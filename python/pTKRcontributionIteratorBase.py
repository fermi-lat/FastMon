## @package pTKRcontributionIteratorBase
## @brief Package defining the functions for iterating over the TKR event
#  contribution.

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
    ## @param errorCounter
    #  The pEventErrorCounter object responsible for managing the errors.

    def __init__(self, event, contribution, treeMaker, errorCounter):

        ## @var TemId
        ## @brief The TEM number.

        ## @var TreeMaker
        ## @brief The pRootTreeMaker object.

        ## @var ErrorCounter
        ## @brief The pEventErrorCounter object responsible for
        #  managing the errors.
        
        LDF.TKRcontributionIterator.__init__(self, event, contribution)
        self.TemId          = LDF.LATPcellHeader.source(contribution.header())
        self.TreeMaker      = treeMaker
        self.ErrorCounter   = errorCounter

    ## @brief Iterate over the event contribution.
    ## @param self
    #  The class instance.

    def iterate(self):
        self.iterateStrips()
        self.iterateTOTs()

    ## @brief Function included by default by the corresponding method
    #  of the derived iterator (the one which is actually run).

    def strip(self, tower, layerEnd, hit):
        if hit < 0 or hit > 1535:
            self.ErrorCounter.fill('UNPHYSICAL_STRIP_ID',\
                                   [tower, layerEnd, hit])

    ## @brief Function included by default by the corresponding method
    #  of the derived iterator (the one which is actually run).
        
    def TOT(self, tower, layerEnd, tot):
        pass

    ## @brief Function filling the tkr_strip_count variable.
    ## @param self
    #  The class instance.
    
    def tkr_strip_count(self):
        self.TreeMaker.getVariable("tkr_strip_count")\
                        [0] += copy(self.stripCount())

    ## @brief Function filling the tkr_tower_strip_count variable.
    ## @param self
    #  The class instance.
    
    def tkr_tower_strip_count(self):
        self.TreeMaker.getVariable("tkr_tower_strip_count")\
                        [self.TemId] = copy(self.stripCount())

    ## @brief Function filling the tkr_layer_end_strip_count variable in the
    #  strip() iterator method.
    ## @param self
    #  The class instance.
    ## @param tower
    #  The TEM id (0 to 15).
    ## @param layerEnd
    #  The TKR layer end id (0 to 71). 
    ## @param hit
    #  The TKR strip id.
    
    def tkr_layer_end_strip_count__strip__(self, tower, layerEnd, hit):
        self.TreeMaker.getVariable("tkr_layer_end_strip_count")\
                        [self.TemId][layerEnd/2][layerEnd%2] += 1

    ## @brief Function filling the tkr_layer_end_tot variable in the
    #  TOT() iterator method.
    ## @param self
    #  The class instance.
    ## @param tower
    #  The TEM id (0 to 15).
    ## @param layerEnd
    #  The TKR layer end id (0 to 71). 
    ## @param tot
    #  The value of the TOT for the specified layer.

    def tkr_layer_end_tot__TOT__(self, tower, layerEnd, tot):
        self.TreeMaker.getVariable("tkr_layer_end_tot")\
                        [self.TemId][layerEnd/2][layerEnd%2] = copy(tot)

