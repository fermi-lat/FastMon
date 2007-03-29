
## @package pXmlOutputList
## @brief Description of a xml output list for the data monitor.
#
#  It contains the definition of the output list and all the plot
#  representations.

import logging
import ROOT

from pXmlElement   import pXmlElement
from pXmlList      import pXmlList
from pAlarmHandler import *
from pGlobals      import *

import pCUSTOMplots
from pCUSTOMplots    import *


SUPPORTED_PLOT_TYPES = ['TH1F', 'TH2F', 'StripChart', 'CUSTOM']
LAT_LEVEL            = 'lat'
TOWER_LEVEL          = 'tower'
TKR_LAYER_LEVEL      = 'tkr_layer'


## @brief Class describing the representation of a generic plot.
#
#  The possibility of producing the same plot for multiple objects
#  (e.g. per tower, per layer, etc) is implemented through the Level
#  member, provided that the input variable is multi-dimensional.

class pPlotXmlRep(pXmlElement):

    ## @brief Constructor
    ## @param self
    #  The class instance.
    ## @param element
    #  The xml element object representing the plot. 

    def __init__(self, element):

        ## @var Level
        ## @brief The level at which the plot(s) must be created.
        #
        #  If not specified it is set to LAT_LEVEL (one single cumulative plot
        #  for the specified variable).

        ## @var Title
        ## @brief The title of the plot.

        ## @var Expression
        ## @brief The input variable(s) for the plot.

        ## @var Cut
        ## @brief An optional cut which can be applied on the plot.

        ## @var XLabel
        ## @brief The x axis label.

        ## @var YLabel
        ## @brief the y axis label.

        ## @var XLog
        ## @brief Flag for the log scale on the x axis (used for the report).

        ## @var YLog
        ## @brief Flag for the log scale on the y axis (used for the report).

        ## @var AlarmHandler
        ## @brief The Alarm handler for the plot.

        ## @var RootObjects
        ## @brief A dictionary containing the actual ROOT object(s)
        #  (maybe more than one, depending on the Level) to be written
        #  in the output tree along with the variables.
        
        pXmlElement.__init__(self, element)
        self.Level       = self.getAttribute('level')
        if self.Level == '':
            self.Level = LAT_LEVEL
        self.Title        = self.getTagValue('title')
        self.Expression   = self.getTagValue('expression')
        self.Cut          = self.getTagValue('cut'   , '')
        self.XLabel       = self.getTagValue('xlabel', '')
        self.YLabel       = self.getTagValue('ylabel', '')
        self.XLog         = self.evalTagValue('xlog', False)
        self.YLog         = self.evalTagValue('ylog', False)
        self.RootObjects  = {}

    ## @brief Return the suffix to be attached to the plot name or
    #  title for a particular object (e.g. tower or tkr layer), in case
    #  the Level requires it.
    #
    #  Other levels (i.e. cal rows, columns or crystals) can be implemented
    #  if needed.
    ## @param self
    #  The class instance.
    ## @param tower
    #  The tower Id.
    ## @param layer
    #  The TKR layer Id.
        
    def getSuffix(self, tower=None, layer=None):
        suffix = ''
        if tower is not None:
            suffix += '_tower_%d' % tower
        if layer is not None:
            suffix += '_layer_%d' % layer
        return suffix


    ## @brief Return the plot name for a particular object (e.g. tower or
    #  tkr layer), in case the Level requires it.
    ## @param self
    #  The class instance.
    ## @param tower
    #  The tower Id.
    ## @param layer
    #  The TKR layer Id.

    def getExpandedName(self, tower=None, layer=None):
        return '%s%s' % (self.Name, self.getSuffix(tower, layer))

    ## @brief Return the plot title for a particular object (e.g. tower or
    #  tkr layer), in case the Level requires it.
    ## @param self
    #  The class instance.
    ## @param tower
    #  The tower Id.
    ## @param layer
    #  The TKR layer Id.

    def getExpandedTitle(self, tower=None, layer=None):
        return '%s%s' % (self.Title, self.getSuffix(tower, layer))

    ## @brief Modify the base Expression for a particular object (e.g. tower
    #  or tkr layer), in case the Level requires it. 
    #
    #  Other levels (i.e. cal rows, columns or crystals) can be implemented
    #  if needed.
    ## @param self
    #  The class instance.
    ## @param tower
    #  The tower Id.
    ## @param layer
    #  The TKR layer Id.

    def getExpandedExpression(self, tower=None, layer=None):
        expression = self.Expression
        if tower is not None:
            expression += '[%d]' % tower
        if layer is not None:
            expression += '[%d]' % layer
        return expression

    ## @brief Modify the base Cut for a particular object (e.g. tower
    #  or tkr layer), in case the Level requires it. 
    #
    #  Other levels (i.e. cal rows, columns or crystals) can be implemented
    #  if needed.
    ## @param self
    #  The class instance.
    ## @param tower
    #  The tower Id.
    ## @param layer
    #  The TKR layer Id.

    def getExpandedCut(self, tower=None, layer=None):
        return self.Cut.replace(self.getExpandedExpression(),\
                                self.getExpandedExpression(tower, layer))

    ## @brief Add the alarms defined for the plot rep to the specified
    #  alarm handler.
    ## @param self
    #  The class instance.
    ## @param handler
    #  The alarm handler.

    def addAlarms(self, handler):
        for element in self.getElementsByTagName('alarm'):
            if self.Level == LAT_LEVEL:
                handler.addAlarm(pAlarm(element), self.getExpandedName())
            elif self.Level == TOWER_LEVEL:
                for tower in range(NUM_TOWERS):
                    handler.addAlarm(pAlarm(element),\
                                     self.getExpandedName(tower))
            elif self.Level == TKR_LAYER_LEVEL:
                for tower in range(NUM_TOWERS):
                    for layer in range(NUM_TKR_LAYERS_PER_TOWER):
                        handler.addAlarm(pAlarm(element),\
                                         self.getExpandedName(tower, layer))
                        
    ## @brief Create the actual ROOT objects.
    ## @param self
    #  The class instance.
    ## @param rootTree
    #  The ROOT tree containing the (filled) branches from which the
    #  plots are created.
    
    def createRootObjects(self, rootTree):
        if self.Level == LAT_LEVEL:
            object = self.getRootObject(rootTree)
            self.RootObjects[object.GetName()] = object
        elif self.Level == TOWER_LEVEL:
            for tower in range(NUM_TOWERS):
                object = self.getRootObject(rootTree, tower)
                self.RootObjects[object.GetName()] = object
        elif self.Level == TKR_LAYER_LEVEL:
            for tower in range(NUM_TOWERS):
                for layer in range(NUM_TKR_LAYERS_PER_TOWER):
                    object = self.getRootObject(rootTree, tower, layer)
                    self.RootObjects[object.GetName()] = object

    def activateAlarms(self, handler):
        for plot in self.RootObjects.values():
            handler.activateAlarms(plot)

    ## @brief Class representation.
    ## @param self
    #  The class instance.

    def __str__(self):
        return pXmlElement.__str__(self)            +\
               'Level     : %s\n' % self.Level      +\
               'Title     : %s\n' % self.Title      +\
               'Expression: %s\n' % self.Expression +\
               'Cut       : %s\n' % self.Cut


## @brief Class describing the representation of a 1-D histogram.

class pTH1FXmlRep(pPlotXmlRep):

    ## @brief Constructor
    ## @param self
    #  The class instance.
    ## @param element
    #  The xml element object representing the histogram. 

    def __init__(self, element):

        ## @var NumXBins
        ## @brief The number of bins on the x axis.

        ## @var XMin
        ## @brief The minimum value on the x axis.
        
        ## @var XMax
        ## @brief The maximum value on the x axis.
        
        pPlotXmlRep.__init__(self, element)
        self.NumXBins = self.evalTagValue('xbins')
        self.XMin     = self.evalTagValue('xmin')
        self.XMax     = self.evalTagValue('xmax')

    ## @brief Return the actual ROOT histogram for the specified Level.
    ## @param self
    #  The class instance.
    ## @param tower
    #  The tower ID for the specified Level.
    ## @param layer
    #  The TKR layer ID for the specified Level.

    def getRootObject(self, rootTree, tower=None, layer=None):
        histogram = ROOT.TH1F(self.getExpandedName(tower, layer),\
                              self.getExpandedTitle(tower, layer),\
                              self.NumXBins, self.XMin, self.XMax)
        histogram.GetXaxis().SetTitle(self.XLabel)
        histogram.GetYaxis().SetTitle(self.YLabel)
        rootTree.Project(histogram.GetName(),\
                         self.getExpandedExpression(tower, layer),\
                         self.getExpandedCut(tower, layer))
        return histogram

    ## @brief Class representation.
    ## @param self
    #  The class instance.

    def __str__(self):
        return pPlotXmlRep.__str__(self)          +\
               'X bins    : %s\n' % self.NumXBins +\
               'X min     : %s\n' % self.XMin     +\
               'X max     : %s\n' % self.XMax


## @brief Class describing the representation of a 2-D histogram.

class pTH2FXmlRep(pTH1FXmlRep):

    ## @brief Constructor
    ## @param self
    #  The class instance.
    ## @param element
    #  The xml element object representing the histogram. 

    def __init__(self, element):

        ## @var NumYBins
        ## @brief The number of bins on the y axis.

        ## @var YMin
        ## @brief The minimum value on the y axis.
        
        ## @var YMax
        ## @brief The maximum value on the y axis.
        
        pTH1XmlRep.__init__(self, element)
        self.NumYBins = self.evalTagValue('ybins')
        self.YMin     = self.evalTagValue('ymin')
        self.YMax     = self.evalTagValue('ymax')

    ## @brief Return the actual ROOT histogram for the specified Level.
    ## @param self
    #  The class instance.
    ## @param tower
    #  The tower ID for the specified Level.
    ## @param layer
    #  The TKR layer ID for the specified Level.

    def getRootObject(self, tower=None, layer=None):
        histogram = ROOT.TH2F(self.getExpandedName(tower, layer),\
                              self.getExpandedTitle(tower, layer),\
                              self.NumXBins, self.XMin, self.XMax,\
                              self.NumYBins, self.YMin, self.YMax)
        histogram.GetXaxis().SetTitle(self.XLabel)
        histogram.GetYaxis().SetTitle(self.YLabel)
        rootTree.Project(histogram.GetName(),\
                         self.getExpandedExpression(tower, layer),\
                         self.getExpandedCut(tower, layer))
        return histogram

    ## @brief Class representation.
    ## @param self
    #  The class instance.

    def __str__(self):
        return pTH1FXmlRep.__str__(self)          +\
               'Y bins    : %s\n' % self.NumYBins +\
               'Y min     : %s\n' % self.YMin     +\
               'Y max     : %s\n' % self.YMax
    

## @brief Class describing the representation of a strip chart.
## @todo Much work to be done here.

class pStripChartXmlRep(pPlotXmlRep):

    def __init__(self, element):
        pPlotXmlRep.__init__(self, element)
        self.DTime = float(self.getTagValue('dtime'))
        self.YMin     = self.evalTagValue('ymin')
        self.YMax     = self.evalTagValue('ymax')

    def getRootObject(self, rootTree, tower=None, layer=None):
	tmin = rootTree.GetMinimum('event_timestamp')
        tmax = rootTree.GetMaximum('event_timestamp')
	# ymin and ymax may be passed in the xml if not try to get
        #them from the tree
        # GetMaximum works only on direct tree variable (e.g. not on
        #cal_log_count[i])
	# Need to implement something better
	expression = self.getExpandedExpression()
        if self.YMin is None:
	  self.YMin = rootTree.GetMinimum(expression)
        if self.YMax is None:
	  self.YMax = rootTree.GetMaximum(expression)
	  
        #logging.debug('StripChart %s: tmin=%d tmax=%d ymin=%d ymax=%d' %\
	#		(expression, tmin, tmax, self.YMin, self.YMax) )
        nTimeBin = int((tmax-tmin)/self.DTime)
	htemp = ROOT.TH2F('htemp', 'htemp', nTimeBin, tmin, tmax, 100,\
                          self.YMin,self.YMax)
	#Cut is always on the variable itself now : should come from xml
        expression = self.getExpandedExpression(tower, layer)
        cut        = self.getExpandedCut(tower, layer)
	rootTree.Project('htemp', '%s:event_timestamp'% expression, cut)
        profile = htemp.ProfileX()
        profile.SetNameTitle(self.getExpandedName(tower, layer),\
                             self.getExpandedTitle(tower, layer))
        profile.GetXaxis().SetTitle(self.XLabel)
        profile.GetYaxis().SetTitle(self.YLabel)
        del htemp
	return  profile

    def __str__(self):
        return pPlotXmlRep.__str__(self)
    

## @brief Class describing the representation of a CUSTOM plot

class pCUSTOMXmlRep(pPlotXmlRep):

    ## @brief Constructor
    ## @param self
    #  The class instance.
    ## @param element
    #  The xml element object representing the histogram. 

    def __init__(self, element):

        ## @brief The number of bins on the x axis.
	## Basically need to take title
	## Potentialy also axis labels
        
        pPlotXmlRep.__init__(self, element)

    ## @brief Return the custom ROOT histogram
    ## @param self
    #  The class instance.
    ## @param tower
    #  The tower ID for the specified Level.
    ## @param layer
    #  The TKR layer ID for the specified Level.

    def getRootObject(self, rootTree, tower=None, layer=None):
        name       = '%s%s' % (self.getName(), self.getSuffix(tower, layer))
        title      = '%s%s' % (self.Title, self.getSuffix(tower, layer))
        cmd = 'pCUSTOMplots.%s(rootTree, "%s", "%s")' % (name, name, title)
	histogram = eval(cmd)
        return histogram


## @brief Class describing an output list for the data monitor (i.e. a
#  list of representations of the ROOT plots to be filled and saved when
#  the output tree is completed).

class pXmlOutputList(pXmlList):

    ## @brief Constructor
    ## @param self
    #  The class instance.
    ## @param element
    #  The xml element object representing the list.    

    def __init__(self, element):

        ## @var PlotRepsDict
        ## @brief Dictionary containing all the plot representations in the
        #  output list, indexed by plot name.

        ## @var EnabledPlotRepsDict
        ## @brief Dictionary containing all the enabled plot representations
        #  in the output list, indexed by plot name.
        
        pXmlList.__init__(self, element)
        self.PlotRepsDict        = {}
        self.EnabledPlotRepsDict = {}
        for plotType in SUPPORTED_PLOT_TYPES:
            for element in self.getElementsByTagName(plotType):
                plotRep = eval('p%sXmlRep(element)' % plotType)
                self.PlotRepsDict[plotRep.Name] = plotRep
                if plotRep.Enabled:
                    self.EnabledPlotRepsDict[plotRep.Name] = plotRep
	
    ## @brief Class representation.
    ## @param self
    #  The class instance.

    def __str__(self):
        return pXmlList.__str__(self)         +\
               'Variables        : %s\n' % self.PlotRepsDict.keys()       +\
               'Enabled variables: %s\n' % self.EnabledPlotRepsDict.keys()


if __name__ == '__main__':
    from xml.dom  import minidom
    doc = minidom.parse(file('../xml/config.xml'))
    for element in doc.getElementsByTagName('outputList'):
        list = pXmlOutputList(element)
        print list
        for plotRep in list.PlotRepsDict.values():
            print plotRep
