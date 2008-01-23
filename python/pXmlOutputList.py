
## @package pXmlOutputList
## @brief Description of a xml output list for the data monitor.
#
#  It contains the definition of the output list and all the plot
#  representations.

import pSafeLogger
logger = pSafeLogger.getLogger('pXmlOutputList')

from pXmlElement    import pXmlElement
from pXmlList       import pXmlList
from pGlobals       import *
from pSafeROOT      import ROOT
from pCustomPlotter import pCustomPlotter

SUPPORTED_PLOT_TYPES = ['TH1F', 'TH2F', 'StripChart', 'RateStripChart',\
                        'CUSTOM']
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
        #
        #  Default is "".

        ## @var XLabel
        ## @brief The x axis label.
        #
        #  Default is "".
        
        ## @var YLabel
        ## @brief the y axis label.
        #
        #  Default is "".

        ## @var XLog
        ## @brief Flag for the log scale on the x axis (used for the report).
        #
        #  Default is False.

        ## @var YLog
        ## @brief Flag for the log scale on the y axis (used for the report).
        #
        #  Default is "".

        ## @var DrawOptions
        ## @brief Draw options used when the corresponding ROOT object(s)
        #  is (are) drawn on a canvas to be saved as image(s).
        #
        #  Default is "".

        ## @var Caption
        ## @brief The text of the plot caption for the test report.
        #
        #  Default is "".

        ## @var RootObjects
        ## @brief A dictionary containing the actual ROOT object(s)
        #  (maybe more than one, depending on the Level) to be written
        #  in the output tree along with the variables.
        
        pXmlElement.__init__(self, element)
        self.Level        = self.getAttribute('level', LAT_LEVEL)
        self.Title        = self.getTagValue('title')
        self.Expression   = self.getTagValue('expression')
        self.Cut          = self.getTagValue('cut'   , '')
        self.XLabel       = self.getTagValue('xlabel', '')
        self.YLabel       = self.getTagValue('ylabel', '')
        self.XLog         = self.evalTagValue('xlog', False)
        self.YLog         = self.evalTagValue('ylog', False)
        self.ZLog         = self.evalTagValue('zlog', False)
        self.DrawOptions  = self.getTagValue('drawoptions', '')
        self.Caption      = self.getTagValue('caption', '')
        self.RootObjects  = {}

    def draw(self, rootObject):
        rootObject.Draw(self.DrawOptions)

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
    ## @param end
    #  The TKR layer end (namely the id of the GTRC).
        
    def getSuffix(self, tower=None, layer=None, end=None):
        suffix = ''
        if tower is not None:
            suffix += '_Tower_%d' % tower
        if layer is not None:
            suffix += '_Layer_%d' % layer
        if end is not None:
            suffix += '_End_%d' % end
        return suffix


    ## @brief Return the plot name for a particular object (e.g. tower or
    #  tkr layer), in case the Level requires it.
    ## @param self
    #  The class instance.
    ## @param tower
    #  The tower Id.
    ## @param layer
    #  The TKR layer Id.
    ## @param end
    #  The TKR layer end (namely the id of the GTRC).

    def getExpandedName(self, tower=None, layer=None, end=None):
        return '%s%s' % (self.Name, self.getSuffix(tower, layer, end))

    ## @brief Return the plot title for a particular object (e.g. tower or
    #  tkr layer), in case the Level requires it.
    ## @param self
    #  The class instance.
    ## @param tower
    #  The tower Id.
    ## @param layer
    #  The TKR layer Id.
    ## @param end
    #  The TKR layer end (namely the id of the GTRC).

    def getExpandedTitle(self, tower=None, layer=None, end=None):
        return '%s%s' % (self.Title, self.getSuffix(tower, layer, end))

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
    ## @param end
    #  The TKR layer end (namely the id of the GTRC).

    def getExpandedExpression(self, tower=None, layer=None, end=None):
        expression = self.Expression
        if tower is not None:
            expression += '[%d]' % tower
        if layer is not None:
            expression += '[%d]' % layer
        if end is not None:
            expression += '[%d]' % end
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
    ## @param end
    #  The TKR layer end (namely the id of the GTRC).

    def getExpandedCut(self, tower=None, layer=None, end=None):
        return self.Cut.replace(self.getExpandedExpression(),\
                                self.getExpandedExpression(tower, layer, end))
                        
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

    ## @brief Get the list of names of the ROOT objects, as they would be
    #  created by createRootObjects().
    #
    #  This is ugly, but for the test report one needs to know this list
    #  to retrieve the objects from the ROOT file produced by the
    #  pRootTreeDataProcessor via the TFile.Get() function.
    ## @todo This could be probably implemented better.
    ## @param self
    #  The class instance.   

    def getRootObjectsName(self):
        namesList = []
        if self.Level == LAT_LEVEL:
            namesList.append(self.getExpandedName())
        elif self.Level == TOWER_LEVEL:
            for tower in range(NUM_TOWERS):
                namesList.append(self.getExpandedName(tower))
        elif self.Level == TKR_LAYER_LEVEL:
            for tower in range(NUM_TOWERS):
                for layer in range(NUM_TKR_LAYERS_PER_TOWER):
                    namesList.append(self.getExpandedName(tower, layer))
        return namesList

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
    ## @param rootTree
    #  The ROOT tree containing the (filled) branches from which the
    #  plots are created.
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
        
        pTH1FXmlRep.__init__(self, element)
        self.NumYBins = self.evalTagValue('ybins')
        self.YMin     = self.evalTagValue('ymin')
        self.YMax     = self.evalTagValue('ymax')

    ## @brief Return the actual ROOT histogram for the specified Level.
    ## @param self
    #  The class instance.
    ## @param rootTree
    #  The ROOT tree containing the (filled) branches from which the
    #  plots are created.
    ## @param tower
    #  The tower ID for the specified Level.
    ## @param layer
    #  The TKR layer ID for the specified Level.

    def getRootObject(self, rootTree, tower=None, layer=None):
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

    ## @brief Constructor
    ## @param self
    #  The class instance.
    ## @param element
    #  The xml element object representing the histogram. 

    def __init__(self, element):

        ## @var DTime
        ## @brief The width of the time bin.

        ## @var YMin
        ## @brief The minimum value on the y axis.

        ## @var YMax
        ## @brief The maximum value on the y axis.
        
        pPlotXmlRep.__init__(self, element)
        self.DTime = float(self.getTagValue('dtime'))
        self.YMin  = self.evalTagValue('ymin')
        self.YMax  = self.evalTagValue('ymax')

    ## @brief Return the actual ROOT histogram for the specified Level.
    ## @param self
    #  The class instance.
    ## @param rootTree
    #  The ROOT tree containing the (filled) branches from which the
    #  plots are created.
    ## @param tower
    #  The tower ID for the specified Level.
    ## @param layer
    #  The TKR layer ID for the specified Level.

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


## @brief Class describing the representation of a different strip chart
#  variant.
#
#  The profile histogram is scaled to the width of the time bin so that
#  it eventually contains rates, rather than number of events.

class pRateStripChartXmlRep(pStripChartXmlRep):

    ## @brief Constructor
    ## @param self
    #  The class instance.
    ## @param element
    #  The xml element object representing the histogram. 

    def __init__(self, element):
        pStripChartXmlRep.__init__(self, element)

    ## @brief Return the actual ROOT histogram for the specified Level.
    ## @param self
    #  The class instance.
    ## @param rootTree
    #  The ROOT tree containing the (filled) branches from which the
    #  plots are created.
    ## @param tower
    #  The tower ID for the specified Level.
    ## @param layer
    #  The TKR layer ID for the specified Level.
    
    def getRootObject(self, rootTree, tower=None, layer=None):
        profileTemp = pStripChartXmlRep.getRootObject(self, rootTree,\
                                                      tower=None, layer=None)
        profileTemp.Scale(profileTemp.GetSumOfWeights()/self.DTime)
        return profileTemp


## @brief Class describing the representation of a custom plot.

class pCUSTOMXmlRep(pPlotXmlRep):

    ## @brief Constructor
    ## @param self
    #  The class instance.
    ## @param element
    #  The xml element object representing the histogram. 

    def __init__(self, element):

        ## @var Type
        ## @brief The type of custom plot.
        #
        #  The type is defined in the xml configuration file and a
        #  corresponding function, whose name must match the type exactly,
        #  must be defined in the @ref pCustomPlotter package.

        ## @var ExcludedValues
        ## @brief Relevant for the tkr_2d_map custom plot type.
        #
        #  See the code for details.
        
        pPlotXmlRep.__init__(self, element)
	self.Type           = element.getAttribute('type')
        self.ExcludedValues = self.evalTagValue('exclude')
        self.Plotter = None

    def setPlotter(self, customPlotter):
        self.Plotter = customPlotter

    ## @brief Return the custom ROOT histogram
    ## @param self
    #  The class instance.
    ## @param rootTree
    #  The ROOT tree.

    def getRootObjects(self, rootTree, tower=None, layer=None):
        try:
            histograms = eval('self.Plotter.%s(self)' % self.Type)
        except AttributeError:
            logger.error('Type %s not defined in pCustomPlotter.' % self.Type)
            logger.info('Returning an empty histogram list.')
            return []
        for histogram in histograms:
            histogram.GetXaxis().SetTitle(self.XLabel)
            histogram.GetYaxis().SetTitle(self.YLabel)
        return histograms

    ## @brief Overloaded method.
    # 
    #  The intention would be to get rid of the "level" concept for
    #  the custom plots. In this case the code has to be written from
    #  scratch anyway so that it is probably worth to code the loop over
    #  towers, layers, front end etc. explicitely. Following this approach we
    #  need to modify the pCustomPlotter methods in order to return lists
    #  of histograms rather than single histograms; this method takes care of
    #  appending the list properly to the global dictionary of ROOT objects.
    #
    #  Note that the level must be defined in the xml file anyway, in order
    #  for the output lists to be properly populated.

    def createRootObjects(self, rootTree):
        objects = self.getRootObjects(rootTree)
        for object in objects:
            self.RootObjects[object.GetName()] = object


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
