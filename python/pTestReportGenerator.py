#! /bin/env python

## @package pTestReportGenerator
## @brief Package for generating test reports.


import os
import sys
import logging
import pConfig
import ROOT
import commands
import time

from pXmlParser import pXmlParser


## @brief Implementation of the test report generator.

class pTestReportGenerator:

    ## @var __DOXY_CONFIG_FILE_NAME
    ## @brief Name of the doxygen configuration file.

    ## @var __DOXY_MAIN_FILE_NAME
    ## @brief Name of the doxygen main page file.

    ## @var __HTML_DIR_NAME
    ## @brief Name of the html report dir.

    ## @var __LATEX_DIR_NAME
    ## @brief Name of the LaTeX report dir.

    ## @var __ROOT_PALETTE
    ## @brief The ROOT palette.

    ## @var __AUX_CANVAS_WIDTH
    ## @brief The width of the auxiliary ROOT canvas used to save plots as
    #  images (in number of pixels).

    ## @var __AUX_CANVAS_HEIGHT
    ## @brief The height of the auxiliary ROOT canvas used to save plots as
    #  images (in number of pixels).

    ## @var __AUX_CANVAS_COLOR
    ## @brief The fill color of the ROOT auxiliary canvas.

    ## @var __LATEX_IMAGES_WIDTH
    ## @brief The width of the images to be included in the LaTeX version
    #  of the report (in cm).

    __DOXY_CONFIG_FILE_NAME = 'config.doxygen'
    __DOXY_MAIN_FILE_NAME   = 'mainpage.doxygen'
    __HTML_DIR_NAME         = 'html'
    __LATEX_DIR_NAME        = 'latex'
    __ROOT_PALETTE          = 1
    __AUX_CANVAS_WIDTH      = 500
    __AUX_CANVAS_HEIGHT     = 400
    __AUX_CANVAS_COLOR      = 10
    __LATEX_IMAGES_WIDTH    = 11.0

    ## @brief Constructor.
    ## @param self
    #  The class instance.
    ## @param inputRootFilePath
    #  Path to the input ROOT file containing the ROOT plots.
    ## @param outputDirPath
    #  Path to the output directory for the report.
    ## @param xmlParser
    #  The pXmlParser object containing the information about the
    #  data processor configuration.
    ## @param forceOverwrite
    #  Flag to overwrite existing files without asking the user.
    ## @param verbose
    #  Print additional informations.

    def __init__(self, xmlParser, inputRootFilePath, outputDirPath=None,
                 forceOverwrite=False, verbose=False):

        ## @var __InputRootFilePath
        ## @brief Path to the input ROOT file containing the ROOT plots.

        ## @var __OutputDirPath
        ## @brief Path to the output directory for the report.

        ## @var __XmlParser
        ## @brief The pXmlParser object containing the information about the
        #  data processor configuration.

        ## @var __ForceOverwrite
        ## @brief Flag to overwrite existing files without asking the user.

        ## @var __HtmlDirPath
        ## @brief Path to the html report directory.

        ## @var __LatexDirPath
        ## @brief Path to the LaTeX report directory.

        ## @var __DoxyMainFile
        ## @brief Doxygen main page file.

        ## @var __InputRootFile
        ## @brief The input ROOT Tfile object.

        ## @var __AuxRootCanvas
        ## @brief A temporary canvas used to draw the plots and save them
        #  as images.

        self.__XmlParser         = xmlParser
        self.__InputRootFilePath = inputRootFilePath
        self.__OutputDirPath     = outputDirPath
        if self.__OutputDirPath is None:
            inputFileDirPath     = os.path.dirname(self.__InputRootFilePath)
            self.__OutputDirPath = os.path.join(inputFileDirPath, 'report')
        self.__Verbose           = verbose
        self.__ForceOverwrite    = forceOverwrite
        self.__HtmlDirPath       = os.path.join(self.__OutputDirPath,\
                                                self.__HTML_DIR_NAME)
        self.__LatexDirPath      = os.path.join(self.__OutputDirPath,\
                                                self.__LATEX_DIR_NAME)
        self.__DoxyMainFile      = None
        self.__InputRootFile     = None
        self.__AuxRootCanvas     = None
        self.fuckRoot()

    ## @brief This function is intended to fool ROOT...
    #
    #  If a valid folder path is passed as one of the arguments to the
    #  python script, ROOT cd into it the first time ROOT itself is called.
    #
    #  By the way... we set the ROOT.gStyle palette here!
    ## @brief self
    #  The class instance.

    def fuckRoot(self):
        currentDirPath = os.path.abspath(os.curdir)
        ROOT.gStyle.SetPalette(self.__ROOT_PALETTE)
        os.chdir(currentDirPath)

    ## @brief Produce the report in html, ps and pdf formats.
    ## @param self
    #  The class instance.

    def run(self):
        self.createDirs()
        self.writeReport()
        self.doxygenate()
        self.compileLatex()

    ## @brief Create the output directory for the report.
    ## @param self
    #  The class instance.
    ## @param force
    #  If this flag is set, existing files are overwritten without prompting.
    
    def __createOutputDir(self, force=False):
        if os.path.exists(self.__OutputDirPath):
            if not self.__ForceOverwrite:
                logging.warn('Output directory already exists.')
                answer = None
                while answer not in ['y', 'n']:
                    answer = raw_input('Do you want to overwrite the old ' +\
                                       'files (y or n)?\n')
                if answer == 'n':
                    sys.exit('Aborting...')
            os.system('rm -rf %s' % self.__OutputDirPath)
        os.makedirs(self.__OutputDirPath)

    ## @brief Create the output html report directory.
    ## @param self
    #  The class instance.
    
    def __createHtmlDir(self):
        os.makedirs(self.__HtmlDirPath)

    ## @brief Create the output LaTeX report directory.
    ## @param self
    #  The class instance.

    def __createLatexDir(self):
        os.makedirs(self.__LatexDirPath)

    ## @brief Create all the necessary output directories.
    ## @param self
    #  The class instance.
    
    def createDirs(self):
        self.__createOutputDir()
        self.__createHtmlDir()
        self.__createLatexDir()

    ## @brief Open a generic file in write mode.
    ## @param self
    #  The class instance.
    ## @param filePath
    #  The file path.

    def __openOutputFile(self, filePath):
        try:
            return file(filePath, 'w')
        except:
            sys.exit('Could not open output file %s' % filePath)

    ## @brief Open the ROOT input TFile object containing the plots.
    ## @param self
    #  The class instance.

    def __openInputRootFile(self):
        rootFile = ROOT.TFile(self.__InputRootFilePath)
        if rootFile.GetFd() != -1:
            return rootFile
        else:
            sys.exit('Could not open input ROOT file %s. Aborting...' %\
                     self.__InputRootFilePath)

    ## @brief Create the doxygen configuration file.
    ## @param self
    #  The class instance.  

    def createDoxyConfigFile(self):
        fileContent = 'FILE_PATTERNS = %s\n'   % self.__DOXY_MAIN_FILE_NAME
        filePath    = os.path.join(self.__OutputDirPath,\
                                   self.__DOXY_CONFIG_FILE_NAME)
        configFile  = self.__openOutputFile(filePath)
        configFile.writelines(fileContent)
        configFile.close()

    ## @brief Open the doxygen main page file.
    ## @param self
    #  The class instance.

    def openDoxyMainFile(self):
        filePath = os.path.join(self.__OutputDirPath,\
                                self.__DOXY_MAIN_FILE_NAME)
        self.__DoxyMainFile = self.__openOutputFile(filePath)

    ## @brief Close the doxygen main page file.
    ## @param self
    #  The class instance.
    
    def closeDoxyMainFile(self):
        self.__DoxyMainFile.close()


    ## @brief Write a line to the doxygen main page file.
    ## @param self
    #  The class instance.
    ## @param line
    #  The ilne to be written.

    def __write(self, line):
        self.__DoxyMainFile.writelines(line)

    ## @brief Write a carriage return to the doxygen main page file.
    ## @param self
    #  The class instance.  

    def __skipLine(self):
        self.__write('\n')

    ## @brief Write the header in the doxygen main page file.
    ## @param self
    #  The class instance.

    def writeHeader(self):
        header = '/** @mainpage Fast monitor report\n'                    +\
                 '@htmlonly\n'                                            +\
                 '<center>\n'                                             +\
                 '<a href="../latex/refman.ps" > PS report  </a> &nbsp\n' +\
                 '<a href="../latex/refman.pdf"> PDF report </a>\n'       +\
                 '</center>\n'                                            +\
                 '@endhtmlonly\n'                                         +\
                 '@author{automatically generated}\n'
        self.__write(header)
        self.__skipLine()
        
    ## @brief Write the trailer in the doxygen main page file.
    ## @param self
    #  The class instance.

    def writeTrailer(self):
        self.__skipLine()
        self.__write('*/')

    ## @brief Add a section to the doxygen main page file.
    ## @param self
    #  The class instance.
    ## @param label
    #  The section label.
    ## @param name
    #  The section name.

    def addSection(self, label, name):
        self.__skipLine()
        self.__write('@section %s %s\n' % (label, name))
        self.__skipLine()

    ## @brief Add a section corresponding to a particular output list
    #  to the doxygen main page file.
    ## @param self
    #  The class instance.
    ## @param list
    #  The pXmlOutputList object.

    def addOutputListSection(self, list):
        name  = list.Name
        label = name.replace(' ', '_')
        self.addSection(label, name)

    ## @brief Add a plot to the doxygen main page file.
    ## @todo There's room for improvements, here (in particular one
    #  could write a method in pXmlPlotRep to return a list of plot reps
    #  for all the levels - with their names, titles, etc - and avoid
    #  the name parameter in this function).
    ## @todo Try and understand how to get rid of the ROOT info output
    #  while saving to eps format.
    ## @param self
    #  The class instance.
    ## @param plotRep
    #  The pXmlPlotRep object representing the plot.
    ## @param name
    #  The plot name (needs to be passed because it may be different for all
    #  the towers/layers).
    
    def addPlot(self, plotRep, name):
        epsImagePath = os.path.join(self.__LatexDirPath, ('%s.eps' % name))
        gifImagePath = os.path.join(self.__HtmlDirPath , ('%s.gif' % name))
        epsImageName = os.path.basename(epsImagePath)
        gifImageName = os.path.basename(gifImagePath)
        self.__AuxRootCanvas.SetLogx(plotRep.XLog)
        self.__AuxRootCanvas.SetLogy(plotRep.YLog)
        self.__InputRootFile.Get(name).Draw(plotRep.DrawOptions)
        self.__AuxRootCanvas.SaveAs(epsImagePath)
        self.__AuxRootCanvas.SaveAs(gifImagePath)
        title   = plotRep.Title
        caption = plotRep.Caption
        block   = ('@htmlonly\n'                                       +\
                   '<div align="center">\n'                            +\
                   '<p><strong>%s.</strong> %s</p>\n'                  +\
                   '<img src="%s" alt="%s">\n'                         +\
                   '</div>\n'                                          +\
                   '@endhtmlonly\n'                                    +\
                   '@latexonly\n'                                      +\
                   '\\begin{figure}[H]\n'                              +\
                   '\\begin{center}\n'                                 +\
                   '\\includegraphics[width=%scm]{%s}\n'               +\
                   '\\caption{{\\bf %s.} %s}\n'                        +\
                   '\\end{center}\n'                                   +\
                   '\\end{figure}\n'                                   +\
                   '@endlatexonly\n'                                   +\
                   '@latexonly\n'                                      +\
                   '\\nopagebreak\n'                                   +\
                   '@endlatexonly\n\n')                                %\
                   (title, caption, gifImageName, gifImageName,         \
                    self.__LATEX_IMAGES_WIDTH, epsImageName, title, caption)
        self.__write(block)

    ## @brief Add all the plots to the test report.
    ## @param self
    #  The class instance.
    
    def addPlots(self):
        ROOT.gROOT.SetBatch(1)
        self.__InputRootFile = self.__openInputRootFile()
        self.__AuxRootCanvas = ROOT.TCanvas('canvas', 'canvas',\
                                            self.__AUX_CANVAS_WIDTH,\
                                            self.__AUX_CANVAS_HEIGHT)
        self.__AuxRootCanvas.SetFillColor(self.__AUX_CANVAS_COLOR)
        for list in self.__XmlParser.OutputListsDict.values():
            self.addOutputListSection(list)
            for plotRep in list.EnabledPlotRepsDict.values():
                for name in plotRep.getRootObjectsName():
                    self.addPlot(plotRep, name)
        self.__InputRootFile.Close()
        self.__AuxRootCanvas.Delete()
        ROOT.gROOT.SetBatch(0)

    ## @brief Write the actual doxygen files.
    ## @param self
    #  The class instance.
    
    def writeReport(self):
        self.createDoxyConfigFile()
        self.openDoxyMainFile()
        self.writeHeader()
        self.addPlots()
        self.writeTrailer()
        self.closeDoxyMainFile()

    ## @brief Run doxygen on the main page.
    ## @param self
    #  The class instance.
    
    def doxygenate(self):
        logging.info('Running doxygen...')
        startTime = time.time()
        command = 'cd %s; doxygen %s' % (self.__OutputDirPath,\
                                         self.__DOXY_CONFIG_FILE_NAME)
        if self.__Verbose:
            os.system(command)
        else:
            commands.getoutput(command)
        logging.info('Done in %s s.\n' % (time.time() - startTime))

    ## @brief Compile the LaTeX report and make ps and pdf files.
    ## @param self
    #  The class instance.

    def compileLatex(self):
        logging.info('Compiling LaTeX report...')
        startTime = time.time()
        command = 'cd %s; make pdf' % self.__LatexDirPath
        if self.__Verbose:
            os.system(command)
        else:
            commands.getoutput(command)
        logging.info('Done in %s s.\n' % (time.time() - startTime))


        

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage='usage: %prog [options] data_file')
    parser.add_option('-c', '--config-file', dest='config_file',\
                      default='../xml/config.xml', type=str,   \
                      help='path to the input xml configuration file')
    parser.add_option('-d', '--report-dir', dest='report_dir', type=str,
                      default=None, help='path to the output report directory')
    parser.add_option('-f', '--force-overwrite', action='store_true',
                      dest='force_overwrite', default=False,
                      help='overwrite files without asking')
    parser.add_option('-v', '--verbose', action='store_true',
                      dest='verbose', default=False,
                      help='print a lot of ROOT/doxygen/LaTeX related stuff')
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.print_help()
        parser.error('incorrect number of arguments.')
        sys.exit()

    xmlParser = pXmlParser(options.config_file)
    reportGenerator = pTestReportGenerator(xmlParser, args[0],\
                                           options.report_dir,\
                                           options.force_overwrite,\
                                           options.verbose)
    reportGenerator.run()

