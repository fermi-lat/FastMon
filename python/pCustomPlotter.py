## @package pCustomPlotter
## @brief package containing the definition of the methods to be called
#  whenever a CUSTOM plot is declared in the xml configuration file.

import pSafeLogger
logger = pSafeLogger.getLogger('pCustomPlotter')

import time
import numpy
import pUtils

from pGlobals  import *
from pSafeROOT import ROOT


TMP_FILE_PATH = 'tmp.root'


class pCustomPlotter:

    def __init__(self, rootFilePath, rootTree):
        self.RootFilePath = rootFilePath
        self.RootTree = rootTree
        self.TmpRootTree = None
        self.StartTime = None

    def __startTimer(self):
        self.StartTime = time.time()

    def __stopTimer(self, plotRep):
        logger.debug('%s created in %.2f s.' %\
                     (plotRep.Name, time.time() - self.StartTime))

    def __openTmpRootFile(self):
        self.TmpRootFile = ROOT.TFile(TMP_FILE_PATH, 'RECREATE')

    def __closeTmpRootFile(self):
        self.TmpRootFile.Close()
        ROOT.gROOT.cd('%s:/' % self.RootFilePath)

    def __createTmpRootTree(self, varList, cut):
        self.__openTmpRootFile()
        self.RootTree.SetBranchStatus('*', 0)
        for varName in varList + pUtils.getCutVariables(cut):
            if self.RootTree.GetLeaf(varName) is None:
                logger.error('Could not find %s.' % varName)
            self.RootTree.SetBranchStatus(varName, 1)
        self.TmpRootTree = self.RootTree.CopyTree(cut)

    def __createNumpyArray(self, varName, shape, type):
        numpyArray = numpy.zeros(shape, type)
        self.TmpRootTree.SetBranchAddress(varName, numpyArray)
        return numpyArray

    def __deleteTmpRootTree(self):
        self.TmpRootTree = None
        self.__closeTmpRootFile()
        self.RootTree.SetBranchStatus('*', 1)

    def ToT_0_WhenTkrHitsExist_TowerPlane(self, plotRep):
        self.__startTimer()
        histogram = ROOT.TH2F(plotRep.Name, plotRep.Title, 36, -0.5, 35.5,
                              16, -0.5, 15.5)
        self.__createTmpRootTree(['TkrHitsTowerPlane', 'ToT_con0_TowerPlane',\
                                  'ToT_con1_TowerPlane'], plotRep.Cut)
        nHits = self.__createNumpyArray('TkrHitsTowerPlane', (16, 36), 'int')
        tot0 = self.__createNumpyArray('ToT_con0_TowerPlane', (16, 36), 'int')
        tot1 = self.__createNumpyArray('ToT_con1_TowerPlane', (16, 36), 'int')
        for i in xrange(self.TmpRootTree.GetEntriesFast()):
            self.TmpRootTree.GetEntry(i)
            for tower in xrange(16):
                for layer in xrange(36):
                    if nHits[tower][layer] > 0 and tot0[tower][layer] == 0\
                           and tot1[tower][layer] == 0:
                        histogram.Fill(layer, tower)
        self.__stopTimer(plotRep)
        self.__deleteTmpRootTree()
        return histogram
