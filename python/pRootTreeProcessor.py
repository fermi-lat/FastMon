
import time
import ROOT
import logging

from pXmlParser import pXmlParser


class pRootTreeProcessor:

    def __init__(self, rootTree, xmlParser):
        self.__XmlParser = xmlParser
        self.__RootTree  = rootTree
        self.__Plots     = []

    def process(self):
        logging.info('Processing the root tree and writing histograms...')
        startTime = time.time()
        self.__createObjects()
        logging.info('Done in %s s.\n' % (time.time() - startTime))

    def __createObjects(self):
        for rep in self.__XmlParser.EnabledPlotRepsDict.values():
            rep.createRootObjects(self.__RootTree)


if __name__ == '__main__':
    f = ROOT.TFile('IsocDataFile.root')
    tree = f.Get('IsocDataTree')
    parser = pXmlParser('config.xml')
    processor = pRootTreeProcessor(tree, parser)
    outputFile = ROOT.TFile('data/output.root', 'recreate')
    processor.process()       
    processor.stripchart()
    outputFile.Write()
    outputFile.Close()
