#! /bin/env python

import pSafeLogger
logger = pSafeLogger.getLogger('pReportGenerator')

from pRootFileManager     import pRootFileManager
from pBaseReportGenerator import pBaseReportGenerator
from pErrorHandler        import pErrorHandler
from pXmlParser           import pXmlParser

import time

class pReportGenerator(pBaseReportGenerator):





if __name__ == '__main__':
    from pXmlParser import pXmlParser
    from pOptionParser import pOptionParser
    optparser = pOptionParser('cvLV',1,1,False)

    xmlParser = pXmlParser(optparser.Options.c)
    errorHandler    = pErrorHandler()
    reportGenerator = pReportGenerator(errorHandler, xmlParser, optparser.Argument)
    reportGenerator.run(optparser.Options.v)
    if optparser.Options.V:
        reportGenerator.viewReport()
