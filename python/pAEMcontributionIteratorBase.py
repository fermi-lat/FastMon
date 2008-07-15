## @package pAEMcontributionIteratorBase
## @brief Package defining the functions for iterating over the ACD
#  event contribution.

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
    ## @param errorHandler
    #  The pErrorHandler object responsible for managing the errors.
    
    def __init__(self, event, contribution, treeMaker, errorHandler):

        ## @var TreeMaker
        ## @brief The pRootTreeMaker object responsible for the creation
        #  of the ROOT tree.

        ## @var ErrorHandler
        ## @brief The pEventErrorHandler object responsible for
        #  managing the errors.
        
        LDF.AEMcontributionIterator.__init__(self, event, contribution)
        self.TreeMaker    = treeMaker
        self.ErrorHandler = errorHandler

    def populateAcceptList(self, header):
        self.AcceptList = []
        acceptMap = header.acceptMap()
        for i in range(18):
            if (acceptMap >> i) & 0x1:
                self.AcceptList.append(17 - i)

    ## @brief Function included by default by the corresponding method
    #  of the derived iterator (the one which is actually run). 
    
    def header(self, cable, header):
        if header.parityError():
            self.ErrorHandler.fill('ACD_HEADER_PARITY_ERROR', [cable])
        self.populateAcceptList(header)
    
    ## @brief Function included by default by the corresponding method
    #  of the derived iterator (the one which is actually run).
    
    def pha(self, cable, channel, pha):
        if channel not in self.AcceptList:
            self.ErrorHandler.fill('ACD_PHA_INCONSISTENCY',\
                                   [cable, channel, self.AcceptList])
        if pha.parityError():
            self.ErrorHandler.fill('ACD_PHA_PARITY_ERROR', [cable, channel])

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

    ## @brief Fill AcdHitChannel tree branch [12,18].
    ## @param self
    #  The class instance.
    ## @param cable
    #  The tile cable id.
    ## @param channel
    #  The tile channel id.
    ## @param pha
    #  The tile pulse height.

    def AcdHitChannel__pha__(self, cable, channel, pha):
	self.TreeMaker.getVariable('AcdHitChannel')[cable][channel] += 1

