
ERROR_BITS_DICT = {
    'TIMETONE_INCOMPLETE'         : 0,
    'TIMETONE_EARLY_EVENT'        : 1,
    'TIMETONE_FLYWHEELING'        : 2,
    'TIMETONE_MISSING_CPUPPS'     : 3,
    'TIMETONE_MISSING_LATPPS'     : 4,
    'TIMETONE_MISSING_TIMETONE'   : 5,
    'TIMETONE_NULL_SOURCE_GPS'    : 6,
    'GCCC_ERROR'                  : 8, 
    'GTCC_ERROR'                  : 9, 
    'PHASE_ERROR'                 : 10,
    'TIMEOUT_ERROR'               : 11,
    'GTRC_PHASE_ERROR'            : 12,
    'GTFE_PHASE_ERROR'            : 13,
    'GTCC_FIFO_ERROR'             : 14,
    'GTCC_TIMEOUT_ERROR'          : 15,
    'GTCC_HEADER_PARITY_ERROR'    : 16,
    'GTCC_WORD_COUNT_PARITY_ERROR': 17,
    'GTRC_SUMMARY_ERROR'          : 18,
    'GTCC_DATA_PARITY_ERROR'      : 19,
    'ACD_HEADER_PARITY_ERROR'     : 20,    
    'ACD_PHA_PARITY_ERROR'        : 21,
    'ACD_PHA_INCONSISTENCY'       : 22,
    'TEM_BUG'                     : 23,
    'ERR_CONTRIB_ERROR'           : 24,
    'TKR_CONTRIB_ERROR'           : 25,
    'CAL_CONTRIB_ERROR'           : 26,
    'AEM_CONTRIB_ERROR'           : 27, 
    'PACKET_ERROR'                : 28,
    'EBF_CONTRIB_ERROR'           : 29,
    'LAT_CONTRIB_ERROR'           : 30,
    'LAT_DATAGRAM_ERROR'          : 31,
    'EBF_EVENT_ERROR'             : 31    
    }

UNKNOWN_ERROR_BIT = 31


class pErrorEvent:

    def __init__(self, eventNumber):
        self.EventNumber = eventNumber
        self.ErrorsList  = []
        self.ErrorSummary = 0

    def getBitNumber(self, errorCode):
        try:
            return ERROR_BITS_DICT[errorCode]
        except KeyError:
            return UNKNOWN_ERROR_BIT

    def assertSummaryBit(self, errorCode):
        self.ErrorSummary |= (1 << self.getBitNumber(errorCode))

    def hasErrors(self):
        return self.ErrorSummary > 0

    def hasError(self, errorCode):
        return bool((self.ErrorSummary >> self.getBitNumber(errorCode)) & 1)

    def addError(self, error):
        self.ErrorsList.append(error)
        self.assertSummaryBit(error.ErrorCode)

    def getAsText(self):
        txt = 'Event %s contains error(s):\n' % self.EventNumber
        for error in self.ErrorsList:
            txt += '- %s\n' % error.getAsText()
        txt += 'Error summary: 0x%x (decimal %d)\n' %\
            (self.ErrorSummary, self.ErrorSummary)
        return txt

    def getErrorsDict(self):
        dict = {}
        for error in self.ErrorsList:
            dict[error.ErrorCode] = error.getDetailsAsText()
        return dict

    def __str__(self):
        return self.getAsText()


if __name__ == '__main__':
    from pError import pError
    badEvent = pErrorEvent(313)
    badEvent.addError(pError('TEST', [1, 2, 3]))
    badEvent.addError(pError('GCCC_ERROR', [0, 2, 6]))
    print badEvent
    print badEvent.hasErrors()
    print badEvent.hasError('TEST')
    print badEvent.hasError('GCCC_ERROR')
    print badEvent.hasError('GTCC_FIFO_ERROR')
