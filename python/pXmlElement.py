
## @package pXmlElement
## @brief Description of an xml element.

import logging
import sys

from pGlobals import *


## @brief Class describing a xml element.
#
#  This class encapsulates the features that are shared by all the
#  pieces of the xml configuration files (which can describe lists,
#  variables, plots, etc.). In particular the methods for retrieving
#  the element name and the enable flag, along with those for
#  retrieving generic tag values, are provided.

class pXmlElement:

    ## @brief Constructor
    ## @param self
    #  The class instance.
    ## @param element
    #  A xml element, as returned by the getElementsByTagName()
    #  function of the xml.dom.minidom module.

    def __init__(self, element):

        ## @var Element
        ## @brief The xml element, as passed to the constructor.
        
        ## @var NodeName
        ## @brief The element node name (i.e. inputList, variable, etc).

        ## @var Name
        ## @brief The element name.

        ## @var Enabled
        ## @brief The element enable flag.
        
        self.Element  = element
        self.NodeName = self.Element.nodeName
        self.Name     = self.getName()
        self.Enabled  = self.isEnabled()


    ## @brief Return the element attribute corresponing to a
    #  given attribute name.
    #
    #  Note that the str() function which is applied before the value
    #  is returned transorms the unicode objects read from the xml files
    #  to standard strings (i.e. numpy.array does not like u'int' in place
    #  of 'int').
    ## @param self
    #  The class instance.
    ## @param attributeName
    #  The attribute name.

    def getAttribute(self, attributeName):
        return str(self.Element.getAttribute(attributeName))
 
    ## @brief Return the element attribute corresponing to a
    #  given attribute name, as processed by an eval statement.
    #
    #  This function can be used for conversions to int, float or generic
    #  objects.
    ## @param self
    #  The class instance.
    ## @param attributeName
    #  The attribute name.

    def evalAttribute(self, attributeName):
        try:
            return eval(self.getAttribute(attributeName))
        except:
            logging.warn('Could not eval attribute "%s" for element "%s"' %\
                         (attributeName, self.Name))
            return None

    ## @brief Return the 'name' attribute of the element.
    #
    #  Note that the 'name' attribute sohould be defined for each
    #  element.
    ## @param self
    #  The class instance.

    def getName(self):
        return self.getAttribute('name')

    ## @brief Return the 'enabled' attribute of the element.
    #
    #  Note that the 'enabled' attribute sohould be defined for each
    #  element.
    ## @param self
    #  The class instance.

    def isEnabled(self):
        return self.evalAttribute('enabled')

    ## @brief Return the child elements corresponding to a particular
    ## tag name.
    ## @param self
    #  The class instance.
    ## @param tagName
    #  The tag name.

    def getElementsByTagName(self, tagName):
        try:
            return self.Element.getElementsByTagName(tagName)
        except:
            return None

    ## @brief Return the value of the child tag corresponding to a
    #  given tag name.
    #
    #  Note that the execution is interrupted if the tag is defined multiple
    #  times.
    ## @param self
    #  The class instance.
    ## @param tagName
    #  The tag name.
    ## @param defaultValue
    #  The value to be returned in case the element does not have the
    #  specified tag.

    def getTagValue(self, tagName, defaultValue=None):
        elementsList = self.Element.getElementsByTagName(tagName)
        if len(elementsList) > 1:
            sys.exit('Multiple definition of tag %s. Exiting...' % tagName)
        try:
            return str(elementsList[0].childNodes[0].data).strip()
        except:
            return defaultValue

    ## @brief Return the value of the child tag corresponding to a
    #  given tag name, as returned by an eval statement.
    #
    #  Since this function call getTagValue(), the execution is interrupted
    #  if the tag is defined multiple times.
    ## @param self
    #  The class instance.
    ## @param tagName
    #  The tag name.
    ## @param defaultValue
    #  The value to be returned in case it's not possible to eval the
    #  specified tag.

    def evalTagValue(self, tagName, defaultValue=None):
        try:
            return eval(self.getTagValue(tagName))
        except:
            return defaultValue

    ## @brief Class representation.
    ## @param self
    #  The class instance. 

    def __str__(self):
        return 'NodeName  : %s\n' % self.NodeName +\
               'Name      : %s\n' % self.Name     +\
               'Enabled   : %s\n' % self.Enabled


if __name__ == '__main__':
    from xml.dom  import minidom
    doc = minidom.parse(file('config.xml'))
    for element in doc.getElementsByTagName('inputList'):
        print pXmlElement(element)
    for element in doc.getElementsByTagName('outputList'):
        print pXmlElement(element)
