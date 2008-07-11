
ERROR_BITS_DICT = {
    'GCCC_ERROR'                  : 1,
    'GTCC_ERROR'                  : 2,
    'PHASE_ERROR'                 : 3,
    'TIMEOUT_ERROR'               : 4,
    'GTRC_PHASE_ERROR'            : 5,
    'GTFE_PHASE_ERROR'            : 6,
    'GTCC_FIFO_ERROR'             : 7,
    'GTCC_TIMEOUT_ERROR'          : 8,
    'GTCC_HEADER_PARITY_ERROR'    : 9,
    'GTCC_WORD_COUNT_PARITY_ERROR': 10,
    'GTRC_SUMMARY_ERROR'          : 11,
    'GTCC_DATA_PARITY_ERROR'      : 12,
    'ACD_HEADER_PARITY_ERROR'     : 13,
    'ACD_PHA_PARITY_ERROR'        : 14,
    'ACD_PHA_INCONSISTENCY'       : 15,
    'TEM_BUG_INSTANCE'            : 16,
    'TIMETONE_INCOMPLETE'         : 17,
    'TIMETONE_EARLY_EVENT'        : 18,
    'TIMETONE_FLYWHEELING'        : 19,
    'TIMETONE_MISSING_CPUPPS'     : 20,
    'TIMETONE_MISSING_LATPPS'     : 21,
    'TIMETONE_MISSING_TIMETONE'   : 22,
    'TIMETONE_NULL_SOURCE_GPS'    : 23
    }

UNKNOWN_ERROR_BIT = 0


class pErrorEvent:

    def __init__(self, eventNumber):
        self.EventNumber = eventNumber
        self.ErrorsList  = []
        self.ErrorSummary = 0x0

    def assertSummaryBit(self, errorCode):
        try:
            bitNumber = ERROR_BITS_DICT[errorCode]
        except KeyError:
            bitNumber = UNKNOWN_ERROR_BIT
        self.ErrorSummary |= (0x1 << bitNumber)

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
    badEvent.addError(pError('TEST'))
    badEvent.addError(pError('TEST', [1, 2, 3]))
    badEvent.addError(pError('GCCC_ERROR'))
    print badEvent
       
