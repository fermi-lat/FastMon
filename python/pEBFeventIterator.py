## @package pEBFeventIterator
## @brief Package managing the interation over EBF events.

import pSafeLogger
logger = pSafeLogger.getLogger('pEBFeventIterator')

import LDF
from pGlobals  import *


## @brief Implementation of the EBF event iterator.

class pEBFeventIterator(LDF.LDBI_EBFeventIterator):

    ## @brief Constructor.
    ## @param self
    #  The class instance.
    ## @param latComponentIterator
    #  The LAT component iterator object.

    def __init__(self, latComponentIterator):

        ## @var __LatComponentIterator
        ## @brief The LAT component iterator object.

        LDF.LDBI_EBFeventIterator.__init__(self, latComponentIterator)
        self.__LatComponentIterator = latComponentIterator

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
    #  ERR_NonEBFevent : Expected an EBFevent TypeIdI
    #  ERR_BadStatus   : Event has bad internal status
    #

    def handleError(self, event, code, p1, p2):
        s = LDF.EBFeventIterator.handleError(self, event, code, p1,p2)
        errName = LookupErrorCode(self, code)[4:]
        self.ErrorHandler.fill('EBF_EVENT_ERROR', [errName, p1, p2])
        return s

    ## @brief Process the event.
    ## @param self
    #  The class instance.
    ## @param evt
    #  The event object.
    
    def process(self, evt):
        if evt.status() != 0:
            fn = 'pEBFeventIterator.process()'
            logger.error('%s: bad status in event header.')
            return evt.status()
        else:
            self.__LatComponentIterator.iterate(evt)
            return self.__LatComponentIterator.status()
