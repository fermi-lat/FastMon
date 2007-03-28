
import logging
import LDF


class pERRcontributionIteratorBase(LDF.ERRcontributionIterator):
    
    def __init__(self, event, contribution, offset, errorCounter):
        LDF.ERRcontributionIterator.__init__(self, event, contribution)
        self.offset(offset)
        self.__ErrorCounter = errorCounter
    
    def gcccError(self, tower, gccc, err):
        self.__ErrorCounter.fill('GCCC_ERROR')
        return 0

    def gtccError(self, tower, gtcc, err):
        self.__ErrorCounter.fill('GTCC_ERROR')
        return 0

    def phaseError(self, tower, err):
        self.__ErrorCounter.fill('PHASE_ERROR')
        return 0

    def timeoutError(self, tower, err):
        self.__ErrorCounter.fill('TIMEOUT_ERROR')
        return 0

    def gtrcPhaseError(self, tower, gtcc, gtrc, err):
        self.__ErrorCounter.fill('GTRC_PHASE_ERROR')
        return 0

    def gtfePhaseError(self, tower, gtcc, gtrc, err1, err2, err3, err4, err5):
        self.__ErrorCounter.fill('GTFE_PHASE_ERROR')
        return 0

    def gtccFIFOerror(self, tower, gtcc, err):
        self.__ErrorCounter.fill('GTCC_FIFO_ERROR')
        return 0

    def gtccTMOerror(self, tower, gtcc):
        self.__ErrorCounter.fill('GTCC_TIMEOUT_ERROR')
        return 0

    def gtccHDRParityError(self, tower, gtcc):
        self.__ErrorCounter.fill('GTCC_HEADER_PARITY_ERROR')
        return 0

    def gtccWCParityError(self, tower, gtcc):
        self.__ErrorCounter.fill('GTCC_WC_PARITY_ERROR')
        return 0

    def gtrcSummaryError(self, tower, gtcc):
        self.__ErrorCounter.fill('GTRC_SUMMARY_ERROR')
        return 0

    def gtccDataParityError(self, tower, gtcc):
        self.__ErrorCounter.fill('GTCC_DATA_PARITY_ERROR')
        return 0
