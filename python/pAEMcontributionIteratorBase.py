## @package pAEMcontributionIteratorBase
## @brief Package defining the functions for iterating over the ACD
#  event contribution.

import logging
import LDF

from copy import copy

## @brief Base Class for the ACD contribution iterator

class pAEMcontributionIteratorBase(LDF.AEMcontributionIterator):

    ## @brief Constructor.
    ## @param self
    #  The class instance.
    ## @param event
    #  The event object.
    ## @param contribution
    #  The contribution object.
    ## @param treeMaker
    #  The pRootTreeMaker object responsible for the creation of the ROOT tree.
    ## @param errorCounter
    #  The pEventErrorCounter object responsible for managing the errors.
    
    def __init__(self, event, contribution, treeMaker, errorCounter):

        ## @var TreeMaker
        ## @brief The pRootTreeMaker object responsible for the creation
        #  of the ROOT tree.

        ## @var ErrorCounter
        ## @brief The pEventErrorCounter object responsible for
        #  managing the errors.
        
        LDF.AEMcontributionIterator.__init__(self, event, contribution)
        self.TreeMaker    = treeMaker
        self.ErrorCounter = errorCounter

    ## @brief Function included by default by the corresponding method
    #  of the derived iterator (the one which is actually run).
    
    def header(self, cable, header):
        pass
    
    ## @brief Function included by default by the corresponding method
    #  of the derived iterator (the one which is actually run).
    
    def pha(self, cable, channel, pha):
        pass

    ## @brief Fill acd_tile_count tree branch.
    ## @param self
    #  The class instance.
    ## @param cable
    #  The tile cable id.
    ## @param channel
    #  The tile channel id.
    ## @param pha
    #  The tile pulse height.

    def acd_tile_count__pha__(self, cable, channel, pha):
	self.TreeMaker.getVariable('acd_tile_count')[0] += 1

    ## @brief Fill acd_tile_hitmap tree branch.
    ## @param self
    #  The class instance.
    ## @param cable
    #  The tile cable id.
    ## @param header
    #  The contribution header.
   
    def acd_tile_hitmap__header__(self, cable, header):
	self.TreeMaker.getVariable('acd_tile_hitmap')[0] = header.hitMap()

    ## @brief Fill acd_cable_tile_count tree branch.
    ## @param self
    #  The class instance.
    ## @param cable
    #  The tile cable id.
    ## @param channel
    #  The tile channel id.
    ## @param pha
    #  The tile pulse height.

    def acd_cable_tile_count__pha__(self, cable, channel, pha):
	self.TreeMaker.getVariable('acd_cable_tile_count')[cable] += 1

