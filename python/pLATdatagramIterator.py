
import logging
import LDF

class pLATdatagramIterator(LDF.LDBI_LATdatagramIterator):

    def __init__(self, latContributionIterator):
        LDF.LDBI_LATdatagramIterator.__init__(self, latContributionIterator)
        self.__LatContributionIterator = latContributionIterator
        
    def handleError(self, contribution, code, p1, p2):
        fn = 'pLATdatagramIterator.handleError()'
        if code == LDF.LATdatagramIterator.ERR_IDmismatch:
            logging.error('%s: identity mismatch.'  % fn)
            return -1
        else:
            logging.error('%s: unknown error code.' % fn)
            return 0

    def process(self, datagram):
        self.__LatContributionIterator.iterate(datagram)
        status = self.__LatContributionIterator.status()
        if status:
            fn = 'pLATdatagramIterator.process()'
            logging.error('%s: iteration returned %d' % (fn, status))
        return 0
