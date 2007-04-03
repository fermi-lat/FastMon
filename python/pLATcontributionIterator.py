## @package pLATcontributionIterator
## @brief Package managing the interation over a LAT contribution.

import logging
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
        fn = 'pLATcontributionIterator.handleError()'
        if code == LDF.LATcontributionIterator.ERR_UDFcontribution:
            logging.error('%s: unrecognized contribution.' % fn)
            return -1
        else:
            logging.error('%s: unknown error code.' % fn)
            return 0
