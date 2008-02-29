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
import random
from math import sqrt

class pCustomPlotter:

    def __init__(self, rootFilePath, rootTree):
        self.ObjectsPool = {}
        self.RootFilePath = rootFilePath
        self.RootTree = rootTree
        self.TmpRootTree = None
        self.StartTime = None
        self.TmpFilePath = os.path.join(os.path.dirname(rootFilePath),\
                                        'tmp_%s.root' %\
                                        (random.randint(0,100000)))
        if os.path.exists(self.TmpFilePath):
            self.TmpFilePath = self.TmpFilePath.replace('.root', '_1.root')
        logger.debug('Using temp file %s.' % (self.TmpFilePath))

    def cleanup(self):
        logger.info('Removing temp root file...')
        os.system('rm -f %s' % self.TmpFilePath)
        logger.info('Done.')

    def __startTimer(self):
        self.StartTime = time.time()

    def __stopTimer(self, plotRep):
        logger.debug('%s done in %.2f s.' %\
                     (plotRep.getName(), time.time() - self.StartTime))

    def __openTmpRootFile(self):
        self.TmpRootFile = ROOT.TFile(self.TmpFilePath, 'RECREATE')
        
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
        if cut != '':
            self.TmpRootTree = self.RootTree.CopyTree(cut)
        else:
            self.TmpRootTree = self.RootTree
        
    def __createNumpyArray(self, varName, shape, type):
        numpyArray = numpy.zeros(shape, type)
        self.TmpRootTree.SetBranchAddress(varName, numpyArray)
        return numpyArray

    def __deleteTmpRootTree(self):
        self.TmpRootTree = None
        self.__closeTmpRootFile()
        self.RootTree.SetBranchStatus('*', 1)
        
    def ToT_0_WhenTkrHitsExist_TowerPlane(self, plotRep):
        # Note: Histogram Entries seems correct
        self.__startTimer()
        histogram = ROOT.TH2F(plotRep.Name, plotRep.Title,16, -0.5, 15.5,\
                              36, -0.5, 35.5)
        self.__createTmpRootTree(['TkrHitsTowerPlane', 'ToT_con0_TowerPlane',\
                                  'ToT_con1_TowerPlane'], plotRep.Cut)
        nHits = self.__createNumpyArray('TkrHitsTowerPlane', (16, 36), 'int')
        tot0 = self.__createNumpyArray('ToT_con0_TowerPlane', (16, 36), 'int')
        tot1 = self.__createNumpyArray('ToT_con1_TowerPlane', (16, 36), 'int')
        for i in xrange(self.TmpRootTree.GetEntriesFast()):
            self.TmpRootTree.GetEntry(i)
            for tower in range(16):
                # This is for optimizing speed---we gain a factor of 2.
                if nHits[tower].sum():
                    for layer in range(36):
                        if nHits[tower][layer] > 0 and tot0[tower][layer] == 0\
                               and tot1[tower][layer] == 0:
                            histogram.Fill(tower, layer)
        self.__stopTimer(plotRep)
        self.__deleteTmpRootTree()
        return [histogram]

    ## @brief Create an acd tile map.
    #
    #  
    ## @param self
    #  The class instance.
    ## @param plotRep
    #  The custom plot representation from the pXmlParser object.

    def AcdGemVeto_AcdTile(self, plotRep):
        # Note: Histogram Entries seems correct
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
        return [histogram]
    
    ## @brief Method mapping the content of a gem 16 bit register to the
    #  corresponding tower and returning a TH1F object.
    ## @param self
    #  The class instance.
    ## @param plotRep
    #  The custom plot representation from the pXmlParser object.

    def gem_vector_map(self, plotRep):
        # Note: Histogram Entries seems correct
        self.__startTimer()
        histogram = ROOT.TH1F(plotRep.Name, plotRep.Title, 16, -0.5, 16-0.5)
        self.__createTmpRootTree([plotRep.Expression], plotRep.Cut)
        towerVec = self.__createNumpyArray(plotRep.Expression, (1), 'int')
        for i in xrange(self.TmpRootTree.GetEntriesFast()):
            self.TmpRootTree.GetEntry(i)
            for tower in xrange(16):
                if towerVec & (0x1 << tower):
                    histogram.Fill(tower)
        self.__stopTimer(plotRep)
        self.__deleteTmpRootTree()
        return [histogram]

    ## @brief Return a ROOT TH1F object: the distribution of the number of
    #  planes hit in a tower.
    #
    #  This function uses the TkrHitsTowerPlane variable;
    ## @param self
    #  The class instance.
    ## @param plotRep
    #  The custom plot representation from the pXmlParser object.
    ## @param tower
    #  The Tracker tower under analysis

    def TkrPlanesHit(self, plotRep):
        # Note: Histogram Entries seems correct
        self.__startTimer()
        histograms = []
        for tower in range(16):
            histograms.append(ROOT.TH1F(plotRep.getExpandedName(tower),\
                                        plotRep.getExpandedTitle(tower),
                                        38, -0.5, 38 - 0.5))
        self.__createTmpRootTree(['TkrHitsTowerPlane'], plotRep.Cut)
        tkrHits = self.__createNumpyArray('TkrHitsTowerPlane', (16, 36), 'int')
        noHits = numpy.zeros((36), 'int')
        for i in xrange(self.TmpRootTree.GetEntriesFast()):
            self.TmpRootTree.GetEntry(i)
            for tower in range(16):
                histograms[tower].Fill((tkrHits[tower] != noHits).sum())
        self.__stopTimer(plotRep)
        self.__deleteTmpRootTree()
        return histograms

    def __getTkrIntegralHits(self, tkrHits):
        if 'tkrIntegralHits' in self.ObjectsPool.keys():
            return self.ObjectsPool['tkrIntegralHits']
        tkrIntegralHits = numpy.zeros((16, 36, 24), 'int')
        for i in xrange(self.TmpRootTree.GetEntriesFast()):
            self.TmpRootTree.GetEntry(i)
            tkrIntegralHits += tkrHits
        self.ObjectsPool['tkrIntegralHits'] = tkrIntegralHits
        return self.ObjectsPool['tkrIntegralHits']

    def TkrHitsCounter_PlaneGTFE(self, plotRep):
        self.__startTimer()
        histograms = []
        for tower in range(16):
            histograms.append(ROOT.TH2F(plotRep.getExpandedName(tower),\
                                        plotRep.getExpandedTitle(tower),
                                        24, -0.5, 23.5, 36, -0.5, 35.5))
        self.__createTmpRootTree(['TkrHitsGTFE'], plotRep.Cut)
        tkrHits = self.__createNumpyArray('TkrHitsGTFE', (16, 36, 24), 'int')
        tkrIntegralHits = self.__getTkrIntegralHits(tkrHits)
        for tower in range(16):
            for layer in range(36):
                for gtfe in range(24):
                    histograms[tower].Fill(gtfe, layer,\
                                           tkrIntegralHits[tower][layer][gtfe])
        self.__stopTimer(plotRep)
        self.__deleteTmpRootTree()
        # Note: Histogram Entries need to be set by hand
        for tower in range(16):
            histograms[tower].SetEntries(tkrIntegralHits[tower].sum())
        return histograms

    def TkrHitsCounter_Plane(self, plotRep):
        self.__startTimer()
        histograms = []
        for tower in range(16):
            histograms.append(ROOT.TH1F(plotRep.getExpandedName(tower),\
                                        plotRep.getExpandedTitle(tower),
                                        36, -0.5, 35.5))
        self.__createTmpRootTree(['TkrHitsGTFE'], plotRep.Cut)
        tkrHits = self.__createNumpyArray('TkrHitsGTFE', (16, 36, 24), 'int')
        tkrIntegralHits = self.__getTkrIntegralHits(tkrHits)
        for tower in range(16):
            for layer in range(36):   
                histograms[tower].Fill(layer,\
                                       tkrIntegralHits[tower][layer].sum())
        self.__stopTimer(plotRep)
        self.__deleteTmpRootTree()
        # Note: Histogram Entries need to be set by hand
        for tower in range(16):
            histograms[tower].SetEntries(tkrIntegralHits[tower].sum())
        return histograms
                                       
    ## @brief 
    ## @param self
    #  The class instance.
    ## @param plotRep
    #  The custom plot representation from the pXmlParser object.

    def gem_acd_cable_map(self, plotRep):
        # Note: Histogram Entries seems correct
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
        return [histogram]

    def CalLogEndRangeHitCounter(self, plotRep):
        self.__startTimer()
        histograms = []
        for tower in range(16):
            histograms.append(ROOT.TH2F(plotRep.getExpandedName(tower), plotRep.getExpandedTitle(tower),\
	                                24, -0.5, 11.5, 8, -0.5, 7.5))
        self.__createTmpRootTree(['CalLogEndRangeHit'], plotRep.Cut)
        calHits = self.__createNumpyArray('CalLogEndRangeHit',\
                                          (16, 8, 12, 2, 4), 'bool_')
        calIntegralHits = numpy.zeros((16, 8, 12, 2, 4), 'int')
        for i in xrange(self.TmpRootTree.GetEntriesFast()):
            self.TmpRootTree.GetEntry(i)
            calIntegralHits += calHits
	calRange = int(plotRep.Expression[-1])
        for tower in range(16):
	    numEntries = 0
            for layer in range(8):
                for column in range(12):
                    for side in range(2):
                        x = column + side/2. - 0.5
                        y = layer
			n = calIntegralHits[tower][layer][column][side][calRange]
                        histograms[tower].Fill(x, y, n)
			numEntries += n
            histograms[tower].SetEntries(numEntries)
        self.__stopTimer(plotRep)
        self.__deleteTmpRootTree()
        return histograms

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
        self.__createTmpRootTree(['CalXHit_TowerCalLayerCalColumn'],\
                                 plotRep.Cut)
        calHits = self.__createNumpyArray('CalXHit_TowerCalLayerCalColumn',\
                                          (16, 8, 12), 'int')
        for i in xrange(self.TmpRootTree.GetEntriesFast()):
            self.TmpRootTree.GetEntry(i)
            for tower in range(NUM_TOWERS):
                # This is for optimizing speed---we gain a factor of 5.
                if calHits[tower].sum():
                    for layer in range(NUM_CAL_LAYERS_PER_TOWER):
                        histogram.Fill(tower,layer,calHits[tower][layer].sum())
        self.__stopTimer(plotRep)
        self.__deleteTmpRootTree()
        return [histogram]
    
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
        self.__createTmpRootTree(['CalXHit_TowerCalLayerCalColumn'],\
                                 plotRep.Cut)
        calHits = self.__createNumpyArray('CalXHit_TowerCalLayerCalColumn',\
                                          (16, 8, 12), 'int')
        for i in xrange(self.TmpRootTree.GetEntriesFast()):
            self.TmpRootTree.GetEntry(i)
            for tower in range(NUM_TOWERS):
                # This is for optimizing speed---we gain a factor of 3.
                if calHits[tower].sum() == 0:
                    for layer in range(NUM_CAL_LAYERS_PER_TOWER):
                        histogram.Fill(tower, layer)
                else:
                    for layer in range(NUM_CAL_LAYERS_PER_TOWER):
                        if calHits[tower][layer].sum() == 0:
                            histogram.Fill(tower, layer)
        self.__stopTimer(plotRep)
        self.__deleteTmpRootTree()
        return [histogram] 

    ## @brief  Return a ROOT TH2F object: Tower number vs Plane
    # 
    #  
    ## @param plotRep
    #  The custom plot representation from the pXmlParser object.
    
    def ZeroTkrHitsCounter_TowerPlane(self, plotRep):
        self.__startTimer()
        histogram = ROOT.TH2F(plotRep.Name, plotRep.Title, 16, -0.5, 15.5,
                              36, -0.5, 35.5)
        self.__createTmpRootTree(['TkrHitsTowerPlane'], plotRep.Cut)
        tkrHits = self.__createNumpyArray('TkrHitsTowerPlane', (16, 36), 'int')
        for i in xrange(self.TmpRootTree.GetEntriesFast()):
            self.TmpRootTree.GetEntry(i)
            for tower in range(16):
                for layer in range(36):
                    if tkrHits[tower][layer] == 0:
                        histogram.Fill(tower, layer)
        self.__stopTimer(plotRep)
        self.__deleteTmpRootTree()
        return [histogram]

    ## @brief  Return a ROOT TH2F object: Tower number vs Plane
    # 
    #  
    ## @param plotRep
    #  The custom plot representation from the pXmlParser object.

    def TkrHitsCounter_TowerPlane(self, plotRep):
        self.__startTimer()
        histogram = ROOT.TH2F(plotRep.Name, plotRep.Title, 16, -0.5, 15.5,
                              36, -0.5, 35.5)
        self.__createTmpRootTree(['TkrHitsTowerPlane'], plotRep.Cut)
        tkrHits = self.__createNumpyArray('TkrHitsTowerPlane', (16, 36), 'int')
        for i in xrange(self.TmpRootTree.GetEntriesFast()):
            self.TmpRootTree.GetEntry(i)
            for tower in range(16):
                if tkrHits[tower].sum() > 0 :
                    for layer in range(36):
                        histogram.Fill(tower, layer, tkrHits[tower][layer])
        self.__stopTimer(plotRep)
        self.__deleteTmpRootTree()
        return [histogram]

    ## @brief  Return a ROOT TH1F object with rates
    # 
    #  In the returned histogram each bin contains
    #  the number of event that satisfies the cut condition
    #  divided by time interval (the bin widht).
    #  Note that the last bin is widee than the others.
    ## @param plotRep
    #  The custom plot representation from the pXmlParser object.
    
    def RatePlot(self, plotRep):
        self.__startTimer()
        
        # Get Start, Stop, and Delta time
        self.RootTree.GetEntry(0)
        StartTime = self.RootTree.event_timestamp
        
        self.RootTree.GetEntry(self.RootTree.GetEntriesFast()-1)
        StopTime = self.RootTree.event_timestamp
        
        DTime = float(plotRep.getTagValue('dtime'))

        # Set binning, last bin set by hands
        nBins = int((StopTime - StartTime)/DTime)
        if nBins == 0:
            nBins = 1
            binning = numpy.array([StartTime, StopTime ])
        else:        
            binning = numpy.arange(StartTime, StopTime, DTime)
            binning[nBins] = StopTime
                
        histogram = ROOT.TH1F(plotRep.Name, plotRep.Title, nBins, binning)
        
        # Fill histogram
        self.RootTree.Project(histogram.GetName(), 'event_timestamp', \
                                 plotRep.Cut )

        # Scale histogram, last bin set by hands
        LastBinCont  = histogram.GetBinContent(nBins)
        LastBinWidth = histogram.GetBinWidth(nBins)
        LastBinError = histogram.GetBinError(nBins)
        histogram.Sumw2()
        histogram.Scale(1./DTime)
        histogram.SetBinContent(nBins, LastBinCont/LastBinWidth )
        histogram.SetBinError(nBins, LastBinError/LastBinWidth )
        
        self.__stopTimer(plotRep)
        return [histogram]
    
    ## @brief  Return a ROOT TH1F object with total rate calculated using GEM
    #  scaler
    #
    #  This function has a fix for MC production: the time interval is set to
    #  1 second and the bins with rate > 100 kH are artificially removed.
    ## @param plotRep
    #  The custom plot representation from the pXmlParser object.    

    def GemIDOneSecRatePlot(self, plotRep):
        self.__startTimer()
        
        # Get Start, Stop, and Delta time
        nEvents = self.RootTree.GetEntriesFast()
        self.RootTree.GetEntry(0)
        StartTime = self.RootTree.event_timestamp
        
        self.RootTree.GetEntry(nEvents-1)
        StopTime = self.RootTree.event_timestamp
                
        DTime = 1.0
        if plotRep.getTagValue('dtime')!=None \
               and float(plotRep.getTagValue('dtime'))!=1:
            logger.warning("Remember that dtime is fixed to 1 second for GemIDOneSecRatePlot")
            
        # Gen the number of bins and set the histogram binning
        nBins = int((StopTime - StartTime)/DTime)
        if nBins == 0:
            nBins =1
            TimeBins = numpy.array([StartTime, StopTime ])
        else:        
            TimeBins = numpy.arange(StartTime, StopTime, DTime)
            TimeBins[nBins] = StopTime
        histogram = ROOT.TH1F(plotRep.Name, plotRep.Title, nBins, TimeBins)
        
        # Looping on the RootTree
        self.RootTree.GetEntry(0)
        PrevGemId = self.RootTree.meta_context_gem_scalers_sequence
        
        TimeBinId = 0
        for evtId in xrange(nEvents):
            self.RootTree.GetEntry(evtId)
            EvtTime = self.RootTree.event_timestamp
            # if time crosses the bin boundary:
            if EvtTime >= TimeBins[TimeBinId+1]:
                CurrGemId = self.RootTree.meta_context_gem_scalers_sequence
                Rate      = (CurrGemId - PrevGemId)/(1000.*DTime)

                # There is a bug in the MC production
                # that makes a jump of ~ 128k gem counts
                # every 2 seconds (corresponding to a MC job)
                # To temporary fix this feature we do not plots rates > 100kHz
                # it works only with DTime <2 sec.
                if Rate<100:
                    histogram.Fill((TimeBins[TimeBinId+1]+TimeBins[TimeBinId])/2., Rate)         
                TimeBinId +=1
                PrevGemId = CurrGemId
                 
        self.__stopTimer(plotRep)
        return [histogram]

    ## @brief  Return a ROOT TH1F object with total rate calculated using GEM
    #  scaler
    #
    #  This function has is similar to GemIDOneSecRatePlot: it calculates the
    #  rate every 1 second, artificially remove rates >100 kHz (a fix for MC
    #  production), and fill an histogram with arbitrary time bin width (that
    #  can't be lower that 10 seconds anyway)
    ## @param plotRep
    #  The custom plot representation from the pXmlParser object. 

    def GemIDRatePlot(self, plotRep):
        self.__startTimer()
        # Get Start, Stop, and Delta time
        nEvents = self.RootTree.GetEntriesFast()
        self.RootTree.GetEntry(0)
        StartTime = self.RootTree.event_timestamp
        
        self.RootTree.GetEntry(nEvents-1)
        StopTime = self.RootTree.event_timestamp
                
       
        
        if plotRep.getTagValue('dtime') is None \
               or float(plotRep.getTagValue('dtime')) <10:
            DTime = 10.0
            logger.warning("The time interval must be at least 10 second wide for GemIDRatePlot")
        else:
             DTime = float(plotRep.getTagValue('dtime'))
        # Get the number of True bins
        nBins = int((StopTime - StartTime)/DTime)
        if nBins == 0:
            nBins =1
            TimeBins = numpy.array([StartTime, StopTime ])
        else:
            TimeBins = numpy.arange(StartTime, StopTime, DTime)
            TimeBins[nBins] = StopTime
        histogram = ROOT.TH1F(plotRep.Name, plotRep.Title, nBins, TimeBins)
        #print "GemIDRatePlot - DTime:", DTime, nBins
        # Looping on the RootTree
        self.RootTree.GetEntry(0)
        PrevGemId = self.RootTree.meta_context_gem_scalers_sequence
        PrevTime  = self.RootTree.event_timestamp
        AverageRate = 0
        AverageRateCounts = 0
        TimeBinId = 0
        for evtId in xrange(nEvents):
            self.RootTree.GetEntry(evtId)
            EvtTime = self.RootTree.event_timestamp
            # if time crosses 1sec boundary:
            if (EvtTime - PrevTime) >=1:
                CurrGemId = self.RootTree.meta_context_gem_scalers_sequence
                Rate      = (CurrGemId - PrevGemId)/(1000.)
                PrevGemId = CurrGemId
                PrevTime  = EvtTime
                # There is a bug in the MC production
                # that makes a jump of ~ 128k gem counts
                # every 2 seconds (corresponding to a MC job)
                # To temporary fix this feature we do not plots rates > 100kHz
                # it works only with DTime <2 sec.
                if Rate<100:
                    AverageRate       +=Rate
                    AverageRateCounts +=1
                    
            if EvtTime >= TimeBins[TimeBinId+1] and AverageRateCounts>0 :
                AverageRate = AverageRate/AverageRateCounts
                
                histogram.SetBinContent(TimeBinId+1,AverageRate )
                # Do not set bin error for now.
                #histogram.SetBinError(TimeBinId+1,
                #AverageRate/sqrt(AverageRateCounts) )
                AverageRate       = 0
                AverageRateCounts = 0         
                TimeBinId        +=1
                

        self.__stopTimer(plotRep)
        return [histogram]


