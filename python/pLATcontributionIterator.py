
import logging
import LDF

class pLATcontributionIterator(LDF.LDBI_LATcontributionIterator):

    def __init__(self, ebfEventIterator):
        LDF.LDBI_LATcontributionIterator.__init__(self, ebfEventIterator)

    def handleError(self, contribution, code, p1, p2):
        fn = 'pLATcontributionIterator.handleError()'
        if code == LDF.LATcontributionIterator.ERR_UDFcontribution:
            logging.error('%s: unrecognized contribution.' % fn)
            return -1
        else:
            logging.error('%s: unknown error code.' % fn)
            return 0
