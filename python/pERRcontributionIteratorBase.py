## @package pERRcontributionIteratorBase
## @brief Error contribution iterator.

import pSafeLogger
logger = pSafeLogger.getLogger('pERRcontributionIteratorBase')

import LDF
from pGlobals  import *


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
	self.TemId        = LDF.LATPcellHeader.source(contribution.header())
        self.offset(offset)
        self.ErrorHandler = errorHandler

    def getSummary(self):
        return '%1d-%1d-0x%02x-0x%01x' % (long(self.theError().tmo()),
                                          long(self.theError().phs()),
                                          long(self.theError().tkr()),
                                          long(self.theError().cal()))

    ## @brief Handle error function overload
    #  From Ric Claus
    #  
    #  The LookupErrorCode function is in Common/python/pGlobals
    #
    ##  return code is:
    #   - negative to indicate bail immediately
    #   - 0 for SUCCESS
    #   - positive to indicate that there was an error but iteration can continue
    #
    #	{701 : 'ERR_PastEnd',	      # Unexpectedly pointing past end of contribution
    #    702 : 'ERR_OddCcWordCount',  # CC word count was found to be odd - not legal
    #    703 : 'ERR_HighWordCount',   # Word count is higher than max allowed
    #    704 : 'ERR_NoOpaqueData',    # Unexpectedly found no 'opaque data' for error
    #    705 : 'ERR_MissingParams',   # (Some) error params were unexpectedly missing
    #    706 : 'ERR_TEMbug',	      # Phasing AND TKR Errors = TEM bug => junk error data
    #    707 : 'ERR_TooMuchPadding',  # More than the expected amount of padding found
    #    708 : 'ERR_NonzeroPadding'}  # Padding was nonzero

    def handleError(self, event, code, p1, p2):
      s = LDF.ERRcontributionIterator.handleError(self, event, code, p1,p2)
      errName = LookupErrorCode(self, code)[4:]
      # We want to tag the TEM BUG events specifically
      if errName == 'TEMbug':
          self.ErrorHandler.fill('TEM_BUG', ['All tags off by one', self.TemId, p1, p2])
      else:
          self.ErrorHandler.fill('ERR_CONTRIB_ERROR', [errName, self.TemId, p1, p2])
      return s

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
        self.ErrorHandler.fill('PHASE_ERROR', [tower, tags, self.getSummary()])
        return 0

    ## @brief Dispatch function for "cable timeout" errors.
    #  What shall we do with err ?

    def timeoutError(self, tower, err):
        self.ErrorHandler.fill('TIMEOUT_ERROR', [tower])
        return 0

    ## @brief Dispatch function for GTCC "GTRC phase error" errors.
    #  What shall we do with err ?

    def gtrcPhaseError(self, tower, gtcc, gtrc, err):
        self.ErrorHandler.fill('GTRC_PHASE_ERROR', [tower, gtcc, gtrc])
        return 0

    ## @brief Dispatch function for GTCC "GTFE phase error" errors.
    #  What shall we do with err(i) ?
    def gtfePhaseError(self, tower, gtcc, gtrc, err1, err2, err3, err4, err5):
        self.ErrorHandler.fill('GTFE_PHASE_ERROR', [tower, gtcc, gtrc])
        return 0

    ## @brief Dispatch function for GTCC "FIFO full" errors.
    #  What shall we do with err ?

    def gtccFIFOerror(self, tower, gtcc, gtrc, err):
        self.ErrorHandler.fill('GTCC_FIFO_ERROR', [tower, gtcc, gtrc])
        return 0

    ## @brief Dispatch function for GTCC "cable timeout" errors.

    def gtccTMOerror(self, tower, gtcc, gtrc):
        self.ErrorHandler.fill('GTCC_TIMEOUT_ERROR', [tower, gtcc, gtrc])
        return 0

    ## @brief Dispatch function for GTCC "header parity error" errors.

    def gtccHDRParityError(self, tower, gtcc, gtrc):
        self.ErrorHandler.fill('GTCC_HEADER_PARITY_ERROR', [tower, gtcc, gtrc])
        return 0

    ## @brief Dispatch function for GTCC "word count parity error" errors.

    def gtccWCParityError(self, tower, gtcc, gtrc):
        self.ErrorHandler.fill('GTCC_WORD_COUNT_PARITY_ERROR', [tower, gtcc, gtrc])
        return 0

    ## @brief Dispatch function for GTCC "GTRC summary error" errors.

    def gtrcSummaryError(self, tower, gtcc, gtrc):
        self.ErrorHandler.fill('GTRC_SUMMARY_ERROR', [tower, gtcc, gtrc])
        return 0

    ## @brief Dispatch function for GTCC "data parity error" errors.

    def gtccDataParityError(self, tower, gtcc, gtrc):
        self.ErrorHandler.fill('GTCC_DATA_PARITY_ERROR', [tower, gtcc, gtrc])
        return 0


