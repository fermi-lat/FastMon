#! /usr/bin/env python

import pSafeLogger
logger = pSafeLogger.getLogger('pXmlErrorMerger')

import sys

from pXmlWriter import pXmlWriter
from xml.dom    import minidom
from pXmlBaseElement import pXmlBaseElement


class pXmlErrorMerger(pXmlWriter):

    def mergeXmlFiles(self, inputList):
        self.ErrorCountsDict = {}
        self.EventCountsDict = {}
        self.EventSummaryDict = {'num_error_events'      : 0,
                                 'num_processed_events'  : 0,
                                 'truncated'             : 0
                                 }
        self.ErrorEventsList = []
        logger.info('Merging input files list...')
        for filePath in inputList:
            self.addXmlFile(filePath)
        self.writeXmlOutput()

    def addXmlFile(self, inputFilePath):
        logger.info('Adding input file %s...' % inputFilePath)
        xmlDoc = pXmlBaseElement(minidom.parse(file(inputFilePath)))
        for element in xmlDoc.getElementsByTagName('errorType'):
            element = pXmlBaseElement(element)
            code = element.getAttribute('code')
            quantity = int(element.getAttribute('quantity'))
            try:
                self.ErrorCountsDict[code] += quantity
            except KeyError:
                self.ErrorCountsDict[code] = quantity
            events = int(element.getAttribute('events'))
            try:
                self.EventCountsDict[code] += events
            except KeyError:
                self.EventCountsDict[code] = events
        element = pXmlBaseElement(xmlDoc.getElementByTagName('eventSummary'))
        for key in self.EventSummaryDict.keys():
            self.EventSummaryDict[key] += element.evalAttribute(key)
        self.EventSummaryDict['truncated'] =\
            (self.EventSummaryDict['truncated'] > 0)
        for element in xmlDoc.getElementsByTagName('errorEvent'):
            self.ErrorEventsList.append(element.toxml())

    def writeXmlOutput(self):
        logger.info('Writing output file...')
        self.openTag('errorContribution')
        self.indent()
        self.newLine()
        self.writeComment('Summary by error code')
        self.openTag('errorSummary')
        self.indent()
        for (code, number) in self.ErrorCountsDict.items():
            events = self.EventCountsDict[code]
            self.writeTag('errorType', {'code':code,
                                        'quantity': number,
                                        'events': events})
        self.backup()
        self.closeTag('errorSummary')
        self.newLine()
        self.writeComment('Summary by event number')
        self.openTag('eventSummary', self.EventSummaryDict)
        self.indent()
        for errorEvent in self.ErrorEventsList:
            self.writeLine(errorEvent)
        self.backup()
        self.closeTag('eventSummary')
        self.backup()
        self.newLine()
        self.closeTag('errorContribution')
        self.closeFile()


if __name__ == "__main__":
    import optparse
    parser = optparse.OptionParser()
    parser.add_option('-o', '--output-file', dest='o')
    parser.add_option('-i', '--input-file', dest='i', action='append')
    options, args = parser.parse_args()
    if options.i is None:
        print 'Please provide a list of xml file to merge through the i option.'
        sys.exit()
    merger = pXmlErrorMerger(options.o)
    merger.mergeXmlFiles(options.i)
