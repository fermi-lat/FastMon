import logging
import ROOT
from pGlobals    import *

## @brief pCUSTOMplots 
#
#  It contains the definition of the methode to be called by CUSTOM plots
#  as declared in the xml configuration file.

## @brief Must return the custom ROOT histogram
## @param rootTree
#  The ROOT tree to be analyzed to create the plot
## @param name
#  The plot name as a string
## @param title
#  The plot title as a string
def tkr_tot_Test(rootTree, name, title):
    histo = ROOT.TH2F(name, title, 100, 0, 100, 100, 0, 100)
    rootTree.Project(name, "tkr_layer_tot[8][0][0]:tkr_layer_tot[8][0][1]")
    return histo
