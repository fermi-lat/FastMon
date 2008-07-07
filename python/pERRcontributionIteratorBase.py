
## @package pERRcontributionIteratorBase
## @brief Error contribution iterator.

import LDF


## @brief Class implementing the error contribution iterator.
#
#  It essentially fills a @ref pErrorHandler object.

class pERRcontributionIteratorBase(LDF.ERRcontributionIterator):

    ## @brief Contructor.
    #
    #  Note that whenever the iterator is called, the error counter is
    #  filled with a generic error code ('ERROR_ITERATOR_CALL') to keep
    #  track of all possible errors.
    ## @param self
    #  The class instance.
    ## @param event
    #  The event object.
    ## @param contribution
    #  The contribution object.
    ## @param offset
    #  The offset.
    ## @param errorHandler
    #  The @ref pErrorHandler object.
    
    def __init__(self, event, contribution, offset, errorHandler):

        ## @var ErrorHandler
        ## @brief The @ref pErrorHandler object.
        
        LDF.ERRcontributionIterator.__init__(self, event, contribution)
        self.offset(offset)
        self.ErrorHandler = errorHandler

    def handleError(self, event, code, p1, p2):
        if code == LDF.ERRcontributionIterator.ERR_TEMbug:
            self.ErrorHandler.fill('TEM_BUG_INSTANCE', ['generic'])
            return LDF.ERRcontributionIterator.ERR_TEMbug
        return 0

    ## @brief Dispatch function for GCCC errors.
    
    def gcccError(self, tower, gccc, err):
        self.ErrorHandler.fill('GCCC_ERROR', [tower, gccc])
        return 0

    ## @brief Dispatch function for GTCC errors.

    def gtccError(self, tower, gtcc, err):
        self.ErrorHandler.fill('GTCC_ERROR', [tower, gtcc])
        return 0

    ## @brief Dispatch function for "cable phase error" errors.

    def phaseError(self, tower, err):
        tags = []
        for i in range(8):
            tags.append(int((err >> (i << 1)) & 0x0003))
        self.ErrorHandler.fill('PHASE_ERROR', [tower, tags])
        return 0

    ## @brief Dispatch function for "cable timeout" errors.

    def timeoutError(self, tower, err):
        self.ErrorHandler.fill('TIMEOUT_ERROR', [tower])
        return 0

    ## @brief Dispatch function for GTCC "GTRC phase error" errors.

    def gtrcPhaseError(self, tower, gtcc, gtrc, err):
        self.ErrorHandler.fill('GTRC_PHASE_ERROR', [tower, gtcc, gtrc])
        return 0

    ## @brief Dispatch function for GTCC "GTFE phase error" errors.

    def gtfePhaseError(self, tower, gtcc, gtrc, err1, err2, err3, err4, err5):
        self.ErrorHandler.fill('GTFE_PHASE_ERROR', [tower, gtcc, gtrc])
        return 0

    ## @brief Dispatch function for GTCC "FIFO full" errors.

    def gtccFIFOerror(self, tower, gtcc, err):
        self.ErrorHandler.fill('GTCC_FIFO_ERROR', [tower, gtcc])
        return 0

    ## @brief Dispatch function for GTCC "cable timeout" errors.

    def gtccTMOerror(self, tower, gtcc):
        self.ErrorHandler.fill('GTCC_TIMEOUT_ERROR', [tower, gtcc])
        return 0

    ## @brief Dispatch function for GTCC "header parity error" errors.

    def gtccHDRParityError(self, tower, gtcc):
        self.ErrorHandler.fill('GTCC_HEADER_PARITY_ERROR', [tower, gtcc])
        return 0

    ## @brief Dispatch function for GTCC "word count parity error" errors.

    def gtccWCParityError(self, tower, gtcc):
        self.ErrorHandler.fill('GTCC_WORD_COUNT_PARITY_ERROR', [tower, gtcc])
        return 0

    ## @brief Dispatch function for GTCC "GTRC summary error" errors.

    def gtrcSummaryError(self, tower, gtcc):
        self.ErrorHandler.fill('GTRC_SUMMARY_ERROR', [tower, gtcc])
        return 0

    ## @brief Dispatch function for GTCC "data parity error" errors.

    def gtccDataParityError(self, tower, gtcc):
        self.ErrorHandler.fill('GTCC_DATA_PARITY_ERROR', [tower, gtcc])
        return 0
