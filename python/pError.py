## @package pError
## @brief Package describing an error.

import pUtils


DETAIL_LABELS = {
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
    'UNPHYSICAL_TKR_TOT'          : ['Tower', 'LayerEnd', 'tot'],
    'UNPHYSICAL_TKR_STRIP_ID'     : ['Tower', 'LayerEnd', 'hit'],
    'UNPHYSICAL_TKR_LYR_ID'       : ['Tower', 'LayerEnd', 'hit'],
    'UNPHYSICAL_TKR_TWR_ID'       : ['Tower', 'LayerEnd', 'hit'],
    'UNPHYSICAL_CAL_COL_ID'       : ['Tower', 'Layer', 'Column'],
    'UNPHYSICAL_CAL_LYR_ID'       : ['Tower', 'Layer', 'Column'],
    'UNPHYSICAL_CAL_TWR_ID'       : ['Tower', 'Layer', 'Column']
    }


## @brief Class describing a generic error.

class pError:

    ## @brief Basic constructor.
    ## @param self
    #  The class instance.
    ## @param errorCode
    #  The error code (usually a string like "GTCC_FIFO_ERROR").
    ## @param details
    #  The error details (like wich tower, layer, etc... caused the error).
    #  All the additional error information can be added here.
    
    def __init__(self, errorCode, details=[]):

        ## @var ErrorCode
        ## @brief The error code (usually a string like "GTCC_FIFO_ERROR").

        ## @var Details
        ## @brief The error details (like wich tower, layer, etc...
        #  caused the error).
        
        self.ErrorCode   = errorCode
        self.Details     = details

    ## @brief Return the error details formatted in such a way that they can be
    #  printed on the screen or put into the report.
    ## @param self
    #  The class instance.

    def getDetailsAsText(self):
        details = ''
        for i in range(len(self.Details)):
            try:
                label = DETAIL_LABELS[self.ErrorCode][i]
            except KeyError:
                label = 'Parameter %d' % i
            details += '%s=%s, ' % (label, self.Details[i])
        return details[:-2]

    def getAsText(self):
        return '%s (%s)' % (self.ErrorCode, self.getDetailsAsText())

    def __str__(self):
        return self.getAsText()


if __name__ == '__main__':
    errors = [pError('UNPHYSICAL_STRIP_ID', [12, 34, 1753]),
              pError('TEST_CODE', [3, 2])]
    for error in errors:
        print error
