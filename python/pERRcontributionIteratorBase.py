
## @package pERRcontributionIteratorBase
## @brief Error contribution iterator.

import logging
import LDF


## @brief Class implementing the error contribution iterator.
#
#  It essentially fills a @ref pEventErrorCounter object.

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
    ## @param errorCounter
    #  The @ref pEventErrorCounter object.
    
    def __init__(self, event, contribution, offset, errorCounter):

        ## @var __ErrorCounter
        ## @brief The @ref pEventErrorCounter object.
        
        LDF.ERRcontributionIterator.__init__(self, event, contribution)
        self.offset(offset)
        self.__ErrorCounter = errorCounter
        self.__ErrorCounter.fill('ERROR_ITERATOR_CALL')

    ## @brief Dispatch function for GCCC errors.
    
    def gcccError(self, tower, gccc, err):
        self.__ErrorCounter.fill('GCCC_ERROR')
        return 0

    ## @brief Dispatch function for GTCC errors.

    def gtccError(self, tower, gtcc, err):
        self.__ErrorCounter.fill('GTCC_ERROR')
        return 0

    ## @brief Dispatch function for "cable phase error" errors.

    def phaseError(self, tower, err):
        self.__ErrorCounter.fill('PHASE_ERROR')
        return 0

    ## @brief Dispatch function for "cable timeout" errors.

    def timeoutError(self, tower, err):
        self.__ErrorCounter.fill('TIMEOUT_ERROR')
        return 0

    ## @brief Dispatch function for GTCC "GTRC phase error" errors.

    def gtrcPhaseError(self, tower, gtcc, gtrc, err):
        self.__ErrorCounter.fill('GTRC_PHASE_ERROR')
        return 0

    ## @brief Dispatch function for GTCC "GTFE phase error" errors.

    def gtfePhaseError(self, tower, gtcc, gtrc, err1, err2, err3, err4, err5):
        self.__ErrorCounter.fill('GTFE_PHASE_ERROR')
        return 0

    ## @brief Dispatch function for GTCC "FIFO full" errors.

    def gtccFIFOerror(self, tower, gtcc, err):
        self.__ErrorCounter.fill('GTCC_FIFO_ERROR')
        return 0

    ## @brief Dispatch function for GTCC "cable timeout" errors.

    def gtccTMOerror(self, tower, gtcc):
        self.__ErrorCounter.fill('GTCC_TIMEOUT_ERROR')
        return 0

    ## @brief Dispatch function for GTCC "header parity error" errors.

    def gtccHDRParityError(self, tower, gtcc):
        self.__ErrorCounter.fill('GTCC_HEADER_PARITY_ERROR')
        return 0

    ## @brief Dispatch function for GTCC "word count parity error" errors.

    def gtccWCParityError(self, tower, gtcc):
        self.__ErrorCounter.fill('GTCC_WORD_COUNT_PARITY_ERROR')
        return 0

    ## @brief Dispatch function for GTCC "GTRC summary error" errors.

    def gtrcSummaryError(self, tower, gtcc):
        self.__ErrorCounter.fill('GTRC_SUMMARY_ERROR')
        return 0

    ## @brief Dispatch function for GTCC "data parity error" errors.

    def gtccDataParityError(self, tower, gtcc):
        self.__ErrorCounter.fill('GTCC_DATA_PARITY_ERROR')
        return 0
