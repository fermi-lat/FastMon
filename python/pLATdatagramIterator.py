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
        fn = 'pLATdatagramIterator.handleError()'
        if code == LDF.LATdatagramIterator.ERR_IDmismatch:
            logger.error('%s: identity mismatch.'  % fn)
            return -1
        else:
            logger.error('%s: unknown error code.' % fn)
            return 0

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
