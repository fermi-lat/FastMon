#! /bin/env python

import os
import sys
import time
import logging
import LDF
import ROOT
import logging

from copy 			      import copy
from array                            import array
from LICOS_Scripts.analysis.LsfMerger import LsfMerger
from pRootTreeMaker                   import pRootTreeMaker
from pLATdatagramIterator             import pLATdatagramIterator
from pLATcontributionIterator         import pLATcontributionIterator
from pEBFeventIterator                import pEBFeventIterator
from pXmlParser                       import pXmlParser
from pGlobals			      import *

logging.basicConfig(level=logging.DEBUG)

class pDataProcessor:

    def __init__(self):
        self.__XmlParser = pXmlParser('../xml/config.xml')
        self.TreeMaker   = pRootTreeMaker(self.__XmlParser)
        from pLATcomponentIterator    import pLATcomponentIterator
        self.lci         = pLATcomponentIterator(self.TreeMaker)
        self.eei         = pEBFeventIterator(self.lci)
        self.lcti        = pLATcontributionIterator(self.eei)
        self.ldi         = pLATdatagramIterator(self.lcti)
        self.ldbi        = LDF.LATdataBufferIterator(self.ldi)
        self.NumEvents   = 0
        self.LsfMerger   = None
        self.OutROOTFile = None
        self.ROOTTree    = None

    def openFile(self, filePath):
        self.LsfMerger   = LsfMerger(filePath)

    def processEvent(self, event):
        self.TreeMaker.resetVariables()
        self.ldbi.iterate(event, len(event))
        self.TreeMaker.fillTree()
        self.NumEvents += 1
        if not self.NumEvents%100:
            logging.debug('%d events processed' % self.NumEvents)
        
    def processMetaEvent(self, meta):
	self.TreeMaker.DefaultVariablesDictionary['event_timestamp'][0] = \
		self.calculateTimeStamp(meta)


    def calculateTimeStamp(self, meta):
	timeTics = copy(meta.timeTics())
	timeHack_tics = copy(meta.timeHack().tics())
	timeHack_hacks = copy(meta.timeHack().hacks())
	clockTicksEvt1PPS = timeTics - timeHack_tics	
	if(clockTicksEvt1PPS <0):
	    clockTicksEvt1PPS += CLOCK_ROLLOVER
	timestamp = timeHack_hacks +  clockTicksEvt1PPS*CLOCK_TIC
	#print timestamp
	return timestamp
				

    def startProcessing(self, maxEvents = 1000):
        logging.info('Beginning data processing...')
        startTime = time.time()
        while (self.NumEvents < maxEvents):
            try:
                (meta, buff) = self.LsfMerger.getUncompressedEvent()
            except TypeError:
                logging.info('Got void event. Returning...')
                return 
            self.processMetaEvent(meta)
            self.processEvent(buff)
        elapsedTime = time.time() - startTime
        averageRate = self.NumEvents/elapsedTime
        logging.info('Done. %d events processed in %s s (%f Hz).\n' %\
                     (self.NumEvents, elapsedTime, averageRate))
        self.TreeMaker.close()
     

if __name__ == '__main__':
  dataProcessor  = pDataProcessor()
  dataProcessor.openFile('/data/IsocData/lsf/00003521-0b3a63a8-03bc-0000-00da.lsf')
  dataProcessor.startProcessing(1000)
