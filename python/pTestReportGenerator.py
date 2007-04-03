
import os
import sys
import logging
import pConfig
import ROOT

from pXmlParser import pXmlParser


class pTestReportGenerator:

    __DOXY_CONFIG_FILE_NAME = 'config.doxygen'
    __DOXY_MAIN_FILE_NAME   = 'mainpage.doxygen'
    __HTML_DIR_NAME         = 'html'
    __LATEX_DIR_NAME        = 'latex'

    def __init__(self, inputFile, outputDirPath, xmlParser):
        self.__InputRootFilePath = inputFile
        self.__OutputDirPath     = outputDirPath
        self.__XmlParser         = xmlParser
        self.__HtmlDirPath       = os.path.join(self.__OutputDirPath,\
                                                self.__HTML_DIR_NAME)
        self.__LatexDirPath      = os.path.join(self.__OutputDirPath,\
                                                self.__LATEX_DIR_NAME)
        self.__DoxyMainFile      = None

    def __createOutputDir(self):
        if os.path.exists(self.__OutputDirPath):
            logging.warn('Output directory already exists (will be replaced).')
            os.system('rm -rf %s' % self.__OutputDirPath)
        os.makedirs(self.__OutputDirPath)

    def __createHtmlDir(self):
        os.makedirs(self.__HtmlDirPath)

    def __createLatexDir(self):
        os.makedirs(self.__LatexDirPath)

    def createDirs(self):
        self.__createOutputDir()
        self.__createHtmlDir()
        self.__createLatexDir()

    def __openOutputFile(self, filePath):
        try:
            return file(filePath, 'w')
        except:
            sys.exit('Could not open output file %s' % filePath)

    def __write(self, line):
        self.__DoxyMainFile.writelines(line)

    def __skipLine(self):
        self.__write('\n')

    def writeDoxyConfigFile(self):
        fileContent = 'FILE_PATTERNS = %s\n'   % self.__DOXY_MAIN_FILE_NAME
        filePath    = os.path.join(self.__OutputDirPath,\
                                   self.__DOXY_CONFIG_FILE_NAME)
        configFile  = self.__openOutputFile(filePath)
        configFile.writelines(fileContent)
        configFile.close()

    def openDoxyMainFile(self):
        filePath            = os.path.join(self.__OutputDirPath,\
                                           self.__DOXY_MAIN_FILE_NAME)
        self.__DoxyMainFile = self.__openOutputFile(filePath)
        
    def closeDoxyMainFile(self):
        self.__DoxyMainFile.close()

    def addPlots(self):
        ROOT.gROOT.SetBatch(1)
        rootFile   = ROOT.TFile(self.__InputRootFilePath)
        rootCanvas = ROOT.TCanvas()
        for list in self.__XmlParser.OutputListsDict.values():
            name  = list.Name
            label = name.replace(' ', '_')
            self.addSection(label, name)
            for plotRep in list.EnabledPlotRepsDict.values():
                for name in plotRep.getRootObjectsName():
                    plot     = rootFile.Get(name)
                    epsPath = os.path.join(self.__LatexDirPath,\
                                           ('%s.eps' % name))
                    gifPath = os.path.join(self.__HtmlDirPath,\
                                           ('%s.gif' % name))
                    plot.Draw()
                    rootCanvas.SaveAs(epsPath)
                    rootCanvas.SaveAs(gifPath)
                    self.addPlot(plotRep.Title, plotRep.Title,\
                                 epsPath, gifPath)
        ROOT.gROOT.SetBatch(0)

    def writeReport(self):
        self.openDoxyMainFile()
        self.writeDoxyConfigFile()
        self.writeHeader()
        self.addPlots()
        self.writeTrailer()
        self.closeDoxyMainFile()

    def writeHeader(self):
        self.__write('/** @mainpage Fast monitor report\n'                   +\
                     '@htmlonly\n'                                           +\
                     '<center>\n'                                            +\
                     '<a href="../latex/refman.ps" > PS report </a> &nbsp\n' +\
                     '<a href="../latex/refman.pdf"> PDF report </a>\n'      +\
                     '</center>\n'                                           +\
                     '@endhtmlonly\n'                                        +\
                     '@author{automatically generated}\n')
        self.__skipLine()

    def writeTrailer(self):
        self.__skipLine()
        self.__write('*/')

    def addSection(self, label, name):
        self.__skipLine()
        self.__write('@section %s %s' % (label, name))
        self.__skipLine()

    def addPlot(self, title, caption, epsPath, gifPath):
        self.__write(('@htmlonly'+\
                      '<div align="center"> <p><strong> %s.</strong> %s</p>'+\
                      '<img src="%s" alt="%s"> </div> @endhtmlonly\n' +\
                      '@latexonly \\begin{figure}[H]\n' +\
                      '\\begin{center}\n' +\
                      '\\includegraphics[height=10.0cm,width=15.0cm]{%s}' +\
                      '\\caption{{\\bf %s.} %s}\n' +\
                      '\\end{center}\n' +\
                      '\\end{figure}\n' +\
                      '@endlatexonly\n' +\
                      '@latexonly \\nopagebreak @endlatexonly') %\
                     (title, caption,\
                      gifPath, gifPath,\
                      epsPath, title, caption))
    
    def doxygenate(self):
        os.system('cd %s; doxygen %s;' % (self.__OutputDirPath,\
                                          self.__DOXY_CONFIG_FILE_NAME))

    def compileLatex(self):
        os.system('cd %s; make pdf;' % self.__LatexDirPath)


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage='usage: %prog [options] data_file')
    parser.add_option('-c', '--config-file', dest='config_file',\
                      default='../xml/config.xml', type=str,   \
                      help='path to the input xml configuration file')
    parser.add_option('-o', '--output-dir', dest='output_dir', type=str,
                      help='path to the output report directory')
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.print_help()
        parser.error('incorrect number of arguments')
        sys.exit()

    xmlParser = pXmlParser(options.config_file)
    reportGenerator = pTestReportGenerator('IsocDataFile_processed.root',\
                                           '/home/online/temp', xmlParser)
    reportGenerator.createDirs()
    reportGenerator.writeReport()
    reportGenerator.doxygenate()
    reportGenerator.compileLatex()

