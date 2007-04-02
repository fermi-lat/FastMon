## @package pCUSTOMplots
## @brief package containing the definition of the methods to be called
#  whenever a CUSTOM plot is declared in the xml configuration file.

import logging
import ROOT
import time
import numpy

from pGlobals    import *



## @brief Must return the custom ROOT histogram
## @param rootTree
#  The ROOT tree to be analyzed to create the plot
## @param name
#  The plot name as a string
## @param title
#  The plot title as a string

def tkr_2d_map1(rootTree, plotRep):
    startTime = time.time()
    xmin      = 0
    xmax      = NUM_TKR_LAYERS_PER_TOWER
    xbins     = 2*xmax
    ymin      = 0
    ymax      = NUM_TOWERS
    ybins     = ymax
    histogram = ROOT.TH2F(plotRep.Name, plotRep.Title, xbins, xmin, xmax,
                          ybins, ymin, ymax)
    for tower in range(NUM_TOWERS):
        for layer in range(NUM_TKR_LAYERS_PER_TOWER):
            for end in range(NUM_GTRC_PER_LAYER):
                rootTree.Project("h1",\
                             plotRep.getExpandedExpression(tower, layer, end),\
                             plotRep.getExpandedCut(tower, layer, end))
                h1 = ROOT.gROOT.FindObjectAny("h1")
                mean = h1.GetMean()
                histogram.Fill((layer + end/2.0 + 0.25), tower, mean)
                h1.Delete()
    logging.debug('TKR 2D map created in %s s.' % (time.time()-startTime))
    return histogram

def tkr_2d_map(rootTree, plotRep):
    startTime = time.time()
    xmin      = 0
    xmax      = NUM_TKR_LAYERS_PER_TOWER
    xbins     = 2*xmax
    ymin      = 0
    ymax      = NUM_TOWERS
    ybins     = ymax
    histogram = ROOT.TH2F(plotRep.Name, plotRep.Title, xbins, xmin, xmax,
                          ybins, ymin, ymax)
    means   = numpy.zeros((1152), dtype=int)
    entries = numpy.zeros((1152), dtype=int)
    for entry in rootTree:
        means   += entry.tkr_layer_end_strip_count
        entries += means > 0
    for tower in range(NUM_TOWERS):
        for layer in range(NUM_TKR_LAYERS_PER_TOWER):
            for end in range(NUM_GTRC_PER_LAYER):
                index = tower*36*2 + layer*2 +end
                try:
                    mean  = means[index]/float(entries[index])
                except ZeroDivisionError:
                    mean  = 0
                histogram.Fill((layer + end/2.0 + 0.25), tower, mean)
    logging.debug('TKR 2D map created in %s s.' % (time.time()-startTime))
    return histogram

