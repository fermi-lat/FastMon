
## @package pXmlList
## @brief Description of a xml list.

import logging

from pXmlElement import pXmlElement


## @brief Class describing a  xml (either input or output) list.
#
#  It is essentially a pXmlElement object with the additional Group
#  member. Subclassed in pXmlInputList and pXmlOutputList.

class pXmlList(pXmlElement):

    ## @brief Constructor
    ## @param self
    #  The class instance.
    ## @param element
    #  The xml element object representing the list. 

    def __init__(self, element):

        ## @var Group
        ## @brief The group which the list belongs to.
        
        pXmlElement.__init__(self, element)
        self.Group = self.getAttribute('group')

    ## @brief Class representation.
    ## @param self
    #  The class instance.

    def __str__(self):
        return pXmlElement.__str__(self)       +\
               'Group     : %s\n' % self.Group


if __name__ == '__main__':
    from xml.dom  import minidom
    doc = minidom.parse(file('config.xml'))
    for element in doc.getElementsByTagName('inputList'):
        print pXmlList(element)
    for element in doc.getElementsByTagName('outputList'):
        print pXmlList(element)
