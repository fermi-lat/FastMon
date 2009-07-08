## @package pTKRcontributionIteratorBase
## @brief Package defining the functions for iterating over the TKR event
#  contribution.

import LDF

from copy      import copy
from pGlobals  import *


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
    ## @param errorHandler
    #  The pErrorHandler object responsible for managing the errors.

    def __init__(self, event, contribution, treeMaker, errorHandler):

        ## @var TemId
        ## @brief The TEM number.

        ## @var TreeMaker
        ## @brief The pRootTreeMaker object.

        ## @var ErrorHandler
        ## @brief The pErrorHandler object responsible for
        #  managing the errors.
        
        LDF.TKRcontributionIterator.__init__(self, event, contribution)
        self.TemId        = LDF.LATPcellHeader.source(contribution.header())
        self.TreeMaker    = treeMaker
        self.ErrorHandler = errorHandler

    ## @brief Iterate over the event contribution.
    ## @param self
    #  The class instance.

    def iterate(self):
        self.iterateStrips()
        self.iterateTOTs()

    ## @brief Function included by default by the corresponding method
    #  of the derived iterator (the one which is actually run).

    def strip(self, tower, layerEnd, hit):
        pass

    ## @brief Function included by default by the corresponding method
    #  of the derived iterator (the one which is actually run).
        
    def TOT(self, tower, layerEnd, tot):
        pass

    ## @brief Function filling the TkrHits variable.
    ## @param self
    #  The class instance.
    
    def TkrHits(self):
        self.TreeMaker.getVariable("TkrHits")\
                        [0] += copy(self.stripCount())

    ## @brief Function filling the TkrHitsTower variable.
    ## @param self
    #  The class instance.
    
    def TkrHitsTower(self):
        self.TreeMaker.getVariable("TkrHitsTower")\
                        [self.TemId] = copy(self.stripCount())

    ## @brief Function filling the TkrHitsTowerPlaneEnd variable in the
    #  strip() iterator method.
    ## @param self
    #  The class instance.
    ## @param tower
    #  The TEM id (0 to 15).
    ## @param layerEnd
    #  The TKR layer end id (0 to 71). 
    ## @param hit
    #  The TKR strip id.
    
    def TkrHitsTowerPlaneEnd__strip__(self, tower, layerEnd, hit):
        try:
            self.TreeMaker.getVariable("TkrHitsTowerPlaneEnd")\
                 [self.TemId][layerEnd/2][layerEnd%2] += 1
        except IndexError:
            pass

    ## @brief Function filling the TkrHitsGTFE variable in the
    #  strip() iterator method.
    ## @param self
    #  The class instance.
    ## @param tower
    #  The TEM id (0 to 15).
    ## @param layerEnd
    #  The TKR layer end id (0 to 71). 
    ## @param hit
    #  The TKR strip id.
    
    def TkrHitsGTFE__strip__(self, tower, layerEnd, hit):
        try:
            self.TreeMaker.getVariable("TkrHitsGTFE")\
                        [self.TemId][layerEnd/2][hit/64] += 1
        except IndexError:
            pass

    ## @brief Function filling the ToT_con0_TowerPlane variable in the
    #  TOT() iterator method.
    ## @param self
    #  The class instance.
    ## @param tower
    #  The TEM id (0 to 15).
    ## @param layerEnd
    #  The TKR layer end id (0 to 71). 
    ## @param tot
    #  The value of the TOT for the specified layer.

    def ToT_con0_TowerPlane__TOT__(self, tower, layerEnd, tot):
        if layerEnd%2 == 0:
            try:
                self.TreeMaker.getVariable("ToT_con0_TowerPlane")\
                        [self.TemId][layerEnd/2]= copy(tot)
            except IndexError:
                pass

    ## @brief Function filling the ToT_con1_TowerPlane variable in the
    #  TOT() iterator method.
    ## @param self
    #  The class instance.
    ## @param tower
    #  The TEM id (0 to 15).
    ## @param layerEnd
    #  The TKR layer end id (0 to 71). 
    ## @param tot
    #  The value of the TOT for the specified layer.

    def ToT_con1_TowerPlane__TOT__(self, tower, layerEnd, tot):
        if layerEnd%2 == 1:
            try:
                self.TreeMaker.getVariable("ToT_con1_TowerPlane")\
                        [self.TemId][layerEnd/2]= copy(tot)
            except IndexError:
                pass
        
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
        try:
            self.TreeMaker.getVariable("tkr_layer_end_tot")\
                        [self.TemId][layerEnd/2][layerEnd%2] = copy(tot)
        except IndexError:
            pass
        
    ## @brief Function filling the TkrHitsTowerPlane variable in the
    #  strip() iterator method.
    ## @param self
    #  The class instance.
    ## @param tower
    #  The TEM id (0 to 15).
    ## @param layerEnd
    #  The TKR layer end id (0 to 71). 
    ## @param hit
    #  The TKR strip id.
    def TkrHitsTowerPlane__strip__(self, tower, layerEnd, hit):
        try:
            self.TreeMaker.getVariable("TkrHitsTowerPlane")\
                        [self.TemId][layerEnd/2] += 1
        except IndexError:
            pass
