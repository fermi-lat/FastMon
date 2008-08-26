## @package pLATdatagramIterator
## @brief Package managing the interation over LAT datagrams.

import pSafeLogger
logger = pSafeLogger.getLogger('pLATdatagramIterator')

import LDF
from pGlobals  import *


## @brief Implementation of the LAT datagram iterator.

class pLATdatagramIterator(LDF.LDBI_LATdatagramIterator):

    ## @brief Constructor.
    ## @param self
    #  The class instance.
    ## @param latContributionIterator
    #  The LAT contribution iterator object.

    def __init__(self, latContributionIterator):

        ## @var __LatContributionIterator
        ## @brief The LAT contribution iterator object.
        
        LDF.LDBI_LATdatagramIterator.__init__(self, latContributionIterator)
        self.__LatContributionIterator = latContributionIterator

    ## @brief Handle error function overload
    ## @param self
    #  The class instance.
    ## @param contribution
    #  The contribution object.
    ## @param code
    #  The error code.
    ## @param p1
    #  Parameter 1.
    ## @param p2
    #  Parameter 2.
    #   
    ##  From Ric Claus
    #  
    #  The LookupErrorCode function is in Common/python/pGlobals
    #
    ##  return code is:
    #   - negative to indicate bail immediately
    #   - 0 for SUCCESS
    #   - positive to indicate that there was an error but iteration can continue
    #
    ## Error type 
    #  LATdatagramIterator.ERR_IDmismatch	Identity mismatch
    #  

    def handleError(self, contribution, code, p1, p2):
        s = LDF.LATdatagramIterator.handleError(self, contribution, code, p1,p2)
        errName = LookupErrorCode(self, code)[4:]
        self.ErrorHandler.fill('LAT_DATAGRAM_ERROR', [errName, p1, p2])
        return s

    ## @brief Process the datagram.
    ## @param self
    #  The class instance.
    ## @param datagram
    #  The datagram object.

    def process(self, datagram):
        self.__LatContributionIterator.iterate(datagram)
        status = self.__LatContributionIterator.status()
        if status:
            fn = 'pLATdatagramIterator.process()'
            logger.error('%s: iteration returned %d' % (fn, status))
        return 0
