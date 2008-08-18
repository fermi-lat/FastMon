
ERROR_BITS_DICT = {
    'GCCC_ERROR'                  : 0,
    'GTCC_ERROR'                  : 1,
    'PHASE_ERROR'                 : 2,
    'TIMEOUT_ERROR'               : 3,
    'GTRC_PHASE_ERROR'            : 4,
    'GTFE_PHASE_ERROR'            : 5,
    'GTCC_FIFO_ERROR'             : 6,
    'GTCC_TIMEOUT_ERROR'          : 7,
    'GTCC_HEADER_PARITY_ERROR'    : 8,
    'GTCC_WORD_COUNT_PARITY_ERROR': 9,
    'GTRC_SUMMARY_ERROR'          : 10,
    'GTCC_DATA_PARITY_ERROR'      : 11,
    'ACD_HEADER_PARITY_ERROR'     : 12,
    'ACD_PHA_PARITY_ERROR'        : 13,
    'ACD_PHA_INCONSISTENCY'       : 14,
    'TEM_BUG_INSTANCE'            : 15,
    'TIMETONE_INCOMPLETE'         : 16,
    'TIMETONE_EARLY_EVENT'        : 17,
    'TIMETONE_FLYWHEELING'        : 18,
    'TIMETONE_MISSING_CPUPPS'     : 19,
    'TIMETONE_MISSING_LATPPS'     : 20,
    'TIMETONE_MISSING_TIMETONE'   : 21,
    'TIMETONE_NULL_SOURCE_GPS'    : 22,
    'UNKNOWN_ERROR'               : 31
    }


class pErrorEvent:

    def __init__(self, eventNumber):
        self.EventNumber = eventNumber
        self.ErrorsList  = []
        self.ErrorSummary = 0

    def assertSummaryBit(self, errorCode):
        try:
            bitNumber = ERROR_BITS_DICT[errorCode]
        except KeyError:
            bitNumber = ERROR_BITS_DICT['UNKNOWN_ERROR']
        self.ErrorSummary |= (1 << bitNumber)

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
       
