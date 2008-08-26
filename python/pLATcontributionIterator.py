## @package pLATcontributionIterator
## @brief Package managing the interation over a LAT contribution.

import pSafeLogger
logger = pSafeLogger.getLogger('pLATcontributionIterator')

import LDF
from pGlobals  import *


## @brief Implementation of the LAT contribution iterator.

class pLATcontributionIterator(LDF.LDBI_LATcontributionIterator):

    ## @brief Constructor.
    ## @param self
    #  The class instance.
    ## @param ebfEventIterator
    #  The EBF event iterator object.

    def __init__(self, ebfEventIterator):
        LDF.LDBI_LATcontributionIterator.__init__(self, ebfEventIterator)


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
    ## Error type 
    #  ERR_UDFcontribution : Found unrecognized LATdatagram contribution
    #  ERR_NotProgressing   : Iteration is not making progress, Parser may be lost
    #

    def handleError(self, contribution, code, p1, p2):
        s = LDF.LATcontributionIterator.handleError(self, contribution, code, p1,p2)
        errName = LookupErrorCode(self, code)[4:]
        self.ErrorHandler.fill('LAT_CONTRIB_ERROR', [errName, p1, p2])
        return s

