import pSafeLogger
logger = pSafeLogger.getLogger('pCALcontributionIteratorBase')

import LDF

from copy import copy

## @brief Base Class for the CAL contribution iterator

class pCALcontributionIteratorBase(LDF.CALcontributionIterator):

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

        ## @var TemId
        ## @brief The TEM id for the contribution.

        ## @var TreeMaker
        ## @brief The pRootTreeMaker object responsible for the creation
        #  of the ROOT tree.

        ## @var ErrorHandler
        ## @brief The pErrorHandler object responsible for
        #  managing the errors.
        
        LDF.CALcontributionIterator.__init__(self, event, contribution)
        self.TemId        = LDF.LATPcellHeader.source(contribution.header())
        self.TreeMaker    = treeMaker
        self.ErrorHandler = errorHandler

    ## @brief Handle error function overload
    #  Inspiration from the original c++ code implementation
    #  of the handleError function in "CALcontributionIterator.cpp"
    #
    ##  return code is:
    #   - negative to indicate bail immediately
    #   - 0 for SUCCESS
    #   - positive to indicate that there was an error but iteration can continue
    #
    ## No error is expected to be found when parsing the CAL contribution ?
    def handleError(self, event, code, p1, p2):        	
    	logger.debug("UNKNOWN_ERROR\n"\
	             "\tFor TEM %d contribution:\n"\
                     "\tUnrecognized error code %d = 0x%08x with "\
                     "\targuments %d = 0x%08x, %d = 0x%08x\n" %\
                     (self.TemId, code, code, p1, p1, p2, p2))

        self.ErrorHandler.fill('CAL_CONTRIB_ERROR', ['UNKNOWN_ERROR_CODE', p1, p2])
    	return code


    ## @brief Function included by default by the corresponding method
    #  of the derived iterator (the one which is actually run).
        
    def log(self, tower, layer, calLog):
        pass
    
    ## @brief Fill CalXHit tree branch
    ## Number of logs hit in the LAT
    ## @param self
    #  The class instance.

    def CalXHit(self):
        self.TreeMaker.getVariable("CalXHit")[0] +=\
                       copy(self.contribution().numLogAccepts())

    ## @brief Fill CalXHit_Tower tree branch
    ## Number of logs hit in each tower of the LAT
    ## @param self
    #  The class instance.

    def CalXHit_Tower(self):
        self.TreeMaker.getVariable("CalXHit_Tower")[self.TemId] =\
                       copy(self.contribution().numLogAccepts())

    ## @brief Fill CalXHit_TowerCalLayer tree branch
    ## Number of logs iterator call per layer for each tower of the LAT
    ## @param self
    #  The class instance.
    ## @param tower
    #  The tower id.
    ## @param layer
    #  The CAL layer id.
    ## @param calLog
    #  The CAL log object.
    
    #def CalXHit_TowerCalLayer__log__(self, tower, layer, calLog):
    #    self.TreeMaker.getVariable("CalXHit_TowerCalLayer")[tower][layer] += 1

    ## @brief Fill CalXHit_TowerCalLayerCalColumn tree branch
    ## Number of logs hit per column per layer for each tower of the LAT
    ## @param self
    #  The class instance.
    ## @param tower
    #  The tower id.
    ## @param layer
    #  The CAL layer id.
    ## @param calLog
    #  The CAL log object.

    def CalXHit_TowerCalLayerCalColumn__log__(self, tower, layer, calLog):
        try:
            self.TreeMaker.getVariable("CalXHit_TowerCalLayerCalColumn")\
             [tower][layer][calLog.column()] = 1
        except IndexError:
            pass
        
    ## @brief Fill CalTowerCount tree branch
    ## Number of calorimeters with at least one log hit
    ## @param self
    #  The class instance.

    def CalTowerCount(self):
        if self.contribution().numLogAccepts() > 0:
	    self.TreeMaker.getVariable("CalTowerCount")[0] += 1


    def CalLogEndRangeHit__log__(self, tower, layer, calLog):
        calLogEnd = calLog.negative()
        if calLogEnd.value() > 0:
            try:
                self.TreeMaker.getVariable('CalLogEndRangeHit')\
                 [tower][layer][calLog.column()][0][calLogEnd.range()] = 1
            except IndexError:
                pass
        calLogEnd = calLog.positive()
        if calLogEnd.value() > 0:
            try:
                self.TreeMaker.getVariable('CalLogEndRangeHit')\
                 [tower][layer][calLog.column()][1][calLogEnd.range()] = 1   
            except IndexError:
                pass
