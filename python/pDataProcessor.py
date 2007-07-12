#! /bin/env python

## @package pDataProcessor
## @brief Basic module for data processing.

import pSafeLogger
logger = pSafeLogger.getLogger('pDataProcessor')

import os
import sys
import time
import LDF
import struct

from copy 			      import copy
from LICOS_Scripts.analysis.LsfMerger import LsfMerger
from eventFile			      import LSEReader, LSE_Info
from pFastMonTreeMaker                import pFastMonTreeMaker
from pLATdatagramIterator             import pLATdatagramIterator
from pLATcontributionIterator         import pLATcontributionIterator
from pEBFeventIterator                import pEBFeventIterator
from pXmlParser                       import pXmlParser
from pGlobals			      import *
from pContributionIteratorWriter      import pTKRcontributionIteratorWriter
from pContributionIteratorWriter      import pCALcontributionIteratorWriter
from pContributionIteratorWriter      import pAEMcontributionIteratorWriter
from pContributionWriter              import pGEMcontributionWriter
from pMetaEventProcessor	      import pMetaEventProcessor
from pEvtMetaContextProcessor	      import pEvtMetaContextProcessor
from pErrorHandler                    import pErrorHandler
from pFastMonTreeProcessor            import pFastMonTreeProcessor
from pFastMonReportGenerator          import pFastMonReportGenerator
from pSafeROOT                        import ROOT


## @brief The data processor implementation.

class pDataProcessor:

    ## @brief Constructor.
    ## @param self
    #  The class instance.
    ## @param configFilePath
    #  Path to the xml configuration file path.
    ## @param inputFilePath
    #  Path to the input raw data file.
    ## @param outputFilePath
    #  Path to the output ROOT file.
    ## @param generateReport
    #  Flag to generate a report at the end of the analysis.
    ## @param reportDirPath
    #  The report output directory.
    ## @param forceOverwrite
    #  Flag to overwrite existing files without asking the user.
    ## @param verbose
    #  Print additional informations.

    def __init__(self, inputFilePath, configFilePath=None, outputDir=None,
                 outputFileName=None):

        ## @var XmlParser
        ## @brief The xml parser object (pXmlParser instance).

        ## @var OutputFilePath
        ## @brief The path to the output ROOT file containing the ROOT tree.

        ## @var TreeMaker
        ## @brief The tree maker object (pRootTreeMaker instance).

        ## @var ErrorHandler
        ## @brief The error handler object (pErrorHandler instance).

        ## @var __MetaEventProcessor
        ## @brief The meta event processor (pMetaEventProcessor instance)

        ## @var __EvtMetaContextProcessor
        ## @brief The evt meta context processor (EvtMetaContextProcessor
        ## instance)

        ## @var LatCompIter
        ## @brief The LAT component iterator.

        ## @var EbfEventIter
        ## @brief The EBF event iterator.

        ## @var LatContrIter
        ## @brief The LAT contribution iterator.

        ## @var LatDatagrIter
        ## @brief The LAT datagram iterator.

        ## @var LatDataBufIter
        ## @brief The LAT data buffer iterator.

        ## @var NumEvents
        ## @brief The number of events processed by the data processor
        #  at a given time.

        ## @var LsfMerger
        ## @brief The lsf merger object (relevant for lsf data format only).

        ## @var EvtReader
        ## @brief The EvtReader object created by calling LSEReader(filename)

        ## @var LdfFile
        ## @brief The ldf file object (relevant for ldf data only). 

        ## @var StartTime
        ## @brief The data processor start time.

        ## @var StopTime
        ## @brief The data processor stop time.

        if outputDir is None:
            outputDir = os.path.split(inputFilePath)[0]
        fileName = os.path.split(inputFilePath)[1]
        self.OutputDirPath  = os.path.join(outputDir, fileName.split('.')[0])
        if not os.path.exists(self.OutputDirPath):
            os.makedirs(self.OutputDirPath)
        if outputFileName is None:
            outputFileName   = '%s.root' % fileName.split('.')[0]
        self.OutputFilePath  = os.path.join(self.OutputDirPath, outputFileName)
        self.XmlParser       = pXmlParser(configFilePath)
        self.TreeMaker       = pFastMonTreeMaker(self)
        self.ErrorHandler    = pErrorHandler()
        self.TreeProcessor   = pFastMonTreeProcessor(self)
        self.ReportGenerator = pFastMonReportGenerator(self)
	self.__MetaEventProcessor = pMetaEventProcessor(self.TreeMaker)
	self.__EvtMetaContextProcessor =\
                                  pEvtMetaContextProcessor(self.TreeMaker)
        self.__updateContributionIterators()
        self.__updateContributions()
        from pLATcomponentIterator    import pLATcomponentIterator
        self.LatCompIter    = pLATcomponentIterator(self.TreeMaker,\
                                                    self.ErrorHandler)
        self.EbfEventIter   = pEBFeventIterator(self.LatCompIter)
        self.LatContrIter   = pLATcontributionIterator(self.EbfEventIter)
        self.LatDatagrIter  = pLATdatagramIterator(self.LatContrIter)
        self.LatDataBufIter = LDF.LATdataBufferIterator(self.LatDatagrIter)
        self.NumEvents      = None
        self.LsfMerger      = None
        self.EvtReader      = None
        self.LdfFile        = None
        self.StartTime      = None
        self.StopTime       = None
        self.openFile(inputFilePath)

    ## @brief Update the event contribution iterators, based on the xml
    #  configuration file.
    ## @param self
    #  The class instance.

    def __updateContributionIterators(self):
        writer = pTKRcontributionIteratorWriter(self.XmlParser)
        writer.writeIterator()
        writer = pCALcontributionIteratorWriter(self.XmlParser)
        writer.writeIterator()
        writer = pAEMcontributionIteratorWriter(self.XmlParser)
        writer.writeIterator()

    ## @brief Update the event contributions, based on the xml
    #  configuration file.
    ## @param self
    #  The class instance.

    def __updateContributions(self):
        writer = pGEMcontributionWriter(self.XmlParser)
        writer.writeComponent()

    ## @brief Open the input raw data file.
    #
    #  Both ldf and lsf data files are supported at this level.
    #  The data type is identified based on the file extension.
    ## @param self
    #  The class instance.
    ## @param filePath
    #  Path to the raw data file.
    
    def openFile(self, filePath):
        logger.info('Opening the input data file...')
        if os.path.exists(filePath):
	    fileType = filePath.split('.')[-1]
	    if fileType == 'lsf':
                self.LsfMerger   = LsfMerger(filePath)
	    elif fileType == 'evt':
                self.EvtReader   = LSEReader(filePath)
	    elif fileType == 'ldf':
	        self.LdfFile = file(filePath, 'rb')
	    else:
	    	sys.exit('Unknown file type (%s).' % fileType)
            logger.info('Done.\n')
        else:
            sys.exit('Input data file not found. Exiting...')

    ## @brief Start the data processing.
    ## @param self
    #  The class instance.
    ## @param maxEvents
    #  The maximum number of events to be processed (default is -1, meaning
    #  the whole file).

    def start(self, maxEvents=-1):
        self.NumEvents = 0
        self.StartTime = time.time()
        if self.LsfMerger is not None:
	    self.startLSFProcessing(maxEvents)
        elif self.EvtReader is not None:
	    self.startEvtProcessing(maxEvents)
	elif self.LdfFile is not None:
	    self.startLDFProcessing(maxEvents)
	else:
	    sys.exit('If you see this message, something went really bad...')
        logger.info('End of data processing...')

    ## @brief Finalize the data processing.
    #
    #  This involves creating the histogram from the ROOT tree and
    #  printing out the statistics of the events with errors.
    ## @param self
    #  The class instance.
    
    def finalize(self):
        self.StopTime = time.time()
        elapsedTime   = self.StopTime - self.StartTime
        averageRate   = self.NumEvents/elapsedTime
        self.TreeMaker.close()
        print
        logger.info('Done. %d events processed in %.2f s (%.2f Hz).\n' %\
                     (self.NumEvents, elapsedTime, averageRate))
        self.ErrorHandler.dump(self.OutputFilePath.replace('.root',\
                                                           '.errors.pickle'))
        
    ## @brief Process an event.
    #
    #  This is actually called both for lsf and ldf files.
    ## @param self
    #  The class instance.
    ## @param event
    #  The event object.
 
    def processEvent(self, event):
        self.ErrorHandler.setEventNumber(self.NumEvents)
	self.LatDataBufIter.iterate(event, len(event))
        label = 'processor_event_number'
        self.TreeMaker.VariablesDictionary[label][0] = self.NumEvents
        self.NumEvents += 1
        if not self.NumEvents % 100:
            print '\r%s events processed...' % self.NumEvents,
            sys.stdout.flush()

    ## @brief Process a meta event.
    #
    #  This is relevant for lsf files only.
    ## @param self
    #  The class instance.
    ## @param meta
    #  The meta-event object.

    def processMetaEvent(self, meta):
	self.__MetaEventProcessor.process(meta)

    ## @brief Global event processing sequence for lsf files.
    #
    #  @li reset the tree variables
    #  @li process the meta part of the event 
    #  @li process the event part of the event 
    #  @li fill the tree
    ## @param self
    #  The class instance.
    ## @param meta
    #  The meta-event object.
    ## @param event
    #  The event object.
    
    def processLSF(self, meta, event):
	self.TreeMaker.resetVariables()
        self.processMetaEvent(meta)
        self.processEvent(event)
	self.TreeMaker.fillTree()

    ## @brief Start the event loop for lsf files.
    ## @param self
    #  The class instance.
    ## @param maxEvents
    #  The maximum number of events.
    
    def startLSFProcessing(self, maxEvents):
        while (self.NumEvents != maxEvents):
            try:
                (meta, buff) = self.LsfMerger.getUncompressedEvent()
            except TypeError:
                logger.info('End of file reached.')
                break
            self.processLSF(meta, buff)
        self.finalize()

    ## @brief Print header information of an evt file
    #
    #  This is relevant for evt files only.
    ## @param self
    #  The class instance.

    def evtPrintHeader(self):
	print "\n----------------------"
	print "Reading evt file header"
        print "Run Id\t\t",     self.EvtReader.runid()
        print "Events\t\t",     self.EvtReader.evtcnt()
        print "Begin GEM\t",    self.EvtReader.begGEM()
        print "End GEM\t\t",    self.EvtReader.endGEM()
        print "Begin Second\t", self.EvtReader.begSec()
        print "End Second\t",   self.EvtReader.endSec()
        print "----------------------\n"

    ## @brief Process the context of an evt meta event.
    #
    #  This is relevant for evt files only.
    ## @param self
    #  The class instance.
    ## @param meta
    #  The meta info of the event
    ## @param context
    #  The context info of the event from evt.ctx(), as it's not
    #  directly accessible from meta.context() in this case

    def processEvtContext(self, meta, context):
	self.__EvtMetaContextProcessor.process(meta, context)

    ## @brief Special event processing for evt files.
    ## @param self
    #  The class instance.
    ## @param meta
    #  The meta-event object for time stamp processing
    ## @param context
    #  The meta context info object 
    ## @param buff
    #  The buff object of type LDF.EBFeventIterator
    
    def processEvt(self, meta, context, buff):
	self.TreeMaker.resetVariables()	
	self.ErrorHandler.setEventNumber(self.NumEvents)
        self.processEvtContext(meta, context)	
	self.EbfEventIter.iterate(buff, len(buff), False)	
	label = 'processor_event_number'
	self.TreeMaker.VariablesDictionary[label][0] = self.NumEvents
	self.NumEvents += 1
	if not self.NumEvents % 100:
		print '\r%s events processed...' % self.NumEvents,
            	sys.stdout.flush()
	self.TreeMaker.fillTree()

    ## @brief Start the event loop for evt files.
    ## @param self
    #  The class instance.
    ## @param maxEvents
    #  The maximum number of events.
    ## @todo check different evt.infotype cases or do something smarter
    
    def startEvtProcessing(self, maxEvents):
        self.__EvtMetaContextProcessor.setEvtReader(self.EvtReader)
        while (self.NumEvents != maxEvents):
            evt = self.EvtReader.nextEvent()
            if evt.isNull():
                logger.info("End of File reached.")
                break
            if evt.infotype() == LSE_Info.LPA:
                meta = evt.pinfo()
            elif evt.infotype() == LSE_Info.ACD:
                meta = evt.ainfo()
            elif evt.infotype() == LSE_Info.CAL:
                meta = evt.cinfo()
            elif evt.infotype() == LSE_Info.TKR:
                meta = evt.tinfo()
            elif evt.infotype() == LSE_Info.LCI_ACD:
            	meta = evt.ainfo()
            elif evt.infotype() == LSE_Info.LCI_CAL:
            	meta = evt.cinfo()
            elif evt.infotype() == LSE_Info.LCI_TKR:
            	meta = evt.tinfo()	      
            else:
                meta = None
	    context = evt.ctx()
	    buff = evt.ebf().copyData()
	    self.processEvt(meta, context, buff)
        self.finalize()

    ## @brief Global event processing sequence for ldf files.
    #
    #  @li reset the tree variables
    #  @li process the event part of the event 
    #  @li fill the tree
    ## @param self
    #  The class instance.
    ## @param event
    #  The event object.

    def processLDF(self, event):
	self.TreeMaker.resetVariables()
        self.processEvent(event)
	self.TreeMaker.fillTree()

    ## @brief Start the event loop for ldf files.
    ## @param self
    #  The class instance.
    ## @param maxEvents
    #  The maximum number of events.
    
    def startLDFProcessing(self, maxEvents):
        while (self.NumEvents != maxEvents):
    	    event = self.LdfFile.read(8)
    	    if len(event) < 8:
    	      logger.info("End of File reached.")
              break
    	    else:
    	      (identity, length) = struct.unpack('!LL', event)
    	      event += self.LdfFile.read(length - 8)
	      self.processLDF(event)
        self.finalize()
     

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage='usage: %prog [options] data_file')
    parser.add_option('-c', '--config-file', dest='config_file',
                      default=None, type=str,
                      help='path to the input xml configuration file')
    parser.add_option('-n', '--num-events', dest='events',
                      default=-1, type=int,
                      help='number of events to be processed')
    parser.add_option('-o', '--output-file', dest='output_file',
                      default=None, type=str,
                      help='name of the output ROOT file')
    parser.add_option('-d', '--output-dir', dest='output_dir',
                      default=None, type=str,
                      help='path to the output directory')
    parser.add_option('-p', '--process-tree', action='store_true',
                      dest='process_tree', default=False,
                      help='process the ROOT tree and create histograms')
    parser.add_option('-r', '--create-report', action='store_true',
                      dest='create_report', default=False,
                      help='generate the report from the processed ROOT file')
    parser.add_option('-f', '--force-overwrite', action='store_true',
                      dest='force_overwrite', default=False,
                      help='overwrite existing files without asking')
    parser.add_option('-v', '--verbose', action='store_true',
                      dest='verbose', default=False,
                      help='print a lot of ROOT/doxygen/LaTeX related stuff')
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.print_help()
        parser.error('incorrect number of arguments')
        sys.exit()
    if options.create_report and not options.process_tree:
        parser.print_help()
        parser.error('please run with the -p option if you want the report.')
    dataProcessor  = pDataProcessor( args[0],options.config_file,
                                     options.output_dir,
                                     options.output_file)
    dataProcessor.start(options.events)
    if options.process_tree:
        dataProcessor.TreeProcessor.run()
    if options.create_report:
        dataProcessor.ReportGenerator.run()

