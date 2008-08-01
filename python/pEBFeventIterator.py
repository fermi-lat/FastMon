## @package pEBFeventIterator
## @brief Package managing the interation over EBF events.

import pSafeLogger
logger = pSafeLogger.getLogger('pEBFeventIterator')

import LDF


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

    ## @brief Handle EBF event iterator errors.
    ## @param self
    #  The class instance.
    ## @param event
    #  The event object.
    ## @param code
    #  The error code.
    ## @param p1
    #  Parameter 1.
    ## @param p2
    #  Parameter 2.

    def handleError(self, event, code, p1, p2):
        if code == LDF.EBFeventIterator.ERR_NonEBFevent:
            logger.debug("handleError:ERR_NonEBFevent \n"\
                	 "\tExpected an EBFevent TypeId, not 0x%08x\n" % p1)
		   
	    self.ErrorHandler.fill('EBF_EVENT_ERROR', ['Non EBF event', p1])

    	elif code == LDF.EBFeventIterator.ERR_BadStatus:
            logger.debug("handleError:ERR_BadStatus \n"\
                  	 "\tEvent has bad internal status %d = 0x%08x\n"\
                         "\tAborting processing of event\n" % (p1, p1))
		   
	    self.ErrorHandler.fill('EBF_EVENT_ERROR', ['Bad Status', p1])
	     
        else:
    	    logger.debug("UNKNOWN_ERROR\n"\
                         "\tUnrecognized error code %d = 0x%08x with "\
                         "\targuments %d = 0x%08x, %d = 0x%08x\n" %\
                         (code, code, p1, p1, p2, p2))
            self.ErrorHandler.fill('EBF_EVENT_ERROR', ['UNKNOWN_ERROR_CODE', p1, p2])

        return code


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
