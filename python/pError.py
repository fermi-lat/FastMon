## @package pError
## @brief Package describing an error.


ERROR_DETAIL_LABELS_DICT = {
    'TIMETONE_INCOMPLETE'         : ['timeSecs'],
    'TIMETONE_EARLY_EVENT'        : [],
    'TIMETONE_FLYWHEELING'        : [],
    'TIMETONE_MISSING_CPUPPS'     : [],
    'TIMETONE_MISSING_LATPPS'     : [],
    'TIMETONE_MISSING_TIMETONE'   : [],
    'TIMETONE_NULL_SOURCE_GPS'    : [],
    'GCCC_ERROR'                  : ['Tower', 'GCCC', 'Err'],
    'GTCC_ERROR'                  : ['Tower', 'GTCC', 'Err'],
    'PHASE_ERROR'                 : ['Tower', 'Tags'],
    'TIMEOUT_ERROR'               : ['Tower', 'Err'],
    'GTRC_PHASE_ERROR'            : ['Tower', 'GTCC', 'GTRC', 'Err'],
    'GTFE_PHASE_ERROR'            : ['Tower', 'GTCC', 'GTRC', 'Err1', 'Err2',\
                                     'Err3', 'Err3' , 'Err4', 'Err5'],
    'GTCC_FIFO_ERROR'             : ['Tower', 'GTCC', 'GTRC', 'Err'],
    'GTCC_TIMEOUT_ERROR'          : ['Tower', 'GTCC', 'GTRC'],
    'GTCC_HEADER_PARITY_ERROR'    : ['Tower', 'GTCC', 'GTRC'],
    'GTCC_WORD_COUNT_PARITY_ERROR': ['Tower', 'GTCC', 'GTRC'],
    'GTRC_SUMMARY_ERROR'          : ['Tower', 'GTCC', 'GTRC'],
    'GTCC_DATA_PARITY_ERROR'      : ['Tower', 'GTCC', 'GTRC'],
    'ACD_HEADER_PARITY_ERROR'     : ['Cable'],
    'ACD_PHA_PARITY_ERROR'        : ['Cable', 'Channel'],
    'ACD_PHA_INCONSISTENCY'       : ['Cable', 'Channel', 'AcceptList'],
    'TEM_BUG'                     : ['Type', 'Tower'],
    'ERR_CONTRIB_ERROR'           : ['Type', 'Tower'],    
    'TKR_CONTRIB_ERROR'           : ['Type', 'Tower'],    
    'CAL_CONTRIB_ERROR'           : ['Type', 'Tower'],    
    'ACD_CONTRIB_ERROR'           : ['Type', 'Tower']
    }

ERROR_DOC_DICT = {
    'ACD_PHA_INCONSISTENCY'    :\
        'There is a signal from a channel for which the accept bit is not set.',
    'TIMETONE_EARLY_EVENT'     :\
        'The event arrived close (a few hundred microseconds) to the TimeTone.',
    'TIMETONE_FLYWHEELING'     :\
        'CPU failed to construct its TimeTone message.',
    'TIMETONE_INCOMPLETE'      :\
        'The TimeTone is incomplete.',
    'TIMETONE_MISSING_CPUPPS'  :\
        'The arrival of the 1-PPS signal at the CPU timed out.',
    'TIMETONE_MISSING_LATPPS'  :\
        'The arrival of the 1-PPS signal at the LAT timed out.',
    'TIMETONE_MISSING_TIMETONE':\
	'The 1-PPS signal timed out.',
    'TIMETONE_NULL_SOURCE_GPS' :\
	'The source of the 1-PPS signal is the spacecraft clock, not the GPS.'
    }

ERROR_REMARKS_DICT = {

    }

def getExplanation(errorCode):
    try:
        return ERROR_DOC_DICT[errorCode]
    except:
        return '-'

def getRemerks(errorCode):
    try:
        return ERROR_REMARKS_DICT[errorCode]
    except:
        return '-'



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

    ## @brief Return the label corresponding to a certain item in the
    #  list of details.
    #
    #  If the label is not defined in ERROR_DETAIL_LABELS_DICT, then a generic
    #  one is built in place. If the index exceeds the number of elements
    #  in the predefined list, then it is assumed that the value is
    #  effectively the error summary.

    def getDetailLabel(self, index):
        try:
            if index == len(ERROR_DETAIL_LABELS_DICT[self.ErrorCode]):
                return 'Summary'
            else:
                return ERROR_DETAIL_LABELS_DICT[self.ErrorCode][index]
        except:
            return 'Parameter%d' % index
        
    ## @brief Return the error details formatted in such a way that they can be
    #  printed on the screen or put into the report.
    ## @param self
    #  The class instance.

    def getDetailsAsText(self):
        details = ''
        for (i, detail) in enumerate(self.Details):
            details += ' %s="%s"' % (self.getDetailLabel(i), self.Details[i])
        return details

    def getAsText(self):
        text = self.ErrorCode
        if self.hasDetails():
            text += ' (%s)' % self.getDetailsAsText().strip().replace(' ', ', ')
        return text

    def __str__(self):
        return self.getAsText()



if __name__ == '__main__':
    errors = [pError('TEM_BUG'),
              pError('TEST_CODE', [3, 2])]
    for error in errors:
        print error
