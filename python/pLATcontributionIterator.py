## @package pLATcontributionIterator
## @brief Package managing the interation over a LAT contribution.

import pSafeLogger
logger = pSafeLogger.getLogger('pLATcontributionIterator')

import LDF


## @brief Implementation of the LAT contribution iterator.

class pLATcontributionIterator(LDF.LDBI_LATcontributionIterator):

    ## @brief Constructor.
    ## @param self
    #  The class instance.
    ## @param ebfEventIterator
    #  The EBF event iterator object.

    def __init__(self, ebfEventIterator):
        LDF.LDBI_LATcontributionIterator.__init__(self, ebfEventIterator)

    ## @brief Handle LAT contribution iterator errors.
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

    def handleError(self, contribution, code, p1, p2):

        if code == LDF.LATcontributionIterator.ERR_UDFcontribution:
            logger.debug('handleError:ERR_UDFcontribution\n'\
	                 '\tFound unrecognized LATdatagram contribution type 0x%08X' % p1 )
            self.ErrorHandler.fill('LAT_CONTRIB_ERROR', ['Unrecognized Contribution', p1])
	    	     
        elif code == LDF.LATcontributionIterator.ERR_NotProgressing:
            logger.debug('handleError:ERR_UDFcontribution\n'\
	                 '\tIteration is not making progress\n'\
                         '\tParser may be lost\n')
            self.ErrorHandler.fill('LAT_CONTRIB_ERROR', ['Not Progressing'])
	    
        else:
    	    logger.debug("UNKNOWN_ERROR\n"\
                         "\tUnrecognized error code %d = 0x%08x with "\
                         "\targuments %d = 0x%08x, %d = 0x%08x\n" %\
                         (code, code, p1, p1, p2, p2))
            self.ErrorHandler.fill('LAT_CONTRIB_ERROR', ['UNKNOWN_ERROR_CODE', p1, p2])
			  
        return code
