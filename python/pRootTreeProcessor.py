#! /bin/env python

## @package pRootTreeProcessor
## @brief Module responsible for processing the output ROOT tree and creating
#  all the requested plots.

import pSafeLogger
logger = pSafeLogger.getLogger('pRootTreeProcessor')

import os
import time
import sys

from pXmlParser              import pXmlParser
from pGlobals                import *
from pFastMonReportGenerator import pFastMonReportGenerator
from pSafeROOT               import ROOT


## @brief Implementation of the ROOT tree processor.

class pRootTreeProcessor:

    ## @brief Constructor.
    ## @param self
    #  The class instance.
    ## @param xmlParser
    #  The xml parser containing the requested output lists.
    ## @param inputRootFilePath
    #  Path to the input ROOT file.
    ## @param outputFilePath
    #  Path to the output ROOT file.
    ## @param generateReport
    #  Flag to generate the report at the end of the analysis.
    ## @param reportDirPath
    #  The output directory for the report.
    ## @param inputErrorsFilePath
    #  The input file containing the error summary from the data processor.
    ## @param forceOverwrite
    #  Flag passed to test report generator.
    ## @param verbose
    #  Flag passed to the test report generator.
    
    def __init__(self, xmlParser, inputRootFilePath, outputFilePath=None,
                 generateReport=False, reportDirPath=None,\
                 inputErrorsFilePath=None, forceOverwrite=False,\
                 verbose=False):

        ## @var __XmlParser
        ## @brief The xml parser containing the requested output lists.

        ## @var __InputRootFilePath
        ## @brief Path to the input ROOT TFile object.

        ## @var __InputRootFile
        ## @brief The input ROOT TFile object.

        ## @var __OutputFilePath
        ## @brief Path to the output ROOT file.

        ## @var __GenerateReport
        ## @brief Flag to generate the report at the end of the analysis.

        ## @var __ReportDirPath
        ## @brief The output directory for the report.

        ## @var __InputErrorsFilePath
        ## @brief The input file containing the error summary from the
        #  data processor.

        ## @var __ForceOverwrite
        ## @brief Flag passed to test report generator.

        ## @var __Verbose
        ## @brief Flag passed to the test report generator.

        ## @var __OutputRootFile
        ## @brief The output ROOT TFile object.

        ## @var __RootTree
        ## @brief The ROOT TTree object to be read from the input file.
        
        self.__XmlParser           = xmlParser
        self.__InputRootFilePath   = inputRootFilePath
        self.__InputRootFile       = ROOT.TFile(inputRootFilePath)
        self.__OutputFilePath      = outputFilePath
        if self.__OutputFilePath is None:
            self.__OutputFilePath  =\
                 self.__InputRootFilePath.replace('.root', '_processed.root')
        self.__GenerateReport      = generateReport
        self.__ReportDirPath       = reportDirPath
        self.__InputErrorsFilePath = inputErrorsFilePath
        if self.__InputErrorsFilePath is None:
            self.__InputErrorsFilePath =\
                 self.__InputRootFilePath.replace('.root', '.errors')
        self.__ForceOverwrite      = forceOverwrite
        self.__Verbose             = verbose
        self.__OutputRootFile      = None
        self.__RootTree            = self.__getRootTree()

    ## @brief Dive into the input ROOT file and try and get the ROOT tree.
    ## @param self
    #  The class instance.
    
    def __getRootTree(self):
        rootTree = self.__InputRootFile.Get(ROOT_TREE_NAME)
        if rootTree is None:
            sys.exit('Could not find the %s ROOT tree in the input file %s.' %\
                     (ROOT_TREE_NAME, self.__InputRootFile.GetName()))
        else:
            return rootTree

    ## @brief Open the output ROOT file.
    ## @param self
    #  The class instance.

    def openOutputFile(self):
        self.__OutputRootFile = ROOT.TFile(self.__OutputFilePath, 'recreate')

    ## @brief Close the output ROOT file.
    ## @param self
    #  The class instance.

    def closeOutputFile(self):
        self.__OutputRootFile.Write()
        self.__OutputRootFile.Close()

    ## @param self
    #  The class instance.

    def process(self):
        logger.info('Processing the root tree and writing histograms...')
        startTime = time.time()
        self.openOutputFile()
        self.__createObjects()
        logger.info('Done in %.2f s.\n' % (time.time() - startTime))
        self.closeOutputFile()
        if self.__GenerateReport:
            self.generateReport()

    ## @brief Generate the report.
    ## @param self
    #  The class instance.

    def generateReport(self):
        reportGenerator = pFastMonReportGenerator(self.__XmlParser,
                                               self.__OutputFilePath,
                                               self.__InputErrorsFilePath,
                                               None,
                                               self.__ReportDirPath,
                                               self.__Verbose)
        reportGenerator.run()

    ## @brief Create the ROOT objects defined in the enabled output lists
    #  of the xml configuration file.
    ## @param self
    #  The class instance.

    def __createObjects(self):
        for rep in self.__XmlParser.EnabledPlotRepsDict.values():
            rep.createRootObjects(self.__RootTree)



if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage='usage: %prog [options] data_file')
    parser.add_option('-c', '--config-file', dest='config_file',\
                      default=None, type=str,   \
                      help='path to the input xml configuration file')
    parser.add_option('-o', '--output-file', dest='output_file',
                      default=None, type=str,
                      help='path to the output ROOT file')
    parser.add_option('-r', '--create-report', action='store_true',
                      dest='create_report', default=False,
                      help='generate the report from the processed ROOT file')
    parser.add_option('-d', '--report-dir', dest='report_dir',
                      default=None, type=str,
                      help='path to the output report directory')
    parser.add_option('-e', '--errors-file', dest='errors_file',\
                      default=None, type=str,   \
                      help='path to the event errors file')
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

    xmlParser = pXmlParser(options.config_file)
    processor = pRootTreeProcessor(xmlParser, args[0], options.output_file,
                                   options.create_report, options.report_dir,
                                   options.errors_file,
                                   options.force_overwrite, options.verbose)
    processor.process()


    



