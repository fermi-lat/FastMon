## @package pCUSTOMplots
## @brief package containing the definition of the methods to be called
#  whenever a CUSTOM plot is declared in the xml configuration file.

import pSafeLogger
logger = pSafeLogger.getLogger('pCUSTOMplots')

import time
import numpy
import array

from pGlobals  import *
from pSafeROOT import ROOT
from pUtils    import Root2PythonCutConverter
from pUtils    import getCutVariables


## @brief Method mapping the content of a gem 16 bit register to the
#  corresponding tower and returning a TH1F object.
## @param rootTree
#  The ROOT tree containing the variables.
## @param plotRep
#  The custom plot representation from the pXmlParser object.

## def gem_vector_map(rootTree, plotRep):
##     startTime = time.time()
##     histogram = ROOT.TH1F(plotRep.Name, plotRep.Title, 16, 0, 16)
##     histogram.SetMinimum(0)
##     for entry in rootTree:
##         for tower in xrange(NUM_TOWERS):
##             if eval('entry.%s & (0x1 << tower)' % plotRep.Expression) \
##                    and (eval(Root2PythonCutConverter(plotRep.Cut))):
##                 histogram.Fill(tower)
##     logger.debug('%s created in %.2f s.' %\
##                   (plotRep.Name, time.time() - startTime))
##     return histogram

## @brief 
## @param rootTree
#  The ROOT tree containing the variables.
## @param plotRep
#  The custom plot representation from the pXmlParser object.

## def gem_acd_tile_map(rootTree, plotRep):
##     startTime = time.time()
##     xbin = NUM_ACD_VETOES
##     xmin = -0.5
##     xmax = NUM_ACD_VETOES -0.5
##     histogram = ROOT.TH1F(plotRep.Name, plotRep.Title, xbin, xmin, xmax)
##     #histogram.SetMinimum(0)
##     for entry in rootTree:
##         for tile in xrange(NUM_ACD_VETOES):
##             if eval('entry.%s[tile]' % plotRep.Expression) \
##                    and (eval(Root2PythonCutConverter(plotRep.Cut))):
##                 histogram.Fill(tile)
##     logger.debug('%s created in %.2f s.' %\
##                   (plotRep.Name, time.time() - startTime))
##     return histogram

## @brief 
## @param rootTree
#  The ROOT tree containing the variables.
## @param plotRep
#  The custom plot representation from the pXmlParser object.

## def gem_acd_cable_map(rootTree, plotRep):
##     startTime = time.time()
##     xbin = NUM_ACD_CABLES
##     xmin = -0.5
##     xmax = NUM_ACD_CABLES -0.5
##     histogram = ROOT.TH1F(plotRep.Name, plotRep.Title, xbin, xmin, xmax)
##     #histogram.SetMinimum(0)
##     for entry in rootTree:
##         for board in xrange(NUM_ACD_CABLES):
##             if eval('entry.%s & (0x1 << board)' % plotRep.Expression) \
##                    and (eval(Root2PythonCutConverter(plotRep.Cut))):
##                 histogram.Fill(board)
##     logger.debug('%s created in %.2f s.' %\
##                   (plotRep.Name, time.time() - startTime))
##     return histogram

## @brief Return a ROOT TH2F object with the layer id on the x axis
#  and the tower id on the y axis.
#
#  The x axis is binned in steps of 0.5 and allows to display the two
#  ends (i.e. GTRCs) of the layer separately.
#  The average value of the Expression member of the pXmlPlotRep object
#  passed to the constructor is displayed on the z axis. A list of
#  particular values of the Expression can be excluded in the the average
#  evaluation through a flag passed as a parameter.
## @param rootTree
#  The ROOT tree containing the variables.
## @param plotRep
#  The custom plot representation from the pXmlParser object.

def tkr_2d_map(rootTree, plotRep):
    startTime = time.time()
    xmin      = 0
    xmax      = NUM_TKR_LAYERS_PER_TOWER
    xbins     = NUM_GTRC_PER_LAYER*xmax
    ymin      = 0
    ymax      = NUM_TOWERS
    ybins     = ymax
    histogram = ROOT.TH2F(plotRep.Name, plotRep.Title, xbins, xmin, xmax,
                          ybins, ymin, ymax)
    means   = numpy.zeros((NUM_TKR_GTRC), dtype=int)
    entries = numpy.zeros((NUM_TKR_GTRC), dtype=int)
    for entry in rootTree:
        values = numpy.zeros((NUM_TKR_GTRC), dtype=int)
        buffer = eval('entry.%s' % plotRep.Expression)
        for i in xrange(NUM_TKR_GTRC):
            values[i] = buffer[i]
        status = numpy.ones((NUM_TKR_GTRC), dtype=int)
        means += values
        for value in plotRep.ExcludedValues:
            status = status*(values != value)
        entries += status
    for tower in xrange(NUM_TOWERS):
        for layer in xrange(NUM_TKR_LAYERS_PER_TOWER):
            for end in xrange(NUM_GTRC_PER_LAYER):
                index = tower*NUM_TKR_LAYERS_PER_TOWER*NUM_GTRC_PER_LAYER +\
                        layer*NUM_GTRC_PER_LAYER +end
                if entries[index] == 0:
                    mean  = 0
                else:
                    mean  = means[index]/float(entries[index])
                histogram.Fill((layer + end/2.0 + 0.25), tower, mean)
    logger.debug('%s created in %.2f s.' %\
                  (plotRep.Name, time.time() - startTime))
    return histogram


## @brief This is a variant of the previous function.
#
#  It is fairly slow, though it has the advantage of making any kind of
#  cut on whatever variable possible in evaluating the average.
## @param rootTree
#  The ROOT tree containing the variables.
## @param plotRep
#  The custom plot representation from the pXmlParser object.

def tkr_2d_map_project(rootTree, plotRep):
    startTime = time.time()
    xmin      = 0
    xmax      = NUM_TKR_LAYERS_PER_TOWER
    xbins     = NUM_GTRC_PER_LAYER*xmax
    ymin      = 0
    ymax      = NUM_TOWERS
    ybins     = ymax
    histogram = ROOT.TH2F(plotRep.Name, plotRep.Title, xbins, xmin, xmax,
                          ybins, ymin, ymax)
    for tower in xrange(NUM_TOWERS):
        for layer in xrange(NUM_TKR_LAYERS_PER_TOWER):
            for end in xrange(NUM_GTRC_PER_LAYER):
                rootTree.Project("h1",\
                             plotRep.getExpandedExpression(tower, layer, end),\
                             plotRep.getExpandedCut(tower, layer, end))
                h1 = ROOT.gROOT.FindObjectAny("h1")
                mean = h1.GetMean()
                histogram.Fill((layer + end/2.0 + 0.25), tower, mean)
                h1.Delete()
    logger.debug('%s created in %2.f s.' %\
                  (plotRep.Name, time.time() - startTime))
    return histogram

## @brief This is like tkr_2d_map_project, but plot the number of entries
#  instread of the mean.
#
#  It is fairly slow, though it has the advantage of making any kind of
#  cut on whatever variable possible in evaluating the average.
## @param rootTree
#  The ROOT tree containing the variables.
## @param plotRep
#  The custom plot representation from the pXmlParser object.

def tkr_2d_map_project_count(rootTree, plotRep):
    startTime = time.time()
    xmin      = 0
    xmax      = NUM_TKR_LAYERS_PER_TOWER
    xbins     = NUM_GTRC_PER_LAYER*xmax
    ymin      = 0
    ymax      = NUM_TOWERS
    ybins     = ymax
    histogram = ROOT.TH2F(plotRep.Name, plotRep.Title, xbins, xmin, xmax,
                          ybins, ymin, ymax)
    for tower in xrange(NUM_TOWERS):
        for layer in xrange(NUM_TKR_LAYERS_PER_TOWER):
            for end in xrange(NUM_GTRC_PER_LAYER):
                rootTree.Project("h1",\
                             plotRep.getExpandedExpression(tower, layer, end),\
                             plotRep.getExpandedCut(tower, layer, end))
                h1 = ROOT.gROOT.FindObjectAny("h1")
                entries = h1.GetEntries()
                histogram.Fill((layer + end/2.0 + 0.25), tower, entries)
                h1.Delete()
    logger.debug('%s created in %2.f s.' %\
                  (plotRep.Name, time.time() - startTime))
    return histogram


## @brief Return a hit map of the calorimeter. DEPRECATED
#
#  Each (Tower,Layer) bin contains the average number of logs hit per layer
## @param rootTree
#  The ROOT tree containing the variables.
## @param plotRep
#  The custom plot representation from the pXmlParser object.
def cal_2d_map(rootTree, plotRep):
    startTime = time.time()
    xmin      = 0
    xmax      = NUM_CAL_LAYERS_PER_TOWER
    xbins     = xmax
    ymin      = 0
    ymax      = NUM_TOWERS
    ybins     = ymax
    histogram = ROOT.TH2F(plotRep.Name, plotRep.Title, xbins, xmin, xmax,
                          ybins, ymin, ymax)
    means   = numpy.zeros((NUM_CAL_LAYERS), dtype=int)
    entries = numpy.zeros((NUM_CAL_LAYERS), dtype=int)
    for entry in rootTree:
        values = numpy.zeros((NUM_CAL_LAYERS), dtype=int)
        buffer = eval('entry.%s' % plotRep.Expression)
        for i in xrange(NUM_CAL_LAYERS):
            values[i] = buffer[i]
        status = numpy.ones((NUM_CAL_LAYERS), dtype=int)
        means += values
        for value in plotRep.ExcludedValues:
            status = status*(values != value)
        entries += status
    for tower in xrange(NUM_TOWERS):
        for layer in xrange(NUM_CAL_LAYERS_PER_TOWER):
            index = tower*NUM_CAL_LAYERS_PER_TOWER + layer
            if entries[index] == 0:
                mean  = 0
            else:
                mean  = means[index]/float(entries[index])
            histogram.Fill((layer + 0.25), tower, mean)
    logger.debug('%s created in %.2f s.' %\
                  (plotRep.Name, time.time() - startTime))
    return histogram

## @brief Return a summed hit map of the calorimeter.
#
#  Each (Tower,Layer) bin contains the summed number of logs hit per layer
#  Over all events but periodic triggers
## @param rootTree
#  The ROOT tree containing the variables.
## @param plotRep
#  The custom plot representation from the pXmlParser object.

## def CalXHit_NHit_Counter_TowerCalLayer(rootTree, plotRep):
##     startTime = time.time()
##     xmin      = -0.5
##     xmax      = NUM_CAL_LAYERS_PER_TOWER-0.5
##     xbins     = NUM_CAL_LAYERS_PER_TOWER
##     ymin      = -0.5
##     ymax      = NUM_TOWERS-.5
##     ybins     = NUM_TOWERS
##     histogram = ROOT.TH2F(plotRep.Name, plotRep.Title, xbins, xmin, xmax,
##                           ybins, ymin, ymax)
##     means   = numpy.zeros((NUM_CAL_LAYERS), dtype=int)
##     entries = numpy.zeros((NUM_CAL_LAYERS), dtype=int)
##     for entry in rootTree:
## 	if eval(Root2PythonCutConverter(plotRep.Cut)):
## 	    values = numpy.zeros((NUM_CAL_LAYERS), dtype=int)
## 	    buffer = eval('entry.%s' % plotRep.Expression)
## 	    for i in xrange(NUM_CAL_LAYERS):
## 	        values[i] = buffer[i]
## 	    status = numpy.ones((NUM_CAL_LAYERS), dtype=int)
## 	    means += values
## 	    for value in plotRep.ExcludedValues:
## 	        status = status*(values != value)
## 	    entries += status

##     for tower in xrange(NUM_TOWERS):
##         for layer in xrange(NUM_CAL_LAYERS_PER_TOWER):
##             index = tower*NUM_CAL_LAYERS_PER_TOWER + layer
##             histogram.Fill((layer + 0.25), tower, entries[index])
	    
##     logger.debug('%s created in %.2f s.' %\
##                   (plotRep.Name, time.time() - startTime))
##     return histogram

## @brief Return a map of the number of time there was no hit in a layer.
#
#  Each (Tower,Layer) bin contains the number of time the layer had no hits
#  Over all events but periodic triggers
## @param rootTree
#  The ROOT tree containing the variables.
## @param plotRep
#  The custom plot representation from the pXmlParser object.

## def ZeroCalXHit_NHit_Counter_TowerCalLayer(rootTree, plotRep):
##     startTime = time.time()
##     xmin      = -0.5
##     xmax      = NUM_CAL_LAYERS_PER_TOWER-0.5
##     xbins     = NUM_CAL_LAYERS_PER_TOWER
##     ymin      = -0.5
##     ymax      = NUM_TOWERS-.5
##     ybins     = NUM_TOWERS
##     histogram = ROOT.TH2F(plotRep.Name, plotRep.Title, xbins, xmin, xmax,
##                           ybins, ymin, ymax)
##     entries = numpy.zeros((NUM_CAL_LAYERS), dtype=int)
##     for entry in rootTree:
## 	if eval(Root2PythonCutConverter(plotRep.Cut)):
## 	    values = numpy.zeros((NUM_CAL_LAYERS), dtype=int)
## 	    buffer = eval('entry.%s' % plotRep.Expression)
## 	    for i in xrange(NUM_CAL_LAYERS):
## 	        values[i] = buffer[i]
## 	    status = numpy.ones((NUM_CAL_LAYERS), dtype=int)
## 	    for value in plotRep.ExcludedValues:
## 	        status = status*(values != value)
## 	    isZero = eval('status==0')	
## 	    entries += isZero

##     for tower in xrange(NUM_TOWERS):
##         for layer in xrange(NUM_CAL_LAYERS_PER_TOWER):
##             index = tower*NUM_CAL_LAYERS_PER_TOWER + layer
## 	    histogram.Fill( (layer + 0.25), tower, entries[index])
	    
##     logger.debug('%s created in %.2f s.' %\
##                   (plotRep.Name, time.time() - startTime))
##     return histogram


## @brief Return a ROOT TH1F object: the distribution of the number of
#  planes hit in a tower.
#
#  This function uses the tkr_layer_end_strip_count variable;
#  if it is not present in the TTree the histogram will be empty
#  and a warning message will be sent.
## @param rootTree
#  The ROOT tree containing the variables.
## @param plotRep
#  The custom plot representation from the pXmlParser object.
## @param tower
#  The Tracker tower under analysis

## def TkrPlanesHit(rootTree, plotRep, tower):
##     startTime = time.time()
##     xmin      = 0
##     xmax      = NUM_TKR_LAYERS_PER_TOWER+1
##     xbins     = xmax
##     histogram = ROOT.TH1F(plotRep.getExpandedName(tower), plotRep.getExpandedTitle(tower),
##                           xbins, xmin, xmax)
    
##     if rootTree.GetLeaf("TkrHitsTowerPlane") is None:
##         logger.warning('%s requires TkrHitsTowerPlane that is not in the processed tree' %\
##                        plotRep.getExpandedName(tower))
##         return histogram

##     for entry in rootTree:
##         tmpNumLayer = 0
##         for layer in xrange(NUM_TKR_LAYERS_PER_TOWER):
##             index = tower*NUM_TKR_LAYERS_PER_TOWER + layer
##             buffer = entry.TkrHitsTowerPlane[index]
##             if (buffer>0 ) and (eval(Root2PythonCutConverter(plotRep.Cut))):
##                 tmpNumLayer +=1

##         histogram.Fill(tmpNumLayer)

##     logger.debug('%s created in %.2f s.' %\
##                   (plotRep.getExpandedName(tower), time.time() - startTime))
##     return histogram



## @brief Return a ROOT TH2F object.
#
## @deprecated use ToT_0_WhenTkrHitsExist_TowerPlane instead
## @param rootTree
#  The ROOT tree containing the variables.
## @param plotRep
#  The custom plot representation from the pXmlParser object.
## @todo move cut at the beginning of the event loop to save processing time

## def tkr_no_tot_counter(rootTree, plotRep):

##     startTime = time.time()
##     xmin      = 0
##     xmax      = NUM_TKR_LAYERS_PER_TOWER # 36
##     xbins     = NUM_GTRC_PER_LAYER*xmax # 72
##     ymin      = 0
##     ymax      = NUM_TOWERS
##     ybins     = ymax
##     histogram = ROOT.TH2F(plotRep.Name, plotRep.Title, xbins, xmin, xmax,
##                           ybins, ymin, ymax)

##     if rootTree.GetLeaf("tkr_layer_end_strip_count") is None:
##         logger.warning('%s requires tkr_layer_end_strip_count that is not in the processed tree' %\
##                        plotRep.getExpandedName(tower))
##         return histogram
##     if rootTree.GetLeaf("tkr_layer_end_tot") is None:
##         logger.warning('%s requires tkr_layer_end_tot that is not in the processed tree' %\
##                        plotRep.getExpandedName(tower))
##         return histogram
    
##     for entry in rootTree:
##         for tower in xrange(NUM_TOWERS):
##             for layer in xrange(NUM_TKR_LAYERS_PER_TOWER):
##                 index = tower*NUM_TKR_LAYERS_PER_TOWER*NUM_GTRC_PER_LAYER + layer*NUM_GTRC_PER_LAYER
##                 nStrips0 = entry.tkr_layer_end_strip_count[index]
##                 nStrips1 = entry.tkr_layer_end_strip_count[index +1]
##                 ToT0 = entry.tkr_layer_end_tot[index]
##                 ToT1 = entry.tkr_layer_end_tot[index +1]
                
##                 if nStrips0>0 and ToT0==0 and (eval(Root2PythonCutConverter(plotRep.Cut))):
##                     histogram.Fill(layer, tower)  
##                 if nStrips1>0 and ToT1==0 and (eval(Root2PythonCutConverter(plotRep.Cut))):
##                     histogram.Fill(layer+0.5, tower)

##     logger.debug('%s created in %.2f s.' %\
##                  (plotRep.Name, time.time() - startTime))          
##     return histogram

## ## @brief Return a ROOT TH2F object:
## #
## #  Custom plot to count the number of times that
## #  the TOT is 0 in both controllers
## #  while there are 1 or more strips hit in that plane
## ## @param rootTree
## #  The ROOT tree containing the variables.
## ## @param plotRep
## #  The custom plot representation from the pXmlParser object.

## def ToT_0_WhenTkrHitsExist_TowerPlane(rootTree, plotRep):
##     startTime = time.time()
##     xmin      = -0.5
##     xmax      = NUM_TKR_LAYER_PER_TOWER -0.5
##     xbins     = NUM_TKR_LAYERS_PER_TOWER
##     ymin      =  -0.5
##     ymax      = NUM_TOWERS -0.5
##     ybins     = NUM_TOWERS
##     histogram = ROOT.TH2F(plotRep.Name, plotRep.Title, xbins, xmin, xmax,
##                           ybins, ymin, ymax)

##     if rootTree.GetLeaf("TkrHitsTowerPlane") is None:
##         logger.warning('%s requires TkrHitsTowerPlane that is not in the processed tree' %\
##                        plotRep.getExpandedName(tower))
##         return histogram
##     if rootTree.GetLeaf("ToT_con0_TowerPlane") is None:
##         logger.warning('%s requires ToT_con0_TowerPlane that is not in the processed tree' %\
##                        plotRep.getExpandedName(tower))
##         return histogram
##     if rootTree.GetLeaf("ToT_con1_TowerPlane") is None:
##         logger.warning('%s requires ToT_con1_TowerPlane that is not in the processed tree' %\
##                        plotRep.getExpandedName(tower))
##         return histogram

## ##     for entry in rootTree:
## ##         for tower in xrange(NUM_TOWERS):
## ##             for layer in xrange(NUM_TKR_LAYERS_PER_TOWER):
## ##                 index = tower*NUM_TKR_LAYERS_PER_TOWER + layer
## ##                 nStrips = entry.TkrHitsTowerPlane[index]
## ##                 ToT0 = entry.ToT_con0_TowerPlane[index]
## ##                 ToT1 = entry.ToT_con1_TowerPlane[index]
                
## ##                 if nStrips>0 and ToT0==0 and ToT1==0 \
## ##                        and (eval(Root2PythonCutConverter(plotRep.Cut))):
## ##                     histogram.Fill(layer, tower)


##     rootTree.SetBranchStatus('*', 0)
##     rootTree.SetBranchStatus('TkrHitsTowerPlane', 1)
##     rootTree.SetBranchStatus('ToT_con0_TowerPlane', 1)
##     rootTree.SetBranchStatus('ToT_con1_TowerPlane', 1)
##     rootTree.SetBranchStatus('condsummary', 1)
    
##     lastFile = ROOT.gDirectory.GetPath()
##     tmpFile = ROOT.TFile('tmp.root','RECREATE')
##     tmpTree = rootTree.CopyTree(plotRep.Cut)
    
##     TkrHitsTowerPlane = numpy.zeros((16, 36), dtype=int)
##     ToT_con0_TowerPlane = numpy.zeros((16, 36), dtype=int)
##     ToT_con1_TowerPlane = numpy.zeros((16, 36), dtype=int)
##     tmpTree.SetBranchAddress('TkrHitsTowerPlane', TkrHitsTowerPlane)
##     tmpTree.SetBranchAddress('ToT_con0_TowerPlane', ToT_con0_TowerPlane)
##     tmpTree.SetBranchAddress('ToT_con1_TowerPlane', ToT_con1_TowerPlane)
##     for i in xrange(tmpTree.GetEntriesFast()):
##         tmpTree.GetEntry(i)
##         for tower in xrange(NUM_TOWERS):
##             for layer in xrange(NUM_TKR_LAYERS_PER_TOWER):
##                 nStrips = TkrHitsTowerPlane[tower][layer]
##                 ToT0 = ToT_con0_TowerPlane[tower][layer]
##                 ToT1 = ToT_con1_TowerPlane[tower][layer]
##                 if nStrips>0 and ToT0==0 and ToT1==0:
##                     histogram.Fill(layer, tower)

##     tmpFile.Close()
##     ROOT.gROOT.cd(lastFile)
##     rootTree.SetBranchStatus('*', 1)

##     logger.debug('%s created in %.2f s.' %\
##                  (plotRep.Name, time.time() - startTime))          
##     return histogram

## @brief  Return a ROOT TH2F object: Tower number vs Plane
# 
#  
## @param rootTree
#  The ROOT tree containing the variables.
## @param plotRep
#  The custom plot representation from the pXmlParser object.

def TkrTwrVsPlaneVariableCounter(rootTree, plotRep):
    startTime = time.time()
    xmin      = -0.5
    xmax      = NUM_TKR_LAYERS_PER_TOWER -0.5
    xbins     = NUM_TKR_LAYERS_PER_TOWER
    ymin      = -0.5
    ymax      = NUM_TOWERS -0.5
    ybins     = NUM_TOWERS
    histogram = ROOT.TH2F(plotRep.Name, plotRep.Title, xbins, xmin, xmax,
                          ybins, ymin, ymax)
    for tower in xrange(NUM_TOWERS):
        for layer in xrange(NUM_TKR_LAYERS_PER_TOWER):
            rootTree.Project("h1",\
                             plotRep.getExpandedExpression(tower, layer),\
                             plotRep.getExpandedCut(tower, layer))
            h1 = ROOT.gROOT.FindObjectAny("h1")
            entries = h1.GetEntries()
            histogram.Fill(layer, tower, entries)
            h1.Delete()
    logger.debug('%s created in %2.f s.' %\
                  (plotRep.Name, time.time() - startTime))
    return histogram


## @brief  Return a ROOT TH2F object: Tower number vs Plane
# 
#  
## @param rootTree
#  The ROOT tree containing the variables.
## @param plotRep
#  The custom plot representation from the pXmlParser object.

def TkrTwrVsPlaneVariableSumwx(rootTree, plotRep):
    startTime = time.time()
    xmin      = -0.5
    xmax      = NUM_TKR_LAYERS_PER_TOWER -0.5
    xbins     = NUM_TKR_LAYERS_PER_TOWER
    ymin      = -0.5
    ymax      = NUM_TOWERS -0.5
    ybins     = NUM_TOWERS
    histogram = ROOT.TH2F(plotRep.Name, plotRep.Title, xbins, xmin, xmax,
                          ybins, ymin, ymax)
    stats = array.array('d',7*[0.])
    for tower in xrange(NUM_TOWERS):
        for layer in xrange(NUM_TKR_LAYERS_PER_TOWER):
            rootTree.Project("h1",\
                             plotRep.getExpandedExpression(tower, layer),\
                             plotRep.getExpandedCut(tower, layer))
            h1 = ROOT.gROOT.FindObjectAny("h1")
            h1.GetStats(stats)
            histogram.Fill(layer, tower, stats[2])
            h1.Delete()
    logger.debug('%s created in %2.f s.' %\
                  (plotRep.Name, time.time() - startTime))
    return histogram
