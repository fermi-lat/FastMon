## @package pCUSTOMplots
## @brief package containing the definition of the methods to be called
#  whenever a CUSTOM plot is declared in the xml configuration file.

import logging
import ROOT
import time
import numpy

from pGlobals    import *


## @brief Method mapping the content of a gem 16 bit register to the
#  corresponding tower and returning a TH1F object.
## @param rootTree
#  The ROOT tree containing the variables.
## @param plotRep
#  The custom plot representation from the pXmlParser object.

def gem_vector_map(rootTree, plotRep):
    startTime = time.time()
    histogram = ROOT.TH1F(plotRep.Name, plotRep.Title, 16, 0, 16)
    histogram.SetMinimum(0)
    for entry in rootTree:
        for tower in range(NUM_TOWERS):
            if eval('entry.%s & (0x1 << tower)' % plotRep.Expression):
                histogram.Fill(tower)
    logging.debug('Custom plot %s created in %s s.' %\
                  (plotRep.Name, time.time() - startTime))
    return histogram


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
        for i in range(NUM_TKR_GTRC):
            values[i] = buffer[i]
        status = numpy.ones((NUM_TKR_GTRC), dtype=int)
        means += values
        for value in plotRep.ExcludedValues:
            status = status*(values != value)
        entries += status
    for tower in range(NUM_TOWERS):
        for layer in range(NUM_TKR_LAYERS_PER_TOWER):
            for end in range(NUM_GTRC_PER_LAYER):
                index = tower*NUM_TKR_LAYERS_PER_TOWER*NUM_GTRC_PER_LAYER +\
                        layer*NUM_GTRC_PER_LAYER +end
                if entries[index] == 0:
                    mean  = 0
                else:
                    mean  = means[index]/float(entries[index])
                histogram.Fill((layer + end/2.0 + 0.25), tower, mean)
    logging.debug('Custom plot %s created in %s s.' %\
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
    logging.debug('Custom plot %s created in %s s.' %\
                  (plotRep.Name, time.time() - startTime))
    return histogram


## @brief Return a...

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
        for i in range(NUM_CAL_LAYERS):
            values[i] = buffer[i]
        status = numpy.ones((NUM_CAL_LAYERS), dtype=int)
        means += values
        for value in plotRep.ExcludedValues:
            status = status*(values != value)
        entries += status
    for tower in range(NUM_TOWERS):
        for layer in range(NUM_CAL_LAYERS_PER_TOWER):
            index = tower*NUM_CAL_LAYERS_PER_TOWER + layer
            if entries[index] == 0:
                mean  = 0
            else:
                mean  = means[index]/float(entries[index])
            histogram.Fill((layer + 0.25), tower, mean)
    logging.debug('Custom plot %s created in %s s.' %\
                  (plotRep.Name, time.time() - startTime))
    return histogram