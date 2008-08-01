## @package pLATdatagramIterator
## @brief Package managing the interation over LAT datagrams.

import pSafeLogger
logger = pSafeLogger.getLogger('pLATdatagramIterator')

import LDF


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

    ## @brief Handle datagram errors.
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
        if code == LDF.LATdatagramIterator.ERR_IDmismatch:
            logger.debug('handleError:ERR_IDmismatch\n'\
	                 '\tIdentity mismatch: got %08x, expected %08x\n' % (p1, p2))
            self.ErrorHandler.fill('LAT_DATAGRAM_ERROR', ['ID Mismatch'])
	    
        else:
    	    logger.debug("UNKNOWN_ERROR\n"\
                         "\tUnrecognized error code %d = 0x%08x with "\
                         "\targuments %d = 0x%08x, %d = 0x%08x\n" %\
                         (code, code, p1, p1, p2, p2))
            self.ErrorHandler.fill('LAT_DATAGRAM_ERROR', ['UNKNOWN_ERROR_CODE', p1, p2])

        return code

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
