## @package pError
## @brief Package describing an error.


ERROR_DETAIL_LABELS_DICT = {
    'GCCC_ERROR'                  : ['Tower', 'GCCC', 'Err'],
    'GTCC_ERROR'                  : ['Tower', 'GTCC', 'Err'],
    'PHASE_ERROR'                 : ['Tower', 'Tags'],
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
    'ACD_HEADER_PARITY_ERROR'     : ['Cable'],
    'ACD_PHA_PARITY_ERROR'        : ['Cable', 'Channel'],
    'ACD_PHA_INCONSISTENCY'       : ['Cable', 'Channel', 'AcceptList'],
    'TEM_BUG_INSTANCE'            : ['Type'],
    'TIMETONE_INCOMPLETE'         : ['timeSecs']
    }

ERROR_DOCUMENTATION_DICT = {
    
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

    def hasDetails(self):
        return self.Details != []

    def getXmlLine(self):
        return '<error code="%s" %s/>' %\
            (self.ErrorCode, self.getDetailsAsText())
        
    ## @brief Return the error details formatted in such a way that they can be
    #  printed on the screen or put into the report.
    ## @param self
    #  The class instance.

    def getDetailsAsText(self):
        details = ''
        for (i, detail) in enumerate(self.Details):
            try:
                label = ERROR_DETAIL_LABELS_DICT[self.ErrorCode][i]
            except:
                label = 'Parameter%d' % i
            details += ' %s="%s"' % (label, self.Details[i])
        return details

    def getAsText(self):
        text = self.ErrorCode
        if self.hasDetails():
            text += ' (%s)' % self.getDetailsAsText().strip().replace(' ', ', ')
        return text

    def __str__(self):
        return self.getAsText()



if __name__ == '__main__':
    errors = [pError('TEM_BUG_INSTANCE'),
              pError('TEST_CODE', [3, 2])]
    for error in errors:
        print error
