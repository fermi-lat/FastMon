#! /bin/env python

import os
import sys

try:
    import pSafeLogger
except ImportError:
    sys.path.append('../../Common/python')
    XML_CONFIG_ROOT = '../../FastMonCfg/xml'
    XML_OUTPUT_ROOT = XML_CONFIG_ROOT
    os.environ['XML_CONFIG_DIR'] = XML_CONFIG_ROOT
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
            if self.XmlParser.EnabledPlotRepsDict[plotName].Level == 'tower':
                outputFile.writelines('%s_Tower_TowerLoop%s%s\n' %\
                                      (plotName, SEPARATOR,\
                                       DEFAULT_MERGE_MODE))
            else:
                outputFile.writelines('%s%s%s\n' % (plotName, SEPARATOR,\
                                                    DEFAULT_MERGE_MODE))
        outputFile.close()
        logger.info('Done.')


if __name__ == '__main__':
    mergeHistosMaker = pMergeHistosMaker('%s/config.xml' % XML_CONFIG_ROOT)
    mergeHistosMaker.writeOutputFile('%s/MergeHistos_FastMon.txt' %\
                                     XML_OUTPUT_ROOT)
    
