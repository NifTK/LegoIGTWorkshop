#########################################################################################
### Name convention: Gui Object should have suffix CB for Collapsible
### Button, TB toolbox button etc...
#########################################################################################
import struct
import os
from __main__ import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import math

import socket
import sys

"""Uses ScriptedLoadableModule base class, available at:
https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
"""

#########################################################################################
####                                                                                 ####
####  Lego Workshop ########################################################
####                                                                                 ####
#########################################################################################
class LegoWorkshop(ScriptedLoadableModule):
    #########################################################################################
    #### __init__
    #########################################################################################
    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "1. Lego Workshop"
        self.parent.categories = ["LEGO"]
        self.parent.dependencies = []
        self.parent.contributors = ["John O'Neill (UCL)"]
        self.parent.helpText = """This module is meant to communicate with a LEGO EV3 robot."""
        self.parent.acknowledgementText = """This file was blatantly plagarized from Gabriele Arnulfo & Massimo Narizzano"""

        ## READ the configuration files under the Config/ directory
        self.parentPath = os.path.dirname(parent.path)




#########################################################################################
####                                                                                 ####
####  LegoWorkshopWidget                                                 ####
####                                                                                 ####
#########################################################################################
class LegoWorkshopWidget(ScriptedLoadableModuleWidget):
    #######################################################################################
    ### setup
    #######################################################################################
    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)
        #### Some variables
        self.configurationSetup()
        self.commandSetup()


        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = '1.1.1.1'
        self.server_port = 3148
        

    #######################################################################################
    ### configurationSetup
    ### Collapsible button, where are stored the information for the command module
    ### for example the deeto executable location, etc...
    #######################################################################################
    def configurationSetup(self):
        #### Create a Collapsible Button
        self.setupCB = ctk.ctkCollapsibleButton()
        self.setupCB.text = "LegoWorkshop - Configuration"
        self.setupCB.collapsed = True
        self.layout.addWidget(self.setupCB)

        #### Collapsible button layout
        self.setupFL = qt.QFormLayout(self.setupCB)

        #### Tool Box for changing deeto Executable
        self.deetoTB = qt.QToolButton()
        self.deetoTB.setText("Connect")
        self.deetoTB.toolTip = "Change Server Address"
        self.deetoTB.enabled = True
        self.deetoTB.connect('clicked(bool)', self.ondeetoTB)


        #### Buttons Layout
        self.deetoButtonsHBL = qt.QHBoxLayout()
#        self.deetoButtonsHBL.addWidget(self.deetoLE)
        self.addressBox = qt.QLineEdit("192.168.0.5");
        self.portBox = qt.QLineEdit("3148");
        self.deetoButtonsHBL.addWidget(self.addressBox)
        self.deetoButtonsHBL.addWidget(self.portBox)
        self.deetoButtonsHBL.addWidget(self.deetoTB)

        #### Aggiungo il bottone al layout
        self.setupFL.addRow("Server Location: ", self.deetoButtonsHBL)

        #### Button to change the deeto executable location
        #### It is called in ondeetoTB, when deetoTB is selected
        #self.addressBox.setFileMode(qt.QFileDialog.AnyFile)
        #self.addressBox.setToolTip("Pick the input to the algorithm.")

    #######################################################################################
    ### commandSetup #
    #######################################################################################
    def commandSetup(self):

        #### Collapsible Button --- General Frame
        self.commandCB = ctk.ctkCollapsibleButton()
        self.commandCB.text = "LegoWorkshop - command"
        self.commandCB.contentsLineWidth = 1
        self.layout.addWidget(self.commandCB)
        #### Collapsible Button layout
        self.commandFL = qt.QFormLayout(self.commandCB)

        #### Choose Fiducial - Section
        #### Select box ComboBox -
        self.fiducialCBox = slicer.qMRMLNodeComboBox()
        self.fiducialCBox.nodeTypes = (("vtkMRMLMarkupsFiducialNode"), "")
        self.fiducialCBox.selectNodeUponCreation = False
        self.fiducialCBox.addEnabled = False
        self.fiducialCBox.removeEnabled = False
        self.fiducialCBox.noneEnabled = True
        self.fiducialCBox.setMRMLScene(slicer.mrmlScene)
        self.fiducialCBox.setToolTip("Select a fiducial list")
        #### Add fiducial to the Collapsible Button
        self.commandFL.addRow("Fiducial List", self.fiducialCBox)
        #### Connect the fiducial list to the
        self.fiducialCBox.connect('currentNodeChanged(bool)', self.onfiducialCBox)

        #### Configure command - Section
        ### Read from files the list of the modules
        #with open(slicer.modules.LegoWorkshopInstance.electrodeTypesPath) as data_file:
            # models is a dictionary with the name of electrode type is the key
        #    self.models = json.load(data_file)

        #### Create the caption table for the configuration
        self.tableCaption = ["Name", "Position", "", ""]
        self.tableHsize = [80, 180, 50, 50]
        self.captionGB = qt.QGroupBox(self.commandCB)
        self.captionBL = qt.QHBoxLayout(self.captionGB)
        self.captionBL.setMargin(1)
        for i in (xrange(len(self.tableCaption))):
            a = qt.QLabel(self.tableCaption[i], self.captionGB)
            a.setMaximumWidth(self.tableHsize[i])
            a.setMaximumHeight(20)
            a.setStyleSheet("qproperty-alignment: AlignCenter;")
            self.captionBL.addWidget(a)

        self.commandFL.addRow("", self.captionGB)

    #######################################################################################
    # onfiducialCBox   #
    #  Create dynamically the electrode table, by reading the fiducial list selected, by
    #  (1) Clear old Fiducial Table
    #  (2) If the selected fiducial list is not None Do
    #      (a) Read the fiducial list and
    #      (b) for each point pair create an Electrode object containing:
    #          name, target and entry coordinates and the flag
    #      (c) check simple error cases: (i) missing entry/target,
    #        (ii) more points than expected
    # NB: unselected points will not be parsed
    #######################################################################################

    def onfiducialCBox(self):
        # (1) CLEAR the list
        #self.clearTable()  # Eliminate the electrode list
        #slicer.util.showStatusMessage("HAI")# <-- This prints to the bottom of the left panel
        #print("WHYYYYYYYY???")              # <-- This prints to terminal if you started slicer from terminal, and also it shows up in "Log Messages" under the stream category

        # If they selected None, they probably don't want us to do anything. So we won't.
        if self.fiducialCBox.currentNode() is None:
            return
            
        # (2.a) Read the fiducial list
        operationLog = ""  # error/warning Log string
        self.fids = self.fiducialCBox.currentNode()

        # here we fill list using fiducials
        for i in xrange(self.fids.GetNumberOfFiducials()):
            if self.fids.GetNthFiducialSelected(i) == True:
                # Set up a 3DOF point
                P2 = [0.0, 0.0, 0.0]
                self.fids.GetNthFiducialPosition(i, P2)
                print(P2)
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                address_port = (self.addressBox.text, int(self.portBox.text))
                self.sock.connect(address_port)
                message='lego'+','+repr(P2[0])+','+repr(P2[1])+','+repr(P2[2])
                self.sock.sendall(message)
                self.commandFL.addRow(message, qt.QHBoxLayout())
                
                
                
        

#        horzGroupLayout = qt.QHBoxLayout()
#        horzGroupLayout.addWidget(self.startcommandPB)
#        horzGroupLayout.addWidget(self.createVTKModels)

#        self.commandFL.addRow("HO Ho hoe", qt.QHBoxLayout())
#        self.commandFL.addRow("", self.fiducialSplitBox)
#        self.commandFL.addRow("", self.splitFiducialPB)

        # connections
#        self.splitFiducialPB.connect('clicked(bool)', self.onsplitFiducialClick)
#        self.startcommandPB.connect('clicked(bool)', self.onstartcommandPB)

    #######################################################################################
    # on LegoWorkshop BUTTON
    #######################################################################################
    def ondeetoTB(self):
        """ on LegoWorkshop Tool Box Button Logic """


