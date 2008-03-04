#! /bin/env python

import os
import sys

try:
    import pSafeLogger
except ImportError:
    sys.path.append('../../Common/python')
    os.environ['XML_CONFIG_DIR'] = '../xml'
    import pSafeLogger
logger = pSafeLogger.getLogger('pMergeHistosMaker')

from pXmlParser import pXmlParser


SEPARATOR = '   '
DEFAULT_MERGE_MODE = 'Sum'


class pMergeHistosMaker:
    
    def __init__(self, configFilePath):
        self.XmlParser = pXmlParser(configFilePath)
        self.PlotList = self.XmlParser.EnabledPlotRepsDict.keys()
        logger.info('Configuration files parsed (%d entries found).' %
                    len(self.PlotList))

    def writeOutputFile(self, outputFilePath):
        logger.info('Writing output file %s...' % outputFilePath)
        outputFile = file(outputFilePath, 'w')
        for plotName in self.PlotList:
            outputFile.writelines('%s%s%s\n' % (plotName, SEPARATOR,\
                                                    DEFAULT_MERGE_MODE))
        outputFile.close()
        logger.info('Done.')


if __name__ == '__main__':
    mergeHistosMaker = pMergeHistosMaker('../xml/config.xml')
    mergeHistosMaker.writeOutputFile('../xml/MergeHistos_FastMon.txt')
    
