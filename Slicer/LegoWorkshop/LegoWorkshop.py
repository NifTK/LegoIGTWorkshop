#########################################################################################
### Name convention: Gui Object should have suffix CB for Collapsible
### Button, TB toolbox button etc...
#########################################################################################
import struct
import os
from __main__ import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from numpy import *
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
        
        #Warning: These variables were measured with a caliper and aren't guaranteed to be accurate
        self.offset=33#mm
        self.height=130#mm
        
        self.calibrate()
        
    def calibrate(self):
        # Measurements of the smae points in the LEGO CT scan and on the LEGO Robot
        # For now, these are just the four corners of the top of the 
        #      Name          Azm,Elv,Dst,       X_CT         ,    Y_CT     ,       Z_CT
        # Front Left Corner ,-22,-27,148, -24.857597007947618,125.337890625,-164.55509249983300
        # Front Right Corner, 40,-32,136, -21.765711614238967,123.986328125,-284.10799438990176
        # Back Right Corner , 23,-20,211,-108.338502638081820,126.013671875,-287.19987978361040
        # Back Left Corner  ,-13,-20,218,-111.430388031790530,127.365234375,-167.64697789354165

        X=zeros((self.calibrationTable.rowCount,3))
        Slicer_CT_Calibration_Points=matrix(X)
        LEGO_Calibration_Points=Slicer_CT_Calibration_Points.copy()#Copy over to make sure we have a matrix of the same size
        
        # Do forward kinematics for each calibration point, getting x,y,z for each point in mm
        for i in xrange(self.calibrationTable.rowCount):
            LEGO_Calibration_Points[i]=self.fk(float(self.calibrationTable.item(i,0).text()),float(self.calibrationTable.item(i,1).text()),float(self.calibrationTable.item(i,2).text()))
            for j in xrange(3):
                Slicer_CT_Calibration_Points[i,j]=float(self.calibrationTable.item(i,3+j).text())
        
        # Find the transformation that matches them
        self.ret_R, self.ret_t = self.rigid_transform_3D(Slicer_CT_Calibration_Points, LEGO_Calibration_Points)

        Check_Calibration=False
        # If you want to make sure everything is shipshape, change Check_Calibration to true, and see if all the maths do what you expect
        if Check_Calibration:

            print("Calibration Points in LEGO Coordinates [mm]:")
            print(LEGO_Calibration_Points)
            print("")

            # First we do a bulk transform of all the calibration from the points into LEGO coordinates
            # Note that since we are not using homogeneous coordinates we have to tile the translation and tack it on
            n=Slicer_CT_Calibration_Points.shape[0]
            Projected_Slicer_CT_Calibration_Points = (self.ret_R*Slicer_CT_Calibration_Points.T) + tile(self.ret_t, (1, n))
            Projected_Slicer_CT_Calibration_Points = Projected_Slicer_CT_Calibration_Points.T

            print("Projected Slicer CT Calibration Points into LEGO Coordinates [mm]:")
            print(Projected_Slicer_CT_Calibration_Points)
            print("")

            C=Slicer_CT_Calibration_Points.copy()#Copy over to make sure we have a matrix of the same size (note that num_joints==num_dof)
            C[0]=self.ik(Projected_Slicer_CT_Calibration_Points[0,0],Projected_Slicer_CT_Calibration_Points[0,1],Projected_Slicer_CT_Calibration_Points[0,2])
            C[1]=self.ik(Projected_Slicer_CT_Calibration_Points[1,0],Projected_Slicer_CT_Calibration_Points[1,1],Projected_Slicer_CT_Calibration_Points[1,2])
            C[2]=self.ik(Projected_Slicer_CT_Calibration_Points[2,0],Projected_Slicer_CT_Calibration_Points[2,1],Projected_Slicer_CT_Calibration_Points[2,2])
            C[3]=self.ik(Projected_Slicer_CT_Calibration_Points[3,0],Projected_Slicer_CT_Calibration_Points[3,1],Projected_Slicer_CT_Calibration_Points[3,2])

            print("Inverse Kinematics (Batch Transform)")
            print(C)
            print("")

            D=Slicer_CT_Calibration_Points.copy()#Copy over to make sure we have a matrix of the same size (note that num_joints==num_dof)
            D[0]=self.ik_trans(Slicer_CT_Calibration_Points[0,0],Slicer_CT_Calibration_Points[0,1],Slicer_CT_Calibration_Points[0,2])
            D[1]=self.ik_trans(Slicer_CT_Calibration_Points[1,0],Slicer_CT_Calibration_Points[1,1],Slicer_CT_Calibration_Points[1,2])
            D[2]=self.ik_trans(Slicer_CT_Calibration_Points[2,0],Slicer_CT_Calibration_Points[2,1],Slicer_CT_Calibration_Points[2,2])
            D[3]=self.ik_trans(Slicer_CT_Calibration_Points[3,0],Slicer_CT_Calibration_Points[3,1],Slicer_CT_Calibration_Points[3,2])
            print("Inverse Kinematics (Individual Transform)")
            print(D)
            print("")

            # Find the error
            err = Projected_Slicer_CT_Calibration_Points - LEGO_Calibration_Points

            err = multiply(err, err)
            err = sum(err)
            rmse = math.sqrt(err/n);

            print("RMSE:", rmse)

    # Forward kinematics: For given joint angles figure out what X,Y,Z we have
    def fk(self,Dst,Azm,Elv):
        projected_length=Dst*math.cos(math.radians(Elv))
        effective_length=math.sqrt(projected_length*projected_length+self.offset*self.offset)
        azimuth_correction=math.atan2(self.offset,projected_length)
        azimuth_efective=math.radians(Azm)-azimuth_correction
        x=-effective_length*math.cos(azimuth_efective)
        y= effective_length*math.sin(azimuth_efective)
        z= Dst*math.sin(math.radians(Elv))+self.height
        return [x,y,z]

    # Inverse kinematics: For a given X,Y,Z figure out what joint angles we want
    def ik(self,x,y,z):
        azimuth_efective=math.atan2(y,-x)
        effective_length=math.sqrt(x*x+y*y)
        projected_length=math.sqrt(effective_length*effective_length-self.offset*self.offset)
        Dst=math.sqrt(projected_length*projected_length+(z-self.height)*(z-self.height))
        Elv_Rad=math.asin((z-self.height)/Dst)
        azimuth_correction=math.atan2(self.offset,projected_length)
        Azm_Rad=azimuth_efective+azimuth_correction
        return [Dst,math.degrees(Azm_Rad),math.degrees(Elv_Rad)]

    # Inverse kinematics with Transform: For a given X,Y,Z and rigid transform figure out what joint angles we want
    # This is a convenience function for when we get points sporatically. 
    # If you are dealing with a large batch of points, it's almost certainly faster to transform them all at once.
    def ik_trans(self,x,y,z):
        A=matrix([x, y, z])
        P2 = self.ret_R*A.T + self.ret_t
        return self.ik(P2[0],P2[1],P2[2])

    # Input: expects Nx3 matrix of points
    # Returns R,t
    # R = 3x3 rotation matrix
    # t = 3x1 column vector
    def rigid_transform_3D(self,A, B):
        assert len(A) == len(B)

        N = A.shape[0]; # total points

        centroid_A = mean(A, axis=0)
        centroid_B = mean(B, axis=0)
        
        # centre the points
        AA = A - tile(centroid_A, (N, 1))
        BB = B - tile(centroid_B, (N, 1))

        # dot is matrix multiplication for array
        H = transpose(AA) * BB

        U, S, Vt = linalg.svd(H)

        R = Vt.T * U.T

        # special reflection case
        if linalg.det(R) < 0:
           print("Reflection detected")
           Vt[2,:] *= -1
           R = Vt.T * U.T

        t = -R*centroid_A.T + centroid_B.T

        return R, t



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

        #### Buttons Layout
        self.deetoButtonsHBL = qt.QHBoxLayout()
#        self.deetoButtonsHBL.addWidget(self.deetoLE)
        self.addressBox = qt.QLineEdit("ev3dev.local");
        self.portBox = qt.QLineEdit("3148");
        self.deetoButtonsHBL.addWidget(self.addressBox)
        self.deetoButtonsHBL.addWidget(self.portBox)

        #### Aggiungo il bottone al layout
        self.setupFL.addRow("Server Location: ", self.deetoButtonsHBL)
        
        Slicer_CT_Calibration_Points=matrix('-24.857597007947618,125.337890625,-164.55509249983300;-21.765711614238967,123.986328125,-284.10799438990176;-108.338502638081820,126.013671875,-287.19987978361040;-111.430388031790530,127.365234375,-167.64697789354165')
        LEGO_Calibration_Joints=matrix([[148,-22,-27],[136, 40,-32],[211, 23,-20],[218,-13,-20]])
        self.calibrationTable=qt.QTableWidget(4, 6)
        self.calibrationTable.setHorizontalHeaderLabels(['Dst', 'Azm', 'Elv', 'X', 'Y', 'Z'])
        for row in range(0,4):
            for col in range(0,3):
                item1 = qt.QTableWidgetItem("%s"%Slicer_CT_Calibration_Points[row,col])
                self.calibrationTable.setItem(row, col+3, item1)
                item2 = qt.QTableWidgetItem("%s"%LEGO_Calibration_Joints[row,col])
                self.calibrationTable.setItem(row, col, item2)
        self.setupFL.addRow("Calibration: ", self.calibrationTable)
        
        
        self.CalibrateBtn = qt.QToolButton()
        self.CalibrateBtn.setText("Rerun Calibration")
        self.CalibrateBtn.toolTip = "Rerun Calibration with Points from Table"
        self.CalibrateBtn.enabled = True
        self.CalibrateBtn.connect('clicked(bool)', self.calibrate)
        self.setupFL.addRow("Calibrate: ", self.CalibrateBtn)

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
        
        
        self.buttonsHBL = qt.QHBoxLayout()
        #### Tool Box for changing deeto Executable
        self.deetoTB = qt.QToolButton()
        self.deetoTB.setText("Go")
        self.deetoTB.toolTip = "Send Command to LEGO Robot"
        self.deetoTB.enabled = True
        self.deetoTB.connect('clicked(bool)', self.ondeetoTB)
        
        self.updateListBtn = qt.QToolButton()
        self.updateListBtn.setText("Update")
        self.updateListBtn.toolTip = "Update Feducial List"
        self.updateListBtn.enabled = True
        self.updateListBtn.connect('clicked(bool)', self.onfiducialCBox)
        
        self.updateCalibrationPointsBtn = qt.QToolButton()
        self.updateCalibrationPointsBtn.setText("Replace Calibration Points")
        self.updateCalibrationPointsBtn.toolTip = "Replace Calibration Points with those checked"
        self.updateCalibrationPointsBtn.enabled = True
        self.updateCalibrationPointsBtn.connect('clicked(bool)', self.onupdateCalibrationPointsBtn)
        
        self.buttonsHBL.addWidget(self.deetoTB)
        self.buttonsHBL.addWidget(self.updateListBtn)
        self.buttonsHBL.addWidget(self.updateCalibrationPointsBtn)
        self.commandFL.addRow("Send Command", self.buttonsHBL)

        #### Configure command - Section
        ### Read from files the list of the modules
        #with open(slicer.modules.LegoWorkshopInstance.electrodeTypesPath) as data_file:
            # models is a dictionary with the name of electrode type is the key
        #    self.models = json.load(data_file)

        #### Create the caption table for the configuration
        self.tableCaption = ["Name", "Message", "", ""]
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
        self.FeducailsList = qt.QVBoxLayout()
        self.commandFL.addRow("Feducials", self.FeducailsList)
        
        self.horzGroupLayout=[]
        self.checkboxes=[]
        self.labels=[]

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
        
        for i in range(0,len(self.checkboxes)):
            self.checkboxes[i].setChecked(False)
            self.checkboxes[i].setEnabled(False)
            self.checkboxes[i].setText('')
            self.labels[i].setText('')
            
        self.messages=[]
        self.points=[]
        
        # here we fill list using fiducials
        for i in xrange(self.fids.GetNumberOfFiducials()):
            if self.fids.GetNthFiducialSelected(i) == True:
                # Set up a 3DOF point
                P2 = [0.0, 0.0, 0.0]
                self.fids.GetNthFiducialPosition(i, P2)
                #print(P2)
                self.points.append(P2)
                J2 = self.ik_trans(P2[0],P2[1],P2[2])
                #print(J2)
                message='lego'+','+repr(J2[0])+','+repr(J2[1])+','+repr(J2[2])
                
                self.messages.append(message)
                if len(self.labels)>i:
                    self.labels[i].setText(message)
                    self.checkboxes[i].setEnabled(True)
                    self.checkboxes[i].setText(self.fids.GetNthFiducialLabel(i))
                else:
                    self.horzGroupLayout.append(qt.QHBoxLayout())
                    self.checkboxes.append(qt.QCheckBox(self.fids.GetNthFiducialLabel(i)))
                    self.labels.append(qt.QLabel(message))
                self.horzGroupLayout[i].addWidget(self.checkboxes[i])
                self.horzGroupLayout[i].addWidget(self.labels[i])
                #horzGroupLayout.addWidget(self.createVTKModels)
                self.FeducailsList.addLayout(self.horzGroupLayout[i])
        

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
        for i in range(0,len(self.messages)):
            if self.checkboxes[i].isChecked():
                message=self.messages[i]
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                address_port = (self.addressBox.text, int(self.portBox.text))
                self.sock.connect(address_port)
                self.sock.sendall(message)
    
    def onupdateCalibrationPointsBtn(self):
        """ on LegoWorkshop Tool Box Button Logic """
        rows = 0
        self.calibrationTable.setRowCount(rows)
        for i in range(0,len(self.points)):
            if self.checkboxes[i].isChecked():
                rows=rows+1
                self.calibrationTable.setRowCount(rows)
                for col in range(0,3):
                    item1 = qt.QTableWidgetItem("%s"%self.points[i][col])
                    self.calibrationTable.setItem(rows-1, col+3, item1)



