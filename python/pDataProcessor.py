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

    def __init__(self, inputFilePath, configFilePath = None,
                 outputFilePath = None, outputProcessedFilePath = None,
                 outputErrorFilePath = None, inputMagic7FilePath = None,
                 saaDefinitionFile = None):

        ## @var XmlParser
        ## @brief The xml parser object (pXmlParser instance).

        ## @var OutputFilePath
        ## @brief The path to the output ROOT file containing the ROOT tree.

        ## @var TreeMaker
        ## @brief The tree maker object (pRootTreeMaker instance).

        ## @var ErrorHandler
        ## @brief The error handler object (pErrorHandler instance).

        ## @var MetaEventProcessor
        ## @brief The meta event processor (pMetaEventProcessor instance)

        ## @var EvtMetaContextProcessor
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

        ## @var PrevTimestamp
        ## @brief The time stamp of the previous event, initialized to 0.

        logger.info('Starting Data Processor.')
	logger.info('Using LDF Version : %s - %s - %s', LDF.LDF_VERSION_STR,
                    LDF.LDF_VERSION, LDF.__file__)
        
        self.InputFilePath = inputFilePath
        if outputFilePath is None:
            logger.info('Output file path not specified.')
            logger.info('All output files will be saved in the input folder.')
            self.OutputDirPath  = os.path.split(self.InputFilePath)[0]
            self.OutputFilePath = '%s.root' % self.InputFilePath.split('.')[0]
        else:
            outputDirPath  = os.path.split(outputFilePath)[0]
            self.OutputFilePath = outputFilePath
        if not os.path.exists(outputDirPath):
            os.makedirs(outputDirPath)
            logger.debug('Creating new directory to store output files: %s' %\
                         outputDirPath )
        self.OutputProcessedFilePath = outputProcessedFilePath
        self.OutputErrorFilePath = outputErrorFilePath
        if self.OutputErrorFilePath is None:
            self.OutputErrorFilePath = self.OutputFilePath.replace('.root',\
                                       '.errors.xml')
        self.XmlParser       = pXmlParser(configFilePath)
        self.TreeMaker       = pFastMonTreeMaker(self)
        self.ErrorHandler    = pErrorHandler()
        self.TreeProcessor   = pFastMonTreeProcessor(self.XmlParser,\
                               self.TreeMaker.OutputFilePath,\
                               self.OutputProcessedFilePath)
        self.M7Parser = None
        self.GeomagProcessor = None
        if inputMagic7FilePath is not None:
            from pGeomagProcessor   import pGeomagProcessor
            from pM7Parser          import pM7Parser
            from IGRF               import IGRF
            logger.info('Using magic7 file : %s' % inputMagic7FilePath)
            self.M7Parser = pM7Parser(inputMagic7FilePath, saaDefinitionFile)
            self.GeomagProcessor = pGeomagProcessor(self.TreeMaker)
        if self.M7Parser is None:
            logger.error('pDataProcessor started without magic7 information.')
            logger.error('Are you sure?')
        if self.OutputProcessedFilePath is not None:
            self.ReportGenerator = pFastMonReportGenerator(self)
	self.MetaEventProcessor = pMetaEventProcessor(self.TreeMaker)
	self.EvtMetaContextProcessor =\
                                     pEvtMetaContextProcessor(self.TreeMaker,\
                                                             self.ErrorHandler)
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
	self.PrevTimestamp  = 0

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

    def startProcessing(self, maxNumEvents = -1):
        logger.info('Opening data file %s...' % self.InputFilePath)
        if not os.path.exists(self.InputFilePath):
            sys.exit('Input data file not found. Abort.')
        fileType = self.InputFilePath.split('.')[-1]
        logger.info('Processing started on %s.' % time.asctime())
        self.NumEvents = 0
        self.StartTime = time.time()
        if fileType   == 'lsf':
            self.LsfMerger = LsfMerger(self.InputFilePath)
            self.startLSFProcessing(maxNumEvents)
        elif fileType == 'evt':
            self.EvtReader = LSEReader(self.InputFilePath)
            self.startEvtProcessing(maxNumEvents)
        elif fileType == 'ldf':
            self.LdfFile   = file(self.InputFilePath, 'rb')
            self.startLDFProcessing(maxNumEvents)
        else:
            sys.exit('Unknown file type (%s).' % fileType)
        logger.info('Data processing complete.')

    ## @brief Start the event loop for lsf files.
    ## @param self
    #  The class instance.
    ## @param maxEvents
    #  The maximum number of events.
    
    def startLSFProcessing(self, maxEvents):
        while (self.NumEvents != maxEvents):
            try:
                (meta, event) = self.LsfMerger.getUncompressedEvent()
            except TypeError:
                logger.info('End of file reached.')
                break
            self.MetaEventProcessor.process(meta)
            self.processEvent(event)
        self.finalize()

    ## @brief Start the event loop for evt files.
    ## @param self
    #  The class instance.
    ## @param maxEvents
    #  The maximum number of events.
    ## @todo check different evt.infotype cases or do something smarter
    
    def startEvtProcessing(self, maxEvents):
        self.EvtMetaContextProcessor.setEvtReader(self.EvtReader)
        while (self.NumEvents != maxEvents):
            evt = self.EvtReader.nextEvent()
            if evt.isNull():
                logger.info("End of File reached.")
                break
            if evt.infotype() == LSE_Info.LPA:
                meta = evt.pinfo()
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
              self.__preEvent()
              self.LatDataBufIter.iterate(event, len(event))
              self.TreeMaker.getVariable('meta_context_gem_scalers_sequence')[0] = self.NumEvents
              self.__postEvent()
              #self.processEvent(event)
        self.finalize()

    ## @brief Process an event.
    #
    #  This is actually called both for lsf and ldf files.
    ## @param self
    #  The class instance.
    ## @param event
    #  The event object.
 
    def processEvent(self, event):
        self.__preEvent()
	self.LatDataBufIter.iterate(event, len(event))
        self.__postEvent()

    ## @brief Special event processing for evt files.
    ## @param self
    #  The class instance.
    ## @param meta
    #  The meta-event object for time stamp processing
    ## @param context
    #  The meta context info object 
    ## @param buff
    #  The buff object of type LDF.EBFeventIterator
    #
    # If a magic7 file is provided, the space craft position and the
    # corresponding geomagnetic quantities are updated every 5 seconds
    
    def processEvt(self, meta, context, buff):
        self.__preEvent()
        self.EvtMetaContextProcessor.process(meta, context)
	self.EbfEventIter.iterate(buff, len(buff), False)
        timestamp = self.TreeMaker.getVariable('event_timestamp')
        if self.M7Parser is not None and self.M7Parser.HasData:
	    if (timestamp - self.PrevTimestamp) > 5:
                position = self.M7Parser.getSCPosition((timestamp, 0))
                self.GeomagProcessor.process(position)
	        # Need to copy the value, not to let python use a reference !
		self.PrevTimestamp = copy(timestamp)
        self.__postEvent(buff)

    def __preEvent(self):
        self.TreeMaker.resetVariables()
	self.TreeMaker.VariablesDictionary['processor_event_number'][0] =\
                       self.NumEvents

    ## @brief Post event processing 
    #
    #  where the Tree is filled and the Errors are dumped to the xml
    ## @param self
    #  The class instance.
    ## @param buff
    #  The buff object of type LDF.EBFeventIterator
    #
    ## FASTMON_DUMP_ERRORS_TO_FILE is defined in Common/python/pGlobals
    #  if set to True, FastMon will dump events with at least one error to a
    #  file.
    #  Use for debugging purpose only.
    
    def __postEvent(self, buff):        
        # Try/Except in case the variable is not even defined for backward
        # compatibility
	try:
	    if FASTMON_DUMP_ERRORS_TO_FILE and \
                    self.ErrorHandler.ErrorsBuffer != []:
	        self.__dumpEventToFile(buff)
        except:
	    pass

        error_summary = self.ErrorHandler.flushErrorsBuffer(\
             self.TreeMaker.getVariable('meta_context_gem_scalers_sequence')[0])
	self.TreeMaker.getVariable('error_summary')[0]=error_summary
	
        self.TreeMaker.fillTree()
	self.NumEvents += 1
	if not self.NumEvents % 100:
            elapsedTime = time.time() - self.StartTime
            averageRate = self.NumEvents/elapsedTime
            print '\r%s events processed in %.2f s (average rate %.2f Hz).' %\
                  (self.NumEvents, elapsedTime, averageRate),
            sys.stdout.flush()
      
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

	# For the ErrorHandler get the number of seconds elapsed, assuming
        # counters are fine... 
	tmin = self.TreeMaker.RootTree.GetMinimum("event_timestamp")
	tmax = self.TreeMaker.RootTree.GetMaximum("event_timestamp")
	delta_time = int(tmax-tmin)
	#Now closing the TTree
	self.TreeMaker.close()

        logger.info('Processing stopped on %s.' % time.asctime())
        logger.info('%d events processed in %.2f s (%.2f Hz).\n' %\
                    (self.NumEvents, elapsedTime, averageRate))
	
        self.ErrorHandler.NumProcessedEvents = self.NumEvents
        self.ErrorHandler.SecondsElapsed     = delta_time
        self.ErrorHandler.writeXmlOutput(self.OutputErrorFilePath)

    ## @brief Dump an event buffer to a file
    #
    ## @param self
    #  The class instance.
    ## @param buff
    #  The buff object of type LDF.EBFeventIterator
    #
    ## This function is now used only to dump event with an error to a separate
    #  file.
    
    def __dumpEventToFile(self, buff):       
       evtnum = self.TreeMaker.getVariable('meta_context_gem_scalers_sequence')
       fname = 'Err_'+self.InputFilePath.split('/')[-1][:-3]+'ebf'
       outputDirPath  = os.path.split(self.OutputFilePath)[0]
       fpath = os.path.join(outputDirPath, fname)
       logger.debug('Writing event %d with errors to file' % evtnum)
       logger.debug('Output Error File %s' % fpath)
       f = file(fpath, 'ab')
       f.write(buff)
       f.close()       


    ## @brief Write an xml summary file with run statistics
    #
    ## @param self
    #  The class instance.
    ## @param xmlFilePath
    #  The path to the xml summary file
    
    def writeXmlSummary(self, xmlFilePath):
        from pXmlWriter import pXmlWriter
        logger.info('Writing summary xml file: %s.' % xmlFilePath)
        elapsedTime   = self.StopTime - self.StartTime
        averageRate   = self.NumEvents/elapsedTime

        writer = pXmlWriter(xmlFilePath)
        writer.openTag('pDataProcessorSummary')
        writer.indent()
        writer.writeTag('num_events', {}, self.NumEvents)
        writer.writeTag('elapsed_time', {}, elapsedTime)
        writer.writeTag('average_rate', {}, averageRate)
        #writer.writeTag('current_time', {}, time.asctime())
        writer.backup()
        writer.closeTag('pDataProcessorSummary')
        writer.closeFile()


    
if __name__ == '__main__':
    from pOptionParser import pOptionParser
    optparser = pOptionParser('cnorvVpems', 1, 1, False)
    if optparser.Options.o == None:
        optparser.error('the -o option is mandatory. Exiting...')
    if optparser.Options.p == optparser.Options.o:
        optparser.error("The output file and the processed (histogram) file"+\
                        " can't be the same file. Exiting...")
    if optparser.Options.r and optparser.Options.p == None:
        optparser.error('cannot use the -r option without -p')
    dataProcessor = pDataProcessor(optparser.Argument, optparser.Options.c,\
                                   optparser.Options.o, optparser.Options.p,\
                                   optparser.Options.e, optparser.Options.m,
                                   optparser.Options.s)
    dataProcessor.startProcessing(optparser.Options.n)
    if optparser.Options.p != None:
        dataProcessor.TreeProcessor.run()
    if optparser.Options.r:
        dataProcessor.ReportGenerator.run(optparser.Options.v)
    if optparser.Options.V:
        dataProcessor.ReportGenerator.viewReport()
        

