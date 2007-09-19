## @package pCustomPlotter
## @brief package containing the definition of the methods to be called
#  whenever a CUSTOM plot is declared in the xml configuration file.

import pSafeLogger
logger = pSafeLogger.getLogger('pCustomPlotter')

import time
import numpy
import pUtils
import os

from pGlobals  import *
from pSafeROOT import ROOT


TMP_FILE_PATH = 'tmp.root'


class pCustomPlotter:

    def __init__(self, rootFilePath, rootTree):
        self.RootFilePath = rootFilePath
        self.RootTree = rootTree
        self.TmpRootTree = None
        self.StartTime = None

    def cleanup(self):
        logger.info('Removing temp root file...')
        os.system('rm -f %s' % TMP_FILE_PATH)
        logger.info('Done.')

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

    def __templateFunction(self, plotRep):
        self.__startTimer()
        # Create the histograms.
        # self.__createTmpRootTree([], plotRep.Cut)
        # Create numpy arrays.
        for i in xrange(self.TmpRootTree.GetEntriesFast()):
            self.TmpRootTree.GetEntry(i)
            # Do stuff.
        self.__stopTimer(plotRep)
        self.__deleteTmpRootTree()
        return histogram
        
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

    ## @brief Create an acd tile map.
    #
    #  
    ## @param self
    #  The class instance.
    ## @param plotRep
    #  The custom plot representation from the pXmlParser object.

    def AcdGemVeto_AcdTile(self, plotRep):
        self.__startTimer()
        histogram = ROOT.TH1F(plotRep.Name, plotRep.Title, NUM_ACD_VETOES,\
                              -0.5, NUM_ACD_VETOES -0.5)
        self.__createTmpRootTree(['AcdGemVeto_AcdTile'], plotRep.Cut)
        acdVeto = self.__createNumpyArray('AcdGemVeto_AcdTile',\
                                          (NUM_ACD_VETOES), 'int')
        for i in xrange(self.TmpRootTree.GetEntriesFast()):
            self.TmpRootTree.GetEntry(i)
            for tile in xrange(NUM_ACD_VETOES):
                if acdVeto[tile]:
                    histogram.Fill(tile)
        self.__stopTimer(plotRep)
        self.__deleteTmpRootTree()
        return histogram
    
    ## @brief Method mapping the content of a gem 16 bit register to the
    #  corresponding tower and returning a TH1F object.
    ## @param self
    #  The class instance.
    ## @param plotRep
    #  The custom plot representation from the pXmlParser object.

    def gem_vector_map(self, plotRep):
        self.__startTimer()
        histogram = ROOT.TH1F(plotRep.Name, plotRep.Title, 16, 0, 16)
        self.__createTmpRootTree([plotRep.Expression], plotRep.Cut)
        towerVec = self.__createNumpyArray(plotRep.Expression, (1), 'int')
        for i in xrange(self.TmpRootTree.GetEntriesFast()):
            self.TmpRootTree.GetEntry(i)
            for tower in xrange(16):
                if towerVec & (0x1 << tower):
                    histogram.Fill(tower)
        self.__stopTimer(plotRep)
        self.__deleteTmpRootTree()
        return histogram

    ## @brief Return a ROOT TH1F object: the distribution of the number of
    #  planes hit in a tower.
    #
    #  This function uses the tkr_layer_end_strip_count variable;
    #  if it is not present in the TTree the histogram will be empty
    #  and a warning message will be sent.
    ## @param self
    #  The class instance.
    ## @param plotRep
    #  The custom plot representation from the pXmlParser object.
    ## @param tower
    #  The Tracker tower under analysis

    def TkrPlanesHit(self, plotRep, tower):
        self.__startTimer()
        histogram = ROOT.TH1F(plotRep.getExpandedName(tower),\
                              plotRep.getExpandedTitle(tower),
                              NUM_TKR_LAYERS_PER_TOWER, -0.5,\
                              NUM_TKR_LAYERS_PER_TOWER - 0.5)
        self.__createTmpRootTree(['TkrHitsTowerPlane'], plotRep.Cut)
        tkrHits = self.__createNumpyArray('TkrHitsTowerPlane', (16, 36), 'int')
        for i in xrange(self.TmpRootTree.GetEntriesFast()):
            self.TmpRootTree.GetEntry(i)
            numHitLayers = 0
            for layer in range(36):
                if tkrHits[tower][layer]:
                    numHitLayers += 1
            histogram.Fill(numHitLayers)
        self.__stopTimer(plotRep)
        self.__deleteTmpRootTree()
        return histogram

    ## @brief 
    ## @param self
    #  The class instance.
    ## @param plotRep
    #  The custom plot representation from the pXmlParser object.

    def gem_acd_cable_map(self, plotRep):
        self.__startTimer()
        histogram = ROOT.TH1F(plotRep.Name, plotRep.Title, NUM_ACD_CABLES,\
                              -0.5 , NUM_ACD_CABLES -0.5)
        self.__createTmpRootTree([plotRep.Expression], plotRep.Cut)
        varArray = self.__createNumpyArray(plotRep.Expression, (1), 'int')
        for i in xrange(self.TmpRootTree.GetEntriesFast()):
            self.TmpRootTree.GetEntry(i)
            for board in xrange(NUM_ACD_CABLES):
                if varArray & (0x1 << board):
                    histogram.Fill(board)
        self.__stopTimer(plotRep)
        self.__deleteTmpRootTree()
        return histogram      

    ## @brief Return a summed hit map of the calorimeter.
    #
    #  Each (Tower,Layer) bin contains the summed number of logs hit per layer
    #  Over all events but periodic triggers
    ## @param self
    #  The class instance.
    ## @param plotRep
    #  The custom plot representation from the pXmlParser object.
    def CalXHit_NHit_Counter_TowerCalLayer(self, plotRep):
        self.__startTimer()
        ymin      = -0.5
        ymax      = NUM_CAL_LAYERS_PER_TOWER-0.5
        ybins     = NUM_CAL_LAYERS_PER_TOWER
        xmin      = -0.5
        xmax      = NUM_TOWERS-0.5
        xbins     = NUM_TOWERS

        histogram = ROOT.TH2F(plotRep.Name, plotRep.Title, xbins, xmin, xmax,
                          ybins, ymin, ymax)
        self.__createTmpRootTree(['CalXHit_TowerCalLayer'], plotRep.Cut)
        calHits = self.__createNumpyArray('CalXHit_TowerCalLayer',\
                                          (16, 8), 'int')
        for i in xrange(self.TmpRootTree.GetEntriesFast()):
            self.TmpRootTree.GetEntry(i)
            for tower in range(NUM_TOWERS):
                for layer in range(NUM_CAL_LAYERS_PER_TOWER):
                    if calHits[tower][layer]:
                         histogram.Fill(tower, layer)

        self.__stopTimer(plotRep)
        self.__deleteTmpRootTree()
        return histogram
    
    ## @brief Return a map of the number of time there was no hit in a layer.
    #
    #  Each (Tower,Layer) bin contains the number of time the layer had no hits
    #  Over all events but periodic triggers
    ## @param self
    #  The class instance.
    ## @param plotRep
    #  The custom plot representation from the pXmlParser object.

    def ZeroCalXHit_NHit_Counter_TowerCalLayer(self, plotRep):
        self.__startTimer()    
        ymin      = -0.5
        ymax      = NUM_CAL_LAYERS_PER_TOWER-0.5
        ybins     = NUM_CAL_LAYERS_PER_TOWER
        xmin      = -0.5
        xmax      = NUM_TOWERS-0.5
        xbins     = NUM_TOWERS
        histogram = ROOT.TH2F(plotRep.Name, plotRep.Title, xbins, xmin, xmax,
                          ybins, ymin, ymax)
        self.__createTmpRootTree(['CalXHit_TowerCalLayer'], plotRep.Cut)
        calHits = self.__createNumpyArray('CalXHit_TowerCalLayer',\
                                          (16, 8), 'int')
        for i in xrange(self.TmpRootTree.GetEntriesFast()):
            self.TmpRootTree.GetEntry(i)
            for tower in range(NUM_TOWERS):
                for layer in range(NUM_CAL_LAYERS_PER_TOWER):
                    if calHits[tower][layer]==0:
                         histogram.Fill(tower, layer)

        self.__stopTimer(plotRep)
        self.__deleteTmpRootTree()
        return histogram 


