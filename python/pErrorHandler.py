#! /bin/env python

import pSafeLogger
logger = pSafeLogger.getLogger('pErrorHandler')

import time
import sys
import cPickle
import pUtils

from pError      import pError
from pErrorEvent import pErrorEvent

MAX_ERROR_EVENTS = 500

class pErrorHandler:

    def __init__(self):
        self.NumProcessedEvents = 'n/a'
        self.ErrorCountsDict = {}
        self.ErrorEventsList = []
        self.ErrorsBuffer = []

    def fill(self, errorCode, parameters=[]):
        error = pError(errorCode, parameters)
        # fill the summary by error code
        try:
            self.ErrorCountsDict[errorCode] += 1
        except KeyError:
            self.ErrorCountsDict[errorCode] = 1
        # fill a buffer of errors for this event.
        self.ErrorsBuffer.append(error)
        
    def flushErrorsBuffer(self, eventNumber):
        # fill the ErrorEventsDict, in case the event has errors,
        # using the correct event ID
        # to be called at the end of event processing
        if self.ErrorsBuffer != []:
            errorEvent = pErrorEvent(eventNumber)
            for error in self.ErrorsBuffer:
                errorEvent.addError(error)
            self.ErrorEventsList.append(errorEvent)
            self.ErrorsBuffer = []
            return errorEvent.ErrorSummary
        return 0

    def getNumErrors(self):
        return sum(self.ErrorCountsDict.values())

    def getNumErrorEvents(self):
        return len(self.ErrorEventsList)
 
    def writeXmlOutput(self, filename):
        try:
            from pXmlWriter import pXmlWriter
        except:
            logger.error("Can not find pXmlWriter module. Exit.")
            return None
        truncated = self.getNumErrorEvents() > MAX_ERROR_EVENTS
        xmlWriter  = pXmlWriter(filename)
        xmlWriter.openTag('errorContribution')
        xmlWriter.indent()
        xmlWriter.newLine()
        xmlWriter.writeComment('Summary by error code')
        xmlWriter.openTag('errorSummary')
        xmlWriter.indent()
        for (errorCode, numErrors) in self.ErrorCountsDict.items():
            numEvents = 0
            for errorEvent in self.ErrorEventsList:
                if errorEvent.hasError(errorCode):
                    numEvents += 1
            xmlWriter.writeTag('errorType', {'code':errorCode,
                                             'quantity': numErrors,
                                             'events': numEvents
                                             })
        xmlWriter.backup()
        xmlWriter.closeTag('errorSummary')
        xmlWriter.newLine()
        xmlWriter.writeComment('Summary by event number')
        xmlWriter.openTag('eventSummary',\
                          {'num_error_events'      : self.getNumErrorEvents(),
                           'num_processed_events'  : self.NumProcessedEvents,
                           'truncated'             : truncated})
        xmlWriter.indent()
        for (eventNumber, errorEvent) in enumerate(self.ErrorEventsList):
            xmlWriter.openTag('errorEvent', {'eventNumber': eventNumber})
            xmlWriter.indent()
            for error in errorEvent.ErrorsList:
                xmlWriter.writeLine(error.getXmlLine())
            xmlWriter.backup()
            xmlWriter.closeTag('errorEvent')
        xmlWriter.backup()
        xmlWriter.closeTag('eventSummary')
        xmlWriter.backup()
        xmlWriter.newLine()
        xmlWriter.closeTag('errorContribution')
        xmlWriter.closeFile()


        

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage='usage: %prog pickle_file')
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.print_help()
        parser.error('incorrect number of arguments')
        sys.exit()
    errorHandler = pErrorHandler(args[0])
    errorHandler.browseErrors()
