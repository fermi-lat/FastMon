
## @package pXmlOutputList
## @brief Description of a xml output list for the data monitor.
#
#  It contains the definition of the output list and all the plot
#  representations.

import logging
import ROOT

from pXmlElement import pXmlElement
from pXmlList    import pXmlList
from pGlobals    import *

SUPPORTED_PLOT_TYPES = ['TH1F', 'TH2F', 'StripChart']
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

        ## @var RootObjects
        ## @brief A dictionary containing the actual ROOT object(s)
        #  (maybe more than one, depending on the Level) to be written
        #  in the output tree along with the variables.
        
        pXmlElement.__init__(self, element)
        self.Level       = self.getAttribute('level')
        if self.Level == None:
            self.Level = LAT_LEVEL
        self.Title       = self.getTagValue('title')
        self.Expression  = self.getTagValue('expression')
        self.Cut         = self.getTagValue('cut')
        if self.Cut is None:
            self.Cut = ''
        self.RootObjects = {}

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

    def getExpression(self, tower=None, layer=None):
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

    def getCut(self, tower=None, layer=None):
        return self.Cut.replace(self.getExpression(),\
                                self.getExpression(tower, layer))
  
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
        name      = '%s%s' % (self.getName(), self.getSuffix(tower, layer))
        title     = '%s%s' % (self.Title, self.getSuffix(tower, layer))
        histogram = ROOT.TH1F(name, title, self.NumXBins, self.XMin, self.XMax)
        expression = self.getExpression(tower, layer)
        cut        = self.getCut(tower, layer)
        rootTree.Project(histogram.GetName(), expression, cut)
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
        name      = '%s%s' % (self.getName(), self.getSuffix(tower, layer))
        title     = '%s%s' % (self.Title, self.getSuffix(tower, layer))
        histogram = ROOT.TH2F(name, title,\
                              self.NumXBins, self.XMin, self.XMax,\
                              self.NumYBins, self.YMin, self.YMax)
        expression = self.getExpression(tower, layer)
        cut        = self.getCut(tower, layer)
        rootTree.Project(histogram.GetName(), expression, cut)
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
        name       = '%s%s' % (self.getName(), self.getSuffix(tower, layer))
        title      = '%s%s' % (self.Title, self.getSuffix(tower, later))
	tmin = rootTree.GetMinimum('event_timestamp')
        tmax = rootTree.GetMaximum('event_timestamp')

	# ymin and ymax may be passed in the xml if not try to get them from the tree
        # GetMaximum works only on direct tree variable (e.g. not on cal_log_count[i])
	# Need to implement something better
	expression = self.getExpression()
        if self.YMin is None:
	  self.YMin = rootTree.GetMinimum(expression)
        if self.YMax is None:
	  self.YMax = rootTree.GetMaximum(expression)
	  
        #logging.debug('StripChart %s: tmin=%d tmax=%d ymin=%d ymax=%d' %\
	#		(expression, tmin, tmax, self.YMin, self.YMax) )
        nTimeBin = int((tmax-tmin)/self.DTime)
	htemp = ROOT.TH2F('htemp', 'htemp', nTimeBin, tmin, tmax, 100, self.YMin,self.YMax)
	#Cut is always on the variable itself now : should come from xml
        expression = self.getExpression(tower, layer)
        cut        = self.getCut(tower, layer)
	rootTree.Project('htemp', '%s:event_timestamp'% expression, cut)
        profile = htemp.ProfileX()
        profile.SetNameTitle(name, title)
        del htemp
	return  profile

    def __str__(self):
        return pPlotXmlRep.__str__(self)
    

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
               'Enabled variabled: %s\n' % self.EnabledPlotRepsDict.keys()


if __name__ == '__main__':
    from xml.dom  import minidom
    doc = minidom.parse(file('../xml/config.xml'))
    for element in doc.getElementsByTagName('outputList'):
        list = pXmlOutputList(element)
        print list
        for plotRep in list.PlotRepsDict.values():
            print plotRep
