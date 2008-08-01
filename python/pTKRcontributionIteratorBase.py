## @package pTKRcontributionIteratorBase
## @brief Package defining the functions for iterating over the TKR event
#  contribution.

import pSafeLogger
logger = pSafeLogger.getLogger('pTKRcontributionIteratorBase')

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


    ## @brief Handle error function overload
    #  Inspiration from the original c++ code implementation
    #  of the handleError function in "TKRcontributionIterator.cpp"
    #
    ##  return code is:
    #   - negative to indicate bail immediately
    #   - 0 for SUCCESS
    #   - positive to indicate that there was an error but iteration can continue
    #
    #	501 : 'ERR_WrongOrder'	    # TOTs cannot be accessed before strips have been iterated over
    #	502 : 'ERR_PastEnd'	    # Attempted to iterate past the end of the contribution.
    #	503 : 'ERR_UnphysStrip'     # Encountered an unphysical strip : StripMax = 1535
    #	504 : 'ERR_BadStripOrder'   # Out of order strip found
    #	505 : 'ERR_UnPhysTOT'       # Encountered an unphysical TOT : 251, 252, 253, 254
    #	506 : 'ERR_TooManyHits'     # Too many hits for GTRC size

    def handleError(self, event, code, p1, p2):

    	 if code == LDF.TKRcontributionIterator.ERR_WrongOrder:
             logger.debug("iterateTOTs:ERR_WrongOrder \n"\
                   	  "\tFor TEM %d contribution:\n"\
                   	  "\tTOTs cannot be accessed before "\
                   	  "\tstrips have been iterated over."%\
		          (self.TemId))
		   
	     self.ErrorHandler.fill('TKR_CONTRIB_ERROR', ['Cannot Access ToT before strips', self.TemId])
	     
    	 elif code == LDF.TKRcontributionIterator.ERR_PastEnd:
             which = ["Strips", "TOTs"]
             logger.debug("iterate%s:ERR_PastEnd \n"\
                          "\tFor TEM %d contribution:"\
                          "\tAttempted to iterate past the end of the contribution.\n"%\
                          (which[p1], self.TemId))
		   
	     self.ErrorHandler.fill('TKR_CONTRIB_ERROR', ['Past End', self.TemId, p1, p2])

    	 elif code == LDF.TKRcontributionIterator.ERR_UnphysStrip:
             logger.debug("iterateStrips:ERR_UnphysStrip \n"\
                          "\tFor TEM %d contribution:\n"\
                          "\tEncountered an unphysical strip # (%d).\n"\
                          "\Rest of contribution (TKR, DIAG, ERR) is uniterable due\n"\
                          "\tto the TEM firmware bug." % (self.TemId, p1))
		   
	     self.ErrorHandler.fill('TEM_BUG', ['Unphysical strip', self.TemId, p1])

    	 elif code == LDF.TKRcontributionIterator.ERR_UnphysTOT:
             logger.debug("iterateTOTs:ERR_UnphysTOT \n"\
                   	  "\tFor TEM %d, contribution:\n"\
                   	  "\tEncountered an unphysical TOT value # (%d).\n"\
                   	  "\tRest of contribution (TKR, DIAG, ERR) is uniterable due\n"\
                   	  "\tto the TEM firmware bug." % (self.TemId, p1))
		   
	     self.ErrorHandler.fill('TEM_BUG', ['Unphysical TOT', self.TemId, p1])

    	 elif code == LDF.TKRcontributionIterator.ERR_BadStripOrder:
             logger.debug("iterateStrips:ERR_BadStripOrder \n"\
                   	  "\tFor TEM %d contribution:\n"\
                   	  "\tOut of order strip found: %d is not > %d.\n"\
                   	  "\tRest of contribution (TKR, DIAG, ERR) is uniterable due\n"\
                   	  "\tto the TEM firmware bug."%\
		          (self.TemId, p1, p2))
		   
	     self.ErrorHandler.fill('TEM_BUG', ['Bad Strip Order',self.TemId, p1])

    	 elif code == LDF.TKRcontributionIterator.ERR_TooManyHits:
             logger.debug("iterateStrips:ERR_TooManyHits\n"\
                   	  "\tFor TEM %d contribution:\n"\
                   	  "\tMore hits found on layter-end %d than a GTRC can produce (%d).\n"\
                   	  "\tRest of contribution (TKR, DIAG, ERR) is uniterable due\n"\
                   	  "\tto the TEM firmware bug."%\
		   	  (self.TemId, p1, p2))
		   
	     self.ErrorHandler.fill('TEM_BUG', ['Too Many Hits in GTRC',self.TemId, p1, p2])

    	 else:
    	     logger.debug("UNKNOWN_ERROR\n"\
	                  "\tFor TEM %d contribution:\n"\
                          "\tUnrecognized error code %d = 0x%08x with "\
                          "\targuments %d = 0x%08x, %d = 0x%08x\n" %\
                          (self.TemId, code, code, p1, p1, p2, p2))

             self.ErrorHandler.fill('TKR_CONTRIB_ERROR', ['UNKNOWN_ERROR_CODE', self.TemId, p1, p2])
	     
    	 return code

    ## @brief Iterate over the event contribution.
    #  Iterate first over strips to check for unphysical strip ids
    #  From LDFdumper Tkr component iterator
    ## @param self
    #  The class instance.

    def iterate(self):
        rc     = self.iterateStrips()
        status = self.status()
        if status < 0:
	    return rc             # Exit Tkr contribution iterator on error
	
	# Do not try to read ToT if an error was found reading strip ids    	
        rc = self.iterateTOTs()
	return rc

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
        nstrips = self.stripCount()
        self.TreeMaker.getVariable("TkrHits")[0] += copy(nstrips)


    ## @brief Function filling the TkrHitsTower variable.
    #  Try/Except is probably not needed anymore
    ## @param self
    #  The class instance.
    
    def TkrHitsTower(self):
        try:
            self.TreeMaker.getVariable("TkrHitsTower")\
                        [self.TemId] = copy(self.stripCount())
        except:
	    logger.debug('Strip count too big %s' % self.stripCount())

    ## @brief Function filling the TkrHitsTowerPlaneEnd variable in the
    #  strip() iterator method.
    #  Try/Except is probably not needed anymore
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
    #  Try/Except is probably not needed anymore
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
    #  Try/Except is probably not needed anymore
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
    #  Try/Except is probably not needed anymore
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
    #  Try/Except is probably not needed anymore
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
    #  Try/Except is probably not needed anymore
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
