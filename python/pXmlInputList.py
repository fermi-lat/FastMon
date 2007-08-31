
## @package pXmlInputList
## @brief Description of a xml input list for the data monitor.
#
#  It contains the definition of the input list and of the variable
#  class.

import numpy
import sys

from pXmlElement import pXmlElement
from pXmlList    import pXmlList
from pGlobals    import *


NUMPY_TO_ROOT_TYPE_MAP = {'int8'   : 'B',#an 8 bit signed integer (Char_t)
                          'uint8'  : 'b',#an 8 bit unsigned integer (UChar_t)
                          'int16'  : 'S',#a 16 bit signed integer (Short_t)
                          'uint16' : 's',#a 16 bit unsigned integer (UShort_t)
                          'int32'  : 'I',#a 32 bit signed integer (Int_t)
                          'uint32' : 'i',#a 32 bit unsigned integer (UInt_t)
                          'float32': 'F',#a 32 bit floating point (Float_t)
                          'float64': 'D',#a 64 bit floating point (Double_t)
                          'int64'  : 'L',#a 64 bit signed integer (Long64_t)
                          'uint64' : 'l',#a 64 bit unsigned integer (ULong64_t)
                          'bool_'  : 'O',#a boolean (Bool_t)}
                          'int'    : 'I',
                          'float'  : 'F',
                          'double' : 'D'
                          }

## @brief Class describing a variable to be monitored (i.e to be written
#  in the output root tree by the monitor).

class pRootTreeVariable(pXmlElement):

    ## @brief Constructor
    ## @param self
    #  The class instance.
    ## @param element
    #  The xml element object representing the variable. 

    def __init__(self, element):

        ## @var Type
        ## @brief The variable base type (e.g. int, float, etc).

        ## @var Shape
        ## @brief The dimension(s) of the base array filling the tree.
        
        ## @var LeafList
        ## @brief Parameter to be passed to the ROOT function creating the
        #  tree branches.
        
        ## @var Array
        ## @brief The underlying numpy object filling the tree.
        
        pXmlElement.__init__(self, element)
        self.Name     = '%s%s' % (FAST_MON_PREFIX, self.Name)
        self.Type     = self.getTagValue('type')
        self.Shape    = self.evalTagValue('shape')
        self.LeafList = self.__getLeafList()
        self.Array    = numpy.zeros(self.Shape, self.Type)
        self.Reset    = self.evalAttribute('reset', True)

    ## @brief Reset to 0 the underlying numpy array.
    ## @param self
    #  The class instance.

    def reset(self):
        if self.Reset:
            self.Array.fill(0)
        

    ## @brief Return the LeafList for the ROOT function creating the branches.
    ## @param self
    #  The class instance.

    def __getLeafList(self):
        leafList = self.getName()
        try:
            for dimension in self.Shape:
                leafList += '[%d]' % dimension
        except TypeError:
            leafList += '[%d]' % self.Shape
        leafList += '/%s' % NUMPY_TO_ROOT_TYPE_MAP[self.Type]
        return leafList

    ## @brief Class representation.
    ## @param self
    #  The class instance.

    def __str__(self):
        return pXmlElement.__str__(self)            +\
               'Type      : %s\n' % self.Type       +\
               'Shape     : %s\n' % str(self.Shape) +\
               'Leafs list: %s\n' % self.LeafList


## @brief Class describing an input list to the data monitor (i.e. a
#  list of pRootTreeVariable objects to be eventually written in the
#  output root tree).

class pXmlInputList(pXmlList):

    ## @brief Constructor
    ## @param self
    #  The class instance.
    ## @param element
    #  The xml element object representing the list.

    def __init__(self, element):

        ## @var VariablesDict
        ## @brief Collection of all the variables included in the list.
        
        ## @var EnabledVariablesDict
        ## @brief Collection of the enabled variables included in the list.
        #
        #  Since most likely this is the relevant list of variables,
        #  it is statically filled in the constructor, rather than
        #  dinamically created at runtime to optimize speed.
        
        pXmlList.__init__(self, element)
        self.VariablesDict        = {}
        self.EnabledVariablesDict = {}
        for element in self.getElementsByTagName('variable'):
            variable = pRootTreeVariable(element)
            self.VariablesDict[variable.Name] = variable
            if variable.Enabled:
                self.EnabledVariablesDict[variable.Name] = variable

    ## @brief Class representation.
    ## @param self
    #  The class instance.

    def __str__(self):
        return pXmlList.__str__(self)                                +\
               'Variables        : %s\n' % self.VariablesDict.keys() +\
               'Enabled variabled: %s\n' % self.EnabledVariablesDict.keys()



if __name__ == '__main__':
    from xml.dom  import minidom
    doc = minidom.parse(file('config.xml'))
    for element in doc.getElementsByTagName('inputList'):
        print pXmlInputList(element)
