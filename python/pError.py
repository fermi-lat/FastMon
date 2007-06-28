
import pUtils


PARAMETER_LABELS = {
    'GCCC_ERROR'                  : ['Tower', 'GCCC', 'Err'],
    'GTCC_ERROR'                  : ['Tower', 'GTCC', 'Err'],
    'PHASE_ERROR'                 : ['Tower', 'Err'],
    'TIMEOUT_ERROR'               : ['Tower', 'Err'],
    'GTRC_PHASE_ERROR'            : ['Tower', 'GTCC', 'GTRC', 'Err'],
    'GTFE_PHASE_ERROR'            : ['Tower', 'GTCC', 'GTRC', 'Err1', 'Err2',\
                                     'Err3', 'Err3' , 'Err4', 'Err5'],
    'GTCC_FIFO_ERROR'             : ['Tower', 'GTCC', 'Err'],
    'GTCC_TIMEOUT_ERROR'          : ['Tower', 'GTCC', 'Err'],
    'GTCC_HEADER_PARITY_ERROR'    : ['Tower', 'GTCC', 'Err'],
    'GTCC_WORD_COUNT_PARITY_ERROR': ['Tower', 'GTCC', 'Err'],
    'GTRC_SUMMARY_ERROR'          : ['Tower', 'GTCC', 'Err'],
    'GTCC_DATA_PARITY_ERROR'      : ['Tower', 'GTCC', 'Err'],
    'UNPHYSICAL_STRIP_ID'         : ['Tower', 'Layer end', 'hit']
    }


class pError:

    def __init__(self, eventNumber, errorCode, parameters=[]):
        self.EventNumber = eventNumber
        self.ErrorCode   = errorCode
        self.Parameters  = parameters

    def __getLabel(self, index):
        try:
            return PARAMETER_LABELS[self.ErrorCode][index]
        except:
            return 'Parameter %d' % index
        
    def getPlainRepresentation(self, verbose=True, stringLength=20):
        output = ''
        if verbose:
            output += '%s: %d\n' %\
                      (pUtils.expandString('Event number', stringLength),
                       self.EventNumber)
            output += '%s: %s\n' %\
                      (pUtils.expandString('Error code', stringLength),
                       self.ErrorCode)
        else:
            output += '- %s\n' % self.ErrorCode
        for i in range(len(self.Parameters)):
            parameter = self.Parameters[i]
            label     = self.__getLabel(i)
            output += '%s: %s\n' %\
                      (pUtils.expandString(label, stringLength), parameter)
        return output

    def getDoxygenRepresentation(self):
        output = '- %s\\n\n' % pUtils.verbatim(self.ErrorCode)
        for i in range(len(self.Parameters)):
            parameter = self.Parameters[i]
            label     = self.__getLabel(i)
            output += '%s: %s\\n\n' % (label, parameter)
        return output

    def __str__(self):
        return self.getPlainRepresentation()
    



if __name__ == '__main__':
    errors = [pError(12, 'UNPHYSICAL_STRIP_ID', [12, 34, 1753]),
              pError(116, 'TEST_CODE', [3, 2])
              ]
    for error in errors:
        print error.getPlainRepresentation(True)
        print error.getPlainRepresentation(False)
        print error.getDoxygenRepresentation()
