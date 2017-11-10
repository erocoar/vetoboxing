# -*- coding: utf-8 -*-
"""
Created on Thu Oct 19 00:55:58 2017

@author: Frederik
"""
import sys
import os
import json
import errno
import time
import numpy as np
import random
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5 import QtCore, QtWidgets, QtGui

_DOCK_OPTS = QtWidgets.QMainWindow.AnimatedDocks | QtWidgets.QMainWindow.AllowNestedDocks | QtWidgets.QMainWindow.AllowTabbedDocks

class MainWindow(QtWidgets.QMainWindow):
    """
    Main Window
    """
    def __init__(self, parent = None):
        super(MainWindow, self).__init__()
        self.__setupDockWidgets__()
        self.__setupMenu__()
        self.__initFuns__()
        self.__setupToolbar__()
        
        self.setDockOptions(_DOCK_OPTS)
                
    def __setupToolbar__(self):
        """
        Logo Label Widget
        """
        vb_label = QtWidgets.QLabel()
        vb_label.setPixmap(QtGui.QPixmap("./assets/vetoboxingLogoSmall.png"))
        
        """
        Setup the toolbars of the mainwindow toolbar
        """       
        self.toolbar_fileHandling = self.addToolBar("")
        self.toolbar_fileHandling.setOrientation(QtCore.Qt.Horizontal)
        self.toolbar_fileHandling.setMovable(True)
        self.toolbar_fileHandling.setIconSize(QtCore.QSize(25, 25))
        
        self.toolbar_runSim = self.addToolBar("")
        self.toolbar_runSim.setOrientation(QtCore.Qt.Horizontal)
        self.toolbar_runSim.setMovable(True)
        self.toolbar_runSim.setIconSize(QtCore.QSize(25, 25))
        
        self.toolbar_dockWindows = self.addToolBar("")
        self.toolbar_dockWindows.setOrientation(QtCore.Qt.Horizontal)
        self.toolbar_dockWindows.setMovable(True)
        self.toolbar_dockWindows.setIconSize(QtCore.QSize(25, 25))
                
        self.toolbar_clear = self.addToolBar("")
        self.toolbar_clear.setOrientation(QtCore.Qt.Horizontal)
        self.toolbar_clear.setMovable(True)
        self.toolbar_clear.setIconSize(QtCore.QSize(25, 25))
        
        self.toolbar_logo = self.addToolBar("")
        self.toolbar_logo.setMovable(False)
      
        """
        Mainwindow toolbar actions
        """
        loadAction = QtWidgets.QAction(QtGui.QIcon("./assets/iconOpenFolder.png"), "Import Data", self)
        loadAction.setShortcut("Ctrl+O")
        loadAction.triggered.connect(self.load)
        
        saveAction = QtWidgets.QAction(QtGui.QIcon("./assets/iconSave.png"), "Save Data", self)
        saveAction.setShortcut("Ctrl+S")
        saveAction.triggered.connect(self.save)
        
        saveAllAction = QtWidgets.QAction(QtGui.QIcon("./assets/iconSaveAll.png"), "Save All", self)
        
        runAction = QtWidgets.QAction(QtGui.QIcon("./assets/iconRun.png"), "Run", self)
        runAction.triggered.connect(self.runSimulation)
        
        runAllAction = QtWidgets.QAction(QtGui.QIcon("./assets/iconRunAll.png"), "Run All", self)
        
        runLastAction = QtWidgets.QAction(QtGui.QIcon("./assets/iconRunLast.png"), "Repeat Last Run", self)

        settingsAction = QtWidgets.QAction(QtGui.QIcon("./assets/iconSettings.png"), "Settings", self)
        settingsAction.triggered.connect(self.showPreferences)
        
        manifestoAction = QtWidgets.QAction(QtGui.QIcon("./assets/iconManifesto.png"), "Manifesto", self)
        manifestoAction.triggered.connect(self.showManifesto)
        
        clearAction = QtWidgets.QAction(QtGui.QIcon("./assets/iconClear.png"), "Clear All", self)
        clearAction.setShortcut("Ctrl+C")
        clearAction.triggered.connect(self.readValues)
        
        stretcher = QtWidgets.QWidget()
        stretcher.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        
        """
        add actions to toolbar
        """
        self.toolbar_fileHandling.addActions([loadAction, saveAction, saveAllAction])
        
        self.toolbar_runSim.addActions([runAction, runAllAction, runLastAction])
        
        self.toolbar_dockWindows.addActions([settingsAction, manifestoAction])
        
        self.toolbar_clear.addAction(clearAction)
        
        self.toolbar_logo.addWidget(stretcher)
        self.toolbar_logo.addWidget(vb_label)
        
    def load(self):
        file = QtWidgets.QFileDialog.getOpenFileName(filter = "Text Files (*.txt)")
        
        if file[0]: 
            try:
                with open(file[0]) as sequence:
                    seq = json.load(sequence)
            except:
                raise    
        else:
            return
                
        if "voters" and "statusquo" in seq or "sequence" in seq:
            self.voterWidget.loadTable(seq)
        
        if "visualizationSettings" in seq:
            self.optionsWidget.__loadOptions__(seq["visualizationSettings"])
        
    def save(self):
        file = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory"))
        
        runOptions = self.voterWidget.tabWidget.currentWidget().__saveOptions__()
        otherOptions = self.optionsWidget.__saveOptions__()
        tables = self.voterWidget.tabWidget.currentWidget().__saveTable__()
        
        out = dict(**runOptions, **otherOptions, **tables)
        
        with open(os.path.join(file, "save.txt"), "w") as outfile:
            json.dump(out, outfile)
        
        
    def showPreferences(self):
        if self.preferencesDock.isVisible():
            return
        
        if not self.preferencesDock.isWindow():
            self.preferencesDock.setFloating(True)
        
        self.preferencesDock.setGeometry(QtCore.QRect(100, 100, 400, 400))
        self.preferencesDock.show()
        
    def showManifesto(self):
        if self.manifestoDock.isVisible():
            return
        
        if not self.manifestoDock.isWindow():
            self.manifestoDock.setFloating(True)
            
        self.manifestoDock.show()
    
    def __setupMenu__(self):
        """
        Menu Bar
        """
        menu = self.menuBar()
        menu.addMenu("&Help")
        menu.addMenu("&About")
        
    def __setupDockWidgets__(self):      
        self.setWindowTitle("Vetoboxing")
        self.resize(1000, 1000)
                
        manifestoWidget = ManifestoPyDockWidget(self)
        self.manifestoDock = QtWidgets.QDockWidget()
        self.manifestoDock.setWidget(manifestoWidget)
        self.manifestoDock.setWindowTitle("Manifesto API")
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.manifestoDock)
        
        self.optionsWidget = OptionsWidget()       
        self.preferencesDock = QtWidgets.QDockWidget()
        self.preferencesDock.setWidget(self.optionsWidget)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.preferencesDock)
        
        self.preferencesDock.setGeometry(QtCore.QRect(100, 100, 400, 400))
        self.preferencesDock.setWindowTitle("Settings")
        self.preferencesDock.setWindowIcon(QtGui.QIcon("./assets/iconSettings.png"))
        self.preferencesDock.setFloating(True)
        self.preferencesDock.hide()
        
        self.logWidget = LogDockWidget(self)
        self.logDock = QtWidgets.QDockWidget()
        self.logDock.setWindowTitle("Log")
        self.logDock.setWidget(self.logWidget)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.logDock)
        self.logWidget.append("test")
        
        self.visualizeWidget = VisualizeDockWidget(self)
        self.visualizeDock = QtWidgets.QDockWidget()
        self.visualizeDock.setWindowTitle("Plots")
        self.visualizeDock.setWidget(self.visualizeWidget)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.visualizeDock)
        
        
#        self.animationViewer = AnimationDrawer(r"C:\Users\Frederik\Dropbox\SluggishConstitutionalism\Project5_VetoBoxingProject\vbsim\gui_v2\RESULTS\results-3-2-20__2017-11-08_1204\animation.gif")
#        self.visualizationDock = QtWidgets.QDockWidget()
#        self.visualizationDock.setWindowTitle("Plot")
#        self.visualizationDock.setWidget(self.animationViewer)
#        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.visualizationDock)

        self.voterWidget = VoterSetup(self, initDim = self.optionsWidget.runOptions.spinBox_dimensions.value())
        self.setCentralWidget(self.voterWidget)

#        self.voterWidget.tabWidget.currentChanged.connect(self.voterWidget.__addTab__)
        self.voterWidget.tabWidget.currentChanged.connect(self.__tabWidget_ChangedConnect__)
        
    def __initFuns__(self):
        """
        On-change Functions that continuously pass changes in run options to the respective Game Table's option class
        """
        self.optionsWidget.runOptions.spinBox_dimensions.valueChanged.connect(lambda: 
            self.voterWidget.tabWidget.currentWidget().__changeDim__(self.optionsWidget.runOptions.spinBox_dimensions.value()))
        
        self.optionsWidget.runOptions.spinBox_runs.valueChanged.connect(lambda: 
            self.updateGameTableOptions("runs", self.optionsWidget.runOptions.spinBox_runs.value()))
            
        self.optionsWidget.runOptions.spinBox_dimensions.valueChanged.connect(lambda: 
            self.updateGameTableOptions("dimensions", self.optionsWidget.runOptions.spinBox_dimensions.value()))
            
        self.optionsWidget.runOptions.doubleSpinBox_breaks.valueChanged.connect(lambda: 
            self.updateGameTableOptions("breaks", self.optionsWidget.runOptions.doubleSpinBox_breaks.value()))
            
        self.optionsWidget.runOptions.buttonGroup_method.buttonToggled.connect(lambda:
            self.updateGameTableOptions("method", self.optionsWidget.runOptions.buttonGroup_method.checkedButton().text().lower()))
        
        self.optionsWidget.runOptions.buttonGroup_save.buttonToggled.connect(lambda: 
            self.updateGameTableOptions("save", self.optionsWidget.runOptions.buttonGroup_save.checkedButton().text().lower()))
            
        self.optionsWidget.runOptions.buttonGroup_visualize.buttonToggled.connect(lambda: 
            self.updateGameTableOptions("visualize", self.optionsWidget.runOptions.buttonGroup_visualize.checkedButton().text().lower()))
            
        self.optionsWidget.runOptions.buttonGroup_alterPreferences.buttonToggled.connect(lambda: 
            self.updateGameTableOptions("alterPreferences", self.optionsWidget.runOptions.buttonGroup_alterPreferences.checkedButton().text().lower()))
            
        self.optionsWidget.runOptions.buttonGroup_alterStatusQuo.buttonToggled.connect(lambda: 
            self.updateGameTableOptions("alterStatusQuo", self.optionsWidget.runOptions.buttonGroup_alterStatusQuo.checkedButton().text().lower()))
            
        self.optionsWidget.runOptions.buttonGroup_distanceType.buttonToggled.connect(lambda: 
            self.updateGameTableOptions("distanceType", self.optionsWidget.runOptions.buttonGroup_distanceType.checkedButton().text().lower()))
            
        self.optionsWidget.runOptions.buttonGroup_distribution.buttonToggled.connect(lambda: 
            self.updateGameTableOptions("distribution", self.optionsWidget.runOptions.buttonGroup_distribution.checkedButton().text().lower()))
            
    def updateGameTableOptions(self, option, value):
        if option == "runs":
            self.voterWidget.tabWidget.currentWidget().options.runs = value

        elif option == "dimensions":
            self.voterWidget.tabWidget.currentWidget().options.dimensions = value
            
        elif option == "breaks":
            self.voterWidget.tabWidget.currentWidget().options.breaks = value
            
        elif option == "method":
            self.voterWidget.tabWidget.currentWidget().options.method = value
            
        elif option == "save":
            self.voterWidget.tabWidget.currentWidget().options.save = value
            
        elif option == "visualize":
            self.voterWidget.tabWidget.currentWidget().options.visualize = value
            
        elif option == "alterPreferences":
            self.voterWidget.tabWidget.currentWidget().options.alterPreferences = value
            
        elif option == "alterStatusQuo":
            self.voterWidget.tabWidget.currentWidget().options.alterStatusQuo = value
            
        elif option == "distanceType":
            self.voterWidget.tabWidget.currentWidget().options.distanceType = value
            
        elif option == "distribution":
            self.voterWidget.tabWidget.currentWidget().options.distribution = value
            
    def __tabWidget_ChangedConnect__(self, index):
        self.voterWidget.__addTab__(index)
        self.optionsWidget.__setRunOptions__(self.voterWidget.tabWidget.currentWidget().options)
        
    def runSimulation(self):
        var = self.readValues()
        
        import vb_sim_v2 as vb
        
        sim = vb.Simulation(var, self)
        sim.simulation()
        
    def readValues(self):
        """
        Convert tables to arrays and transfer arrays + settings to 
        var.py for sim to read
        """
        print("connected")
        votercount = self.voterWidget.tabWidget.currentWidget().voterTable.rowCount()
        dimensions = self.voterWidget.tabWidget.currentWidget().options.dimensions
        
        method = self.voterWidget.tabWidget.currentWidget().options.method
        
        runs = self.voterWidget.tabWidget.currentWidget().options.runs
        breaks = self.voterWidget.tabWidget.currentWidget().options.breaks
        save = self.voterWidget.tabWidget.currentWidget().options.save
        visualize = self.voterWidget.tabWidget.currentWidget().options.visualize
        alterPreferences = self.voterWidget.tabWidget.currentWidget().options.alterPreferences
        alterStatusQuo = self.voterWidget.tabWidget.currentWidget().options.alterStatusQuo
        distanceType = self.voterWidget.tabWidget.currentWidget().options.distanceType
        distribution = self.voterWidget.tabWidget.currentWidget().options.distribution

        statusQuoPosition, statusQuoDrift, voterNames, voterRoles, voterPositions,\
        randomAgendaSetter, randomVetoPlayer = self.voterWidget.tabWidget.currentWidget().returnInitArrays()
        
        customRoleArray = self.voterWidget.tabWidget.currentWidget().customRoleArray

        directory = None
        
        if save or visualize:            
            modelNumber = self.setModelNumber(alterStatusQuo, alterPreferences)
            
            if directory is None:
                parentDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'RESULTS')
                self.createDir(parentDir)
                resultsDir = self.resultsDir(modelNumber, dimensions, runs, parentDir)
                directory = resultsDir
        
        
        return SimulationVariables(votercount = votercount, runs = runs, breaks = breaks, dimensions = dimensions, save = save, visualize = visualize,
                                   alterPreferences = alterPreferences, alterStatusQuo = alterStatusQuo, distanceType = distanceType, distribution = distribution,
                                   directory = directory, statusQuoPosition = statusQuoPosition, statusQuoDrift = statusQuoDrift, voterNames = voterNames,
                                   voterRoles = voterRoles, voterPositions = voterPositions, randomAgendaSetter = randomAgendaSetter, 
                                   randomVetoPlayer = randomVetoPlayer, method = method, customRoleArray = customRoleArray)
        
        
    def setModelNumber(self, alterStatusQuo, alterPreferences):    
        """
        Set the model number of the simulation for classifying the model in the csv
        """
        if alterStatusQuo == 'no':
            return 0

        elif alterStatusQuo == 'random':
            return 1
        
        elif alterStatusQuo == 'history':
            return 2
        
        elif alterStatusQuo == 'history+drift' and alterPreferences == 'no':
            return 3
        
        elif alterStatusQuo == 'history + drift' and alterPreferences == 'drift':
            return 4
        
        else:
            return 'NA'
        
    def createDir(self, directory):
        """
        Create directory
        """
        try:
            os.makedirs(directory)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
                
    def resultsDir(self, modelNumber, dimensions, runs, parentDir):
        """
        Create a directory for the simulation results
        """
        timestr = time.strftime("%Y-%m-%d_%H%M")
    
        foldername = ''.join(('results', '-', str(modelNumber), '-', str(dimensions), '-', str(runs), '__', timestr))

        resultsDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), parentDir, foldername)
        self.createDir(resultsDir)
        return resultsDir
    

class VoterSetup(QtWidgets.QWidget):
    """
    Tab Widget for Voter Position / Drift /  Role Tables
    """
    def __init__(self, parent, initDim):
        super(VoterSetup, self).__init__(parent)
        self.fromLoadAdd = False
        self.setRandomAgendaSetter = False
        self.setRandomVetoPlayer = False
        
        self.initDim = initDim
        self.__setupTabWidget__()
        self.__setupToolbar__()

        self.__layout__()
        
    def __setupToolbar__(self):
        self.toolbar = QtWidgets.QToolBar()
        self.toolbar.setIconSize(QtCore.QSize(14, 14))
        
        stretcher = QtWidgets.QWidget()
        stretcher.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        
        clearAction = QtWidgets.QAction(QtGui.QIcon("./assets/iconClear.png"), "Remove Voter", self)
        clearAction.setShortcut("Ctrl+X")
        clearAction.triggered.connect(self.__delVoterTableRow__)
        
        addAction = QtWidgets.QAction(QtGui.QIcon("./assets/iconAdd.png"), "Add Voter", self)
        addAction.setShortcut("Ctrl+A")
        addAction.triggered.connect(self.__addVoterTableRow__)
        
        randomizeAction = QtWidgets.QAction(QtGui.QIcon("./assets/iconRandom.png"), "Random Roles", self)
        randomizeAction.setShortcut("Ctrl+R")
        randomizeAction.triggered.connect(self.__randomRoles__)
        
        self.randomVetoSpinBox = QtWidgets.QSpinBox()
        self.randomVetoSpinBox.setToolTip("Number of Veto Players")
        
        self.randomVetoAction = QtWidgets.QAction(QtGui.QIcon("./assets/iconVeto.png"), "Select Random Veto Player(s)", self)
        self.randomVetoAction.triggered.connect(lambda: self.__setRandomPlayerStates__("vetoplayer"))
                          
        self.randomAgendaSetterAction = QtWidgets.QAction(QtGui.QIcon("./assets/iconAS"), "Select Random Agenda Setter", self)
        self.randomAgendaSetterAction.triggered.connect(lambda: self.__setRandomPlayerStates__("agendasetter"))
        
        self.toolbar.addAction(addAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(clearAction)
        
        self.toolbar.addWidget(stretcher)
        
        self.toolbar.addWidget(self.randomVetoSpinBox)
        self.toolbar.addAction(self.randomVetoAction)
        self.toolbar.addAction(self.randomAgendaSetterAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(randomizeAction)
        
    def __setRandomPlayerStates__(self, player):
        if player == "agendasetter":
            if self.setRandomAgendaSetter is False:
                self.setRandomAgendaSetter = True
                self.randomAgendaSetterAction.setIcon(QtGui.QIcon("./assets/iconASTriggered.png"))
            else:
                self.setRandomAgendaSetter = False
                self.randomAgendaSetterAction.setIcon(QtGui.QIcon("./assets/iconAS.png"))                       
        else:
            if self.setRandomVetoPlayer is False:
                self.setRandomVetoPlayer = True
                self.randomVetoAction.setIcon(QtGui.QIcon("./assets/iconVetoTriggered.png"))
            else:
                self.setRandomVetoPlayer = False
                self.randomVetoAction.setIcon(QtGui.QIcon("./assets/iconVeto.png"))
            
    def __randomRoles__(self):
        if self.setRandomAgendaSetter:
            """clear row first"""
            [self.tabWidget.currentWidget().voterTable.setItem(row, 1, None) 
            for row in range(self.tabWidget.currentWidget().voterTable.rowCount())]
            
            """select rnd index"""
            randomAgendaSetter = random.choice(range(self.tabWidget.currentWidget().voterTable.rowCount()))
            self.tabWidget.currentWidget().voterTable.setItem(randomAgendaSetter, 1, QtWidgets.QTableWidgetItem("True"))
        
        if self.setRandomVetoPlayer:
            """clear row"""
            [self.tabWidget.currentWidget().voterTable.setItem(row, 2, None)
            for row in range(self.tabWidget.currentWidget().voterTable.rowCount())]

            """select rnd indexes"""
            if self.setRandomAgendaSetter:
                randomVetoPlayerSample = [i for i in range(self.tabWidget.currentWidget().voterTable.rowCount()) if i != randomAgendaSetter]
            else:
                randomVetoPlayerSample = [i for i in range(self.tabWidget.currentWidget().voterTable.rowCount())]
                
            randomVetoPlayers = random.sample(randomVetoPlayerSample, self.randomVetoSpinBox.value())
            [self.tabWidget.currentWidget().voterTable.setItem(row, 2, QtWidgets.QTableWidgetItem("True")) for row in randomVetoPlayers]
        
        """fill remainder with false"""
        for col in [index for index in [1 * self.setRandomAgendaSetter, 2 * self.setRandomVetoPlayer] if index != 0]:
            for row in range(self.tabWidget.currentWidget().voterTable.rowCount()):
                if self.tabWidget.currentWidget().voterTable.item(row, col) is None:
                    self.tabWidget.currentWidget().voterTable.setItem(row, col, QtWidgets.QTableWidgetItem("False"))
                    
    def __addVoterTableRow__(self):
        self.tabWidget.currentWidget().voterTable.addRow()

    def __delVoterTableRow__(self):
        self.tabWidget.currentWidget().voterTable.delRow()
        
    def __setupTabWidget__(self):
        self.tabWidget = QtWidgets.QTabWidget()
        self.tabbar = EditableTabBar(self)
        self.tabbar.setSelectionBehaviorOnRemove(QtWidgets.QTabBar.SelectLeftTab)

        self.tabWidget.setTabBar(self.tabbar)
        self.tabWidget.setTabPosition(0)
        
        self.__setupTables__()
        
        self.tabWidget.addTab(QtWidgets.QWidget(), "+" )
        self.tabWidget.setUpdatesEnabled(True)
        
        self.tabWidget.setTabsClosable(True)
        self.tabbar.tabButton(self.tabWidget.count() - 1, QtWidgets.QTabBar.RightSide).resize(0, 0)
        self.tabWidget.tabCloseRequested.connect(self.__removeTab__)

    def __addTab__(self, index):
        if index == self.tabWidget.count() - 1 and not self.fromLoadAdd:    
            """last tab was clicked. add tab"""
            self.tabWidget.insertTab(index, GameTable(self), "Sim {0}".format(index + 1))
            self.tabWidget.setCurrentIndex(index)
        else:
            return
            
    def __removeTab__(self, index):
        widget = self.tabWidget.widget(index)
        
        if widget is not None:
            widget.deleteLater()

        self.tabWidget.removeTab(index)
        
    def __layout__(self):
        self.layout = QtWidgets.QVBoxLayout()
        
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.tabWidget)
        
        self.setLayout(self.layout)
        
    def __setupTables__(self):       
        for i in range(3):
            self.tabWidget.addTab(GameTable(self, 2), "Test")
        
    def loadTable(self, seq):
        if "sequence" in seq:
            self.tabWidget.currentWidget().customRoleArray = seq["sequence"]
            
        else:
            self.fromLoadAdd = True
            self.tabWidget.insertTab(self.tabWidget.count() - 1, GameTable(self, fromLoad = True, file = seq), "Test2")
            self.tabWidget.setCurrentIndex(self.tabWidget.count() - 2)
            self.fromLoadAdd  = False
            
        
class GameTable(QtWidgets.QWidget):
    def __init__(self, parent, dimInit = 2, fromLoad = False, file = None):
        super(GameTable, self).__init__(parent)
                
        self.options = GameTableOptions()
        self.customRoleArray = None
        
        if not fromLoad:
            self.__setup__(dimInit)
            self.__layout__()
            
        else:
            self.__loadTable__(file)
            self.__layout__()
                 
    def __setup__(self, dimInit):
        self.voterTable = TableWidget()
        self.voterTable.setColumnCount(3 + dimInit)
        self.voterTable.setRowCount(3)
        self.voterTable.setHorizontalHeaderLabels(["Name", "Agenda Setter", "Veto Player"] + 
                                                  ["Dim" + str(dim + 1) for dim in range(dimInit)])
        
        self.statusQuoTable = TableWidget()
        self.statusQuoTable.setColumnCount(dimInit)
        self.statusQuoTable.setRowCount(2)
        self.statusQuoTable.setHorizontalHeaderLabels(["Dim" + str(dim + 1) for dim in range(dimInit)])        

    def __layout__(self):
        splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        splitter.addWidget(self.voterTable)
        splitter.addWidget(self.statusQuoTable)
        splitter.setStretchFactor(0, 10)
        splitter.setStretchFactor(1, 3)
        
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(splitter)
        self.setLayout(layout)
        
    def __changeDim__(self, dimValue):
        self.voterTable.setColumnCount(3 + dimValue)
        self.voterTable.setHorizontalHeaderLabels(["Name", "Agenda Setter", "Veto Player"] + 
                                         ["Dim " + str(dim + 1) for dim in range(dimValue)])
        
        self.statusQuoTable.setColumnCount(dimValue)
        self.statusQuoTable.setHorizontalHeaderLabels(["Dim" + str(dim + 1) for dim in range(dimValue)])
    
    def __saveOptions__(self):
        save = {
                "runSettings": {
                        "alterPreferences" : self.options.alterPreferences,
                        "alterStatusQuo" : self.options.alterStatusQuo,
                        "breaks" : self.options.breaks,
                        "dimensions" : self.options.dimensions,
                        "distanceType" : self.options.distanceType,
                        "distribution" : self.options.distribution,
                        "runs" : self.options.runs,
                        "save" : self.options.save,
                        "visualize" : self.options.visualize
                        }
                }
        
        return save
        
    def __saveTable__(self):
        """
        Save voter and SQ setup
        """
        save = {
                "voters" : {
                        "votercount" : self.voterTable.rowCount(),
                        "names" : [self.voterTable.item(row, 0).text() for
                                   row in range(self.voterTable.rowCount())],
                        "agendasetter" : [self.voterTable.item(row, 1).text() for 
                                          row in range(self.voterTable.rowCount())],
                        "vetoplayer" : [self.voterTable.item(row, 2).text() for 
                                        row in range(self.voterTable.rowCount())],
                        "positions" : [[self.voterTable.item(row, dim + 3).text() for 
                                        dim in range(self.voterTable.columnCount() - 3)] 
                        for row in range(self.voterTable.rowCount())]
#                        "drift" : [[self.voterTable.item(row, dim).text() for 
#                                    dim in range(dimensions)] for row in range(voterCount)]
                        },
                "statusquo" : {
                        "position" : [self.statusQuoTable.item(0, dim).text() for
                              dim in range(self.statusQuoTable.columnCount())],
                        "drift" : [self.statusQuoTable.item(1, dim).text() for
                                  dim in range(self.statusQuoTable.columnCount())]
                        }
                }
                
        return save
                
    def __loadTable__(self, sequence):
        """
        Load voter and SQ table data
        """
        seq = sequence
        try:
            """Setup"""
            self.voterTable = TableWidget()
            self.voterTable.setRowCount(seq["voters"]["votercount"])
            self.voterTable.setColumnCount(len(seq["voters"]["positions"][0]) + 3)
            
            self.voterTable.setHorizontalHeaderLabels(["Name", "Agenda Setter", "Veto Player"] + 
                                                      ["Dim" + str(dim + 1) for dim in 
                                                       range(len(seq["voters"]["positions"][0]))])
            
            self.statusQuoTable = TableWidget()
            self.statusQuoTable.setColumnCount(len(seq["statusquo"]["position"]))
            self.statusQuoTable.setRowCount(2)
            self.statusQuoTable.setHorizontalHeaderLabels(["Dim" + str(dim + 1) for dim in 
                                                           range(len(seq["statusquo"]["position"]))]) 
            
            """Names"""
            if "names" in seq["voters"]:
                [self.voterTable.setItem(row, 0, QtWidgets.QTableWidgetItem(item))
                for row, item in zip(range(self.voterTable.rowCount()), seq["voters"]["names"])]
            
            else:
                [self.voterTable.setItem(i, 0, QtWidgets.QTableWidgetItem("Voter " + str(i + 1)))
                for i in range(self.voterTable.rowCount())]
                
            """Agenda Setter"""
            if seq["voters"]["agendasetter"] == "random":
                [self.voterTable.setItem(row, 1, QtWidgets.QTableWidgetItem("random"))
                for row in range(self.voterTable.rowCount())]
                
            else:
                [self.voterTable.setItem(row, 1, QtWidgets.QTableWidgetItem(item))
                for row, item in zip(range(self.voterTable.rowCount()), seq["voters"]["agendasetter"])]
                
            """Veto Player"""
            if seq["voters"]["vetoplayer"] == "random":
                [self.voterTable.setItem(row, 2, QtWidgets.QTableWidgetItem("random"))
                for row in range(self.voterTable.rowCount())]
                
            else:
                [self.voterTable.setItem(row, 2, QtWidgets.QTableWidgetItem(item))
                for row, item in zip(range(self.voterTable.rowCount()), seq["voters"]["agendasetter"])]
                
            """Positions"""
            if "positions" in seq["voters"]:
                for row, item in zip(range(self.voterTable.rowCount()), seq["voters"]["positions"]):
                    for col, it in enumerate(item):
                        self.voterTable.setItem(row, col + 3, QtWidgets.QTableWidgetItem(str(it)))
                        
            """Status Quo"""
            [[self.statusQuoTable.setItem(row, col, QtWidgets.QTableWidgetItem(str(it)))
            for col, it in enumerate(item)] for row, item in zip(range(self.statusQuoTable.rowCount()),
                                     [seq["statusquo"]["position"], seq["statusquo"]["drift"]])]

        except:
            raise
            
    def toBool(self, item):
        if str(item.lower()) == "true" or str(item) == "1":
            return True
        else:
            return
            
    def returnInitArrays(self):
        statusQuoPosition = np.array([[float(self.statusQuoTable.item(0, dim).text()) for dim in range(self.statusQuoTable.columnCount())]])
        statusQuoDrift = np.array([[float(self.statusQuoTable.item(1, dim).text()) for dim in range(self.statusQuoTable.columnCount())]])

        voterNames = [self.voterTable.item(row, 0).text() for row in range(self.voterTable.rowCount())]
        
        randomAgendaSetter = False
        randomVetoPlayer = False
        
        if "random" in self.voterTable.item(0, 1).text() and not "random" in self.voterTable.item(0, 2).text():
            randomAgendaSetter = True
            voterRoles = [0 if not self.toBool(self.voterTable.item(row, 2).text()) else 1 for row in range(self.voterTable.rowCount())]

        elif "random" in self.voterTable.item(0, 2).text() and not "random" in self.voterTable.item(0, 1).text():
            randomVetoPlayer = True
            voterRoles = [0 if not self.toBool(self.voterTable.item(row, 1).text()) else 2 for row in range(self.voterTable.rowCount())]
            
        elif "random" in self.voterTable.item(0, 1).text() and "random" in self.voterTable.item(0, 2).text():
            randomAgendaSetter = True
            randomVetoPlayer = True
            voterRoles = None
            
        else:
            voterRoles = [0 if not self.toBool(self.voterTable.item(row, 1).text()) and not self.toBool(self.voterTable.item(row, 2).text())
            else 2 if self.toBool(self.voterTable.item(row, 1).text()) else 1 for row in range(self.voterTable.rowCount())]

        voterPositions = [[float(self.voterTable.item(row, col + 3).text()) for col in range(self.voterTable.columnCount() - 3)]
        for row in range(self.voterTable.rowCount())]
        
        return statusQuoPosition, statusQuoDrift, voterNames, voterRoles, voterPositions, randomAgendaSetter, randomVetoPlayer


class GameTableOptions:
    def __init__(self):        
        self.runs = 1
        self.dimensions = 2
        self.breaks = 0.01
        self.method = "grid"
        self.save = "yes"
        self.visualize = "yes"
        self.alterPreferences = "no"
        self.alterStatusQuo = "history+drift"
        self.distanceType = "euclidean"
        self.distribution = "uniform"
        
        
class OptionsWidget(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.__setup__()
        self.__layout__()

    def __setup__(self):
        self.listWidget_selection = QtWidgets.QListWidget()
        self.listWidget_selection.addItems(["General", "Run", "Visualization", "Advanced"])
        #TODO set current index here

        self.generalOptions = GeneralOptions()
        self.runOptions = RunOptions()
        self.visualizationOptions = VisualizeOptions()
        self.advancedOptions = AdvancedOptions()

        self.optionsIndex = [self.generalOptions, self.runOptions, self.visualizationOptions, self.advancedOptions]

        self.listWidget_selection.currentItemChanged.connect(self.__setIndex__)

    def __layout__(self):
        hbox = QtWidgets.QHBoxLayout()
        
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter.addWidget(self.listWidget_selection)
        
        splitter.addWidget(self.generalOptions)
        splitter.addWidget(self.runOptions)
        splitter.addWidget(self.visualizationOptions)
        splitter.addWidget(self.advancedOptions)
        
        self.generalOptions.hide()
        self.visualizationOptions.hide()
        self.advancedOptions.hide()
        self.runOptions.hide()
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        
        hbox.addWidget(splitter)
        self.setLayout(hbox)
        
    def __setIndex__(self, current, previous):
        """
        List Widget Click Indexing
        """
        ind_old = self.listWidget_selection.indexFromItem(previous).row()
        ind_new = self.listWidget_selection.indexFromItem(current).row()
       
        self.optionsIndex[ind_old].hide()
        self.optionsIndex[ind_new].show()
        
    def __setRunOptions__(self, GameTableOptions):
        """
        Set Run Options for specific GameTable Widget every time tab changes
        """
        self.runOptions.spinBox_runs.setValue(GameTableOptions.runs)
        self.runOptions.spinBox_dimensions.setValue(GameTableOptions.dimensions)
        self.runOptions.doubleSpinBox_breaks.setValue(GameTableOptions.breaks)
        
        """method"""
        if GameTableOptions.method == "grid":
            self.runOptions.radioButton_pointGrid.setChecked(True)
        else:
            self.runOptions.radioButton_optimization.setChecked(True)
        
        """save"""
        if GameTableOptions.save == "yes":
            self.runOptions.radioButton_save_yes.setChecked(True)
        else:
            self.runOptions.radioButton_save_no.setChecked(True)
            
        """visualize"""
        if GameTableOptions.visualize == "yes":
            self.runOptions.radioButton_visualize_yes.setChecked(True)
        else:
            self.runOptions.radioButton_visualize_no.setChecked(True)
            
        """alter Preferences"""
        if GameTableOptions.alterPreferences == "drift":
            self.runOptions.radioButton_alterPreferences_drift.setChecked(True)
            
        else:
            self.runOptions.radioButton_alterPreferences_no.setChecked(True)
           
        """alter Status Quo"""
        if GameTableOptions.alterStatusQuo == "history+drift":
            self.runOptions.radioButton_alterStatusQuo_historyAndDrift.setChecked(True)
            
        elif GameTableOptions.alterStatusQuo == "history":
            self.runOptions.radioButton_alterStatusQuo_history.setChecked(True)
            
        elif GameTableOptions.alterStatusQuo == "random":
            self.runOptions.radioButton_alterStatusQuo_random.setChecked(True)
            
        else:
            self.runOptions.radioButton_alterStatusQuo_no.setChecked(True)
        
        """distance Type"""
        if GameTableOptions.distanceType == "euclidean":
            self.runOptions.radioButton_distanceEuclidean.setChecked(True)
            
        else:
            self.runOptions.radioButton_distanceManhattan.setChecked(True)
            
        """distribution"""
        if GameTableOptions.distribution == "normal":
            self.runOptions.radioButton_distributionNormal.setChecked(True)
            
        elif GameTableOptions.distribution == "uniform":
            self.runOptions.radioButton_distributionUniform.setChecked(True)
            
        elif GameTableOptions.distribution == "pareto":
            self.runOptions.radioButton_distributionPareto.setChecked(True)
            
        else:
            self.runOptions.radioButton_distributionExponential.setChecked(True)

    def __loadOptions__(self, options):
        """TODO SET RUN OPTIONS IN GAMETABLEWIDGET IN MAIN LOAD FUN"""
        """
        Load all options other than run options here
        """
        self.visualizationOptions.lineWidthAgendaSetter_SpinBox.setValue(options["agendaSetter_lineWidth"])
        self.visualizationOptions.opacityAgendaSetter_SpinBox.setValue(options["agendaSetter_opacity"])
        self.visualizationOptions.sizeAgendaSetter_SpinBox.setValue(options["agendaSetter_size"])
        self.visualizationOptions.colorAgendaSetter = options["agendaSetter_mainColor"]
        self.visualizationOptions.colorAgendaSetterCircle = options["agendaSetter_circleColor"]
        
        self.visualizationOptions.lineWidthVetoPlayer_SpinBox.setValue(options["vetoPlayer_lineWidth"])
        self.visualizationOptions.opacityVetoPlayer_SpinBox.setValue(options["vetoPlayer_opacity"])
        self.visualizationOptions.sizeVetoPlayer_SpinBox.setValue(options["vetoPlayer_size"])
        self.visualizationOptions.colorVetoPlayer = options["vetoPlayer_mainColor"]
        self.visualizationOptions.colorVetoPlayerCircle = options["vetoPlayer_circleColor"]     
        
        self.visualizationOptions.lineWidthNormalVoter_SpinBox.setValue(options["normalVoter_lineWidth"])
        self.visualizationOptions.opacityNormalVoter_SpinBox.setValue(options["normalVoter_opacity"])
        self.visualizationOptions.sizeNormalVoter_SpinBox.setValue(options["normalVoter_size"])
        self.visualizationOptions.colorNormalVoter = options["normalVoter_mainColor"]
        self.visualizationOptions.colorNormalVoterCircle = options["normalVoter_circleColor"]      
        
        self.visualizationOptions.lineWidthTracer_SpinBox.setValue(options["traceLine_lineWidth"])
        self.visualizationOptions.opacityTracer_SpinBox.setValue(options["traceLine_opacity"])
        self.visualizationOptions.colorTracer = options["traceLine_color"]
        
        self.visualizationOptions.lineWidthWinset_SpinBox.setValue(options["winset_lineWidth"])
        self.visualizationOptions.opacityWinset_SpinBox.setValue(options["winset_opacity"])
        self.visualizationOptions.colorWinset = options["winset_color"]
        
        if options["plotTotalChange"] == "yes":
            self.visualizationOptions.radioButton_traceTotalChange_Yes.setChecked(True)
        elif options["plotTotalChange"] == "no":
            self.visualizationOptions.radioButton_traceTotalChange_No.setChecked(True)
        else:
            self.visualizationOptions.radioButton_traceTotalChange_Separate.setChecked(True)
            
        if options["plotRoleArray"] == "yes":
            self.visualizationOptions.radioButton_plotRoleArray_Yes.setChecked(True)
        elif options["plotRoleArray"] == "no":
            self.visualizationOptions.radioButton_plotRoleArray_No.setChecked(True)
        else:
            self.visualizationOptions.radioButton_plotRoleArray_Separate.setChecked(True)

        self.visualizationOptions.__buttonBGColorInit__()        
        
    def __saveOptions__(self):
        """
        Save current settings and voter setup
        """
        save = {"visualizationSettings": {
                        "agendaSetter_lineWidth" : self.visualizationOptions.lineWidthAgendaSetter_SpinBox.value(),
                        "agendaSetter_opacity" : self.visualizationOptions.opacityAgendaSetter_SpinBox.value(),
                        "agendaSetter_size" : self.visualizationOptions.sizeAgendaSetter_SpinBox.value(),
                        "agendaSetter_mainColor" : self.visualizationOptions.colorAgendaSetter,
                        "agendaSetter_circleColor" : self.visualizationOptions.colorAgendaSetterCircle,
                        
                        "vetoPlayer_lineWidth" : self.visualizationOptions.lineWidthVetoPlayer_SpinBox.value(),
                        "vetoPlayer_opacity" : self.visualizationOptions.opacityVetoPlayer_SpinBox.value(),
                        "vetoPlayer_size" : self.visualizationOptions.sizeVetoPlayer_SpinBox.value(),
                        "vetoPlayer_mainColor" : self.visualizationOptions.colorVetoPlayer,
                        "vetoPlayer_circleColor" : self.visualizationOptions.colorVetoPlayerCircle,
                        
                        "normalVoter_lineWidth" : self.visualizationOptions.lineWidthNormalVoter_SpinBox.value(),
                        "normalVoter_opacity" : self.visualizationOptions.opacityNormalVoter_SpinBox.value(),
                        "normalVoter_size" : self.visualizationOptions.sizeNormalVoter_SpinBox.value(),
                        "normalVoter_mainColor" : self.visualizationOptions.colorNormalVoter,
                        "normalVoter_circleColor" : self.visualizationOptions.colorNormalVoterCircle,
                        
                        "traceLine_lineWidth" : self.visualizationOptions.lineWidthTracer_SpinBox.value(),
                        "traceLine_opacity" : self.visualizationOptions.opacityTracer_SpinBox.value(),
                        "traceLine_color" : self.visualizationOptions.colorTracer,
                        
                        "winset_lineWidth" : self.visualizationOptions.lineWidthWinset_SpinBox.value(),
                        "winset_opacity" : self.visualizationOptions.opacityWinset_SpinBox.value(),
                        "winset_color" : self.visualizationOptions.colorWinset,
                        
                        "plotTotalChange" : self.visualizationOptions.buttonGroup_traceTotalChange.checkedButton().text().lower(),
                        "plotRoleArray" : self.visualizationOptions.buttonGroup_plotRoleArray.checkedButton().text().lower()
                        }
                }

        return save
#        with open(os.path.join(self.var_save_dir, "config.txt"), "w") as f:
#            json.dump(save, f)


class GeneralOptions(QtWidgets.QWidget):
    """
    General Options
    """
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.__setup__()
        self.__layout__()
        
        self.outputDir = None
        self.visualizationDir = None
        self.configDir = None        
        
    def __setup__(self):
        """
        Setup Textedits
        """
        self.lineEdit_outputDir = QtWidgets.QLineEdit()
        self.lineEdit_visualizationDir = QtWidgets.QLineEdit()
        self.lineEdit_configDir = QtWidgets.QLineEdit()
        
        self.pushButton_outputDir = QtWidgets.QPushButton("Set")
        self.pushButton_outputDir.clicked.connect(self.__setOutputDir__)
        
        self.pushButton_visualizationDir = QtWidgets.QPushButton("Set")
        self.pushButton_visualizationDir.clicked.connect(self.__setVisualizationDir__)
        
        self.pushButton_configDir = QtWidgets.QPushButton("Set")
        self.pushButton_configDir.clicked.connect(self.__setConfigDir__)
                
    def __layout__(self):
        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignLeft)
        
        groupBox_outputDir = QtWidgets.QGroupBox("Savefile Directory")
        output_hbox = QtWidgets.QHBoxLayout()
        output_hbox.addWidget(self.lineEdit_outputDir)
        output_hbox.addWidget(self.pushButton_outputDir)
        groupBox_outputDir.setLayout(output_hbox)
        
        layout.addWidget(groupBox_outputDir)
        
        groupBox_visualizationDir = QtWidgets.QGroupBox("Visualization Directory")
        visualization_hbox = QtWidgets.QHBoxLayout()
        visualization_hbox.addWidget(self.lineEdit_visualizationDir)
        visualization_hbox.addWidget(self.pushButton_visualizationDir)
        groupBox_visualizationDir.setLayout(visualization_hbox)
        
        layout.addWidget(groupBox_visualizationDir)
        
        groupBox_configDir = QtWidgets.QGroupBox("Startup File Directory")
        config_hbox = QtWidgets.QHBoxLayout()
        config_hbox.addWidget(self.lineEdit_configDir)
        config_hbox.addWidget(self.pushButton_configDir)
        groupBox_configDir.setLayout(config_hbox)
        
        layout.addWidget(groupBox_configDir)
        layout.addStretch(1)
        
        self.setLayout(layout)
        
    def __setConfigDir__(self):
        self.lineEdit_configDir.setText(QtWidgets.QFileDialog.getExistingDirectory())
        
    def __setVisualizationDir__(self):
        self.lineEdit_visualizationDir.setText(QtWidgets.QFileDialog.getExistingDirectory())
        
    def __setOutputDir__(self):
        self.lineEdit_outputDir.setText(QtWidgets.QFileDialog.getExistingDirectory())
 
       
class RunOptions(QtWidgets.QWidget):
    """
    Basic Options
    """
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.__setup__()
        self.__layout__()
        
    def __setup__(self):
        """""""""""
        Setup SpinBoxes
        """""""""""
        self.spinBox_runs = QtWidgets.QSpinBox()
        self.spinBox_runs.setValue(1)
        self.spinBox_runs.setMaximum(9999)
        self.spinBox_runs.setMinimum(1)
        
        self.spinBox_dimensions = QtWidgets.QSpinBox()
        self.spinBox_dimensions.setValue(2)
        self.spinBox_dimensions.setMinimum(1)
        
        self.doubleSpinBox_breaks = QtWidgets.QDoubleSpinBox()
        self.doubleSpinBox_breaks.setDecimals(4)
        self.doubleSpinBox_breaks.setSingleStep(0.0001)
        self.doubleSpinBox_breaks.setValue(0.01)
        self.doubleSpinBox_breaks.setMinimum(0.0001)
        
        """""""""""
        Setup Radiobuttons
        """""""""""
        """""""""""
        Method
        """""""""""
        self.buttonGroup_method = QtWidgets.QButtonGroup()
        self.radioButton_pointGrid = QtWidgets.QRadioButton("Grid")
        self.radioButton_optimization = QtWidgets.QRadioButton("Optimization")
        self.radioButton_pointGrid.setChecked(True)
        self.buttonGroup_method.addButton(self.radioButton_pointGrid)
        self.buttonGroup_method.addButton(self.radioButton_optimization)
        
        """""""""""
        Visualize
        """""""""""
        self.buttonGroup_visualize = QtWidgets.QButtonGroup()
        self.radioButton_visualize_yes = QtWidgets.QRadioButton("Yes")
        self.radioButton_visualize_yes.setChecked(True)
        self.radioButton_visualize_no = QtWidgets.QRadioButton("No")
        self.buttonGroup_visualize.addButton(self.radioButton_visualize_yes)
        self.buttonGroup_visualize.addButton(self.radioButton_visualize_no)
        
        """""""""""
        Save
        """""""""""
        self.buttonGroup_save = QtWidgets.QButtonGroup()
        self.radioButton_save_yes = QtWidgets.QRadioButton("Yes")
        self.radioButton_save_yes.setChecked(True)
        self.radioButton_save_no = QtWidgets.QRadioButton("No")
        self.buttonGroup_save.addButton(self.radioButton_save_yes)
        self.buttonGroup_save.addButton(self.radioButton_save_no)
        
        """""""""""
        Trace
        """""""""""
        self.buttonGroup_traceChanges = QtWidgets.QButtonGroup()
        self.radioButton_trace_yes = QtWidgets.QRadioButton("Yes")
        self.radioButton_trace_yes.setChecked(True)
        self.radioButton_trace_no = QtWidgets.QRadioButton("No")
        self.buttonGroup_traceChanges.addButton(self.radioButton_trace_yes)
        self.buttonGroup_traceChanges.addButton(self.radioButton_trace_no)
        
        """""""""""
        Alter Preferences
        """""""""""
        self.buttonGroup_alterPreferences = QtWidgets.QButtonGroup()
        self.radioButton_alterPreferences_drift = QtWidgets.QRadioButton("Drift")
        self.radioButton_alterPreferences_no = QtWidgets.QRadioButton("No")
        self.radioButton_alterPreferences_no.setChecked(True)
        self.buttonGroup_alterPreferences.addButton(self.radioButton_alterPreferences_drift)
        self.buttonGroup_alterPreferences.addButton(self.radioButton_alterPreferences_no)
       
        """""""""""
        Alter Status Quo
        """""""""""
        self.buttonGroup_alterStatusQuo = QtWidgets.QButtonGroup()
        self.radioButton_alterStatusQuo_no = QtWidgets.QRadioButton("No")
        self.radioButton_alterStatusQuo_random = QtWidgets.QRadioButton("Random")
        self.radioButton_alterStatusQuo_history = QtWidgets.QRadioButton("History")
        self.radioButton_alterStatusQuo_historyAndDrift = QtWidgets.QRadioButton("History+Drift")
        self.radioButton_alterStatusQuo_historyAndDrift.setChecked(True)
        self.buttonGroup_alterStatusQuo.addButton(self.radioButton_alterStatusQuo_no)
        self.buttonGroup_alterStatusQuo.addButton(self.radioButton_alterStatusQuo_random)
        self.buttonGroup_alterStatusQuo.addButton(self.radioButton_alterStatusQuo_history)
        self.buttonGroup_alterStatusQuo.addButton(self.radioButton_alterStatusQuo_historyAndDrift)
        
        """""""""""
        Distribution
        """""""""""
        self.buttonGroup_distribution = QtWidgets.QButtonGroup()
        self.radioButton_distributionNormal = QtWidgets.QRadioButton("Normal")
        self.radioButton_distributionPareto = QtWidgets.QRadioButton("Pareto")
        self.radioButton_distributionUniform = QtWidgets.QRadioButton("Uniform")
        self.radioButton_distributionUniform.setChecked(True)
        self.radioButton_distributionExponential = QtWidgets.QRadioButton("Exponential")
        self.buttonGroup_distribution.addButton(self.radioButton_distributionNormal)
        self.buttonGroup_distribution.addButton(self.radioButton_distributionPareto)
        self.buttonGroup_distribution.addButton(self.radioButton_distributionUniform)
        self.buttonGroup_distribution.addButton(self.radioButton_distributionExponential)   
        
        """""""""""
        Distance Type
        """""""""""
        self.buttonGroup_distanceType = QtWidgets.QButtonGroup()
        self.radioButton_distanceEuclidean = QtWidgets.QRadioButton("Euclidean")
        self.radioButton_distanceEuclidean.setChecked(True)
        self.radioButton_distanceManhattan = QtWidgets.QRadioButton("Manhattan")
        self.buttonGroup_distanceType.addButton(self.radioButton_distanceEuclidean)
        self.buttonGroup_distanceType.addButton(self.radioButton_distanceManhattan)
    
    def __layout__(self):
        layout = QtWidgets.QVBoxLayout(self)
        
        """""""""""
        General
        """""""""""
        groupBox_general = QtWidgets.QGroupBox("General")
        
        spinBox_vbox = QtWidgets.QVBoxLayout()
        
        for widget in [self.__spinBoxSetup__(spinBox, label) for 
                       spinBox, label in zip([self.spinBox_runs, self.spinBox_dimensions, self.doubleSpinBox_breaks], ["Runs", "Dimensions", "Breaks"])]:
            spinBox_vbox.addLayout(widget)
                    
        groupBox_general.setLayout(spinBox_vbox)
        
        layout.addWidget(groupBox_general)
        
        """Method"""
        groupBox_method = QtWidgets.QGroupBox("Method")
        
        method_hbox = QtWidgets.QHBoxLayout()
        
        for widget in [self.radioButton_pointGrid, self.radioButton_optimization]:
            method_hbox.addWidget(widget)
            
        groupBox_method.setLayout(method_hbox)
        
        layout.addWidget(groupBox_method)
        
        """""""""""
        Save
        """""""""""
        groupBox_save = QtWidgets.QGroupBox("Save")
        
        save_hbox = QtWidgets.QHBoxLayout()
        
        for widget in [self.radioButton_save_yes, self.radioButton_save_no]:
            save_hbox.addWidget(widget)
            
        groupBox_save.setLayout(save_hbox)
        
        layout.addWidget(groupBox_save)
        
        """""""""""
        Visualize
        """""""""""
        groupBox_visualize = QtWidgets.QGroupBox("Visualize")
        
        visualization_hbox = QtWidgets.QHBoxLayout()
        
        for widget in [self.radioButton_visualize_yes, self.radioButton_visualize_no]:
            visualization_hbox.addWidget(widget)
            
        groupBox_visualize.setLayout(visualization_hbox)
        
        layout.addWidget(groupBox_visualize)
        
        """""""""""
        Alter Preferences
        """""""""""
        groupBox_alterPreferences = QtWidgets.QGroupBox("Alter Preferences")
        
        alterPreferences_hbox = QtWidgets.QHBoxLayout()
        
        for widget in [self.radioButton_alterPreferences_drift, self.radioButton_alterPreferences_no]:
            alterPreferences_hbox.addWidget(widget)
            
        groupBox_alterPreferences.setLayout(alterPreferences_hbox)
        
        layout.addWidget(groupBox_alterPreferences)
        
        """""""""""
        Alter Status Quo
        """""""""""
        groupBox_alterStatusQuo = QtWidgets.QGroupBox("Alter Status Quo")
        
        alterStatusQuo_vbox = self.__radioButtonSetup__([self.radioButton_alterStatusQuo_historyAndDrift, self.radioButton_alterStatusQuo_history,
                                                         self.radioButton_alterStatusQuo_random, self.radioButton_alterStatusQuo_no], 2)
            
        groupBox_alterStatusQuo.setLayout(alterStatusQuo_vbox)
        
        layout.addWidget(groupBox_alterStatusQuo)
        
        """""""""""
        Distance Type
        """""""""""
        groupBox_distanceType = QtWidgets.QGroupBox("Distance Type")
        
        distanceType_vbox = self.__radioButtonSetup__([self.radioButton_distanceEuclidean, self.radioButton_distanceManhattan], 1)

        groupBox_distanceType.setLayout(distanceType_vbox)
        
        layout.addWidget(groupBox_distanceType)
        
        """""""""""
        Distribution
        """""""""""
        groupBox_distribution = QtWidgets.QGroupBox("Distribution")
        
        distribution_vbox = self.__radioButtonSetup__([self.radioButton_distributionNormal, self.radioButton_distributionUniform,
                                                       self.radioButton_distributionPareto, self.radioButton_distributionExponential], 2)
            
        groupBox_distribution.setLayout(distribution_vbox)
        
        layout.addWidget(groupBox_distribution)

        layout.setAlignment(QtCore.Qt.AlignLeft)
        layout.addStretch(1)
        self.setLayout(layout)
        
    def __radioButtonSetup__(self, buttons, rows, label = None):
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setAlignment(QtCore.Qt.AlignLeft)
        
        if label is not None:
            vbox.addWidget(label)
        
        if rows == 1:
            hbox = QtWidgets.QHBoxLayout(self)
            
            for i, button in enumerate(buttons):
                hbox.addWidget(button)
                
            vbox.addLayout(hbox)

        elif rows == 2:
            grid = QtWidgets.QGridLayout(self)
            for i, button in enumerate(buttons[:2]):
                grid.addWidget(button, 0, i)
                
            for i, button in enumerate(buttons[2:]):
                grid.addWidget(button, 1, i)
                
            vbox.addLayout(grid)
            
        return vbox

    def __spinBoxSetup__(self, spinBox, label):
        layout = QtWidgets.QVBoxLayout(self)
        
        label = QtWidgets.QLabel(label)
        label.setAlignment(QtCore.Qt.AlignBottom)
                
        layout.addWidget(label)
        layout.addWidget(spinBox)
        
        return layout    
    
    
class VisualizeOptions(QtWidgets.QWidget):
    """
    Visualization Options
    """
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.__setup__()
        self.__layout__()
                
    def __setup__(self):
        """""""""""
        Plot Colors
        """""""""""
        self.colorVetoPlayer = "#d62728"
        self.colorNormalVoter = "#7f7f7"
        self.colorAgendaSetter = "#1f77b4"
        self.colorStatusQuo = "#8c564b"
        self.colorOutcome = "#ff7f0e"
        self.colorVetoPlayerCircle = "#d62728"
        self.colorNormalVoterCircle = "#7f7f7f"
        self.colorAgendaSetterCircle = "#1f77b4"
        self.colorWinset = "#ff7f0e"
        self.colorTracer = "#2ca02c"
        
        """""""""""
        Column Labels
        """""""""""
        self.label_lineWidth = QtWidgets.QLabel("Line Width")
        self.label_opacity = QtWidgets.QLabel("Opacity")
        self.label_size = QtWidgets.QLabel("Size")
        self.label_color = QtWidgets.QLabel("Main Color")
        self.label_colorCircle = QtWidgets.QLabel("Circle Color")
        
        self.label_agendaSetter = QtWidgets.QLabel("Agenda Setter")
        self.label_vetoPlayer = QtWidgets.QLabel("Veto Player")
        self.label_normalVoter = QtWidgets.QLabel("Normal Voter")
        self.label_statusQuo = QtWidgets.QLabel("Status Quo")
        self.label_trace = QtWidgets.QLabel("Trace Line")
        self.label_winset = QtWidgets.QLabel("Winset")
        
        self.label2_lineWidth = QtWidgets.QLabel("Line Width")
        self.label2_opacity = QtWidgets.QLabel("Opacity")
        self.label2_color = QtWidgets.QLabel("Main Color")

        """""""""""
        Agenda Setter
        """""""""""
        self.lineWidthAgendaSetter_SpinBox = QtWidgets.QSpinBox()
        self.lineWidthAgendaSetter_SpinBox.setValue(1)
        
        self.opacityAgendaSetter_SpinBox = QtWidgets.QSpinBox()
        self.opacityAgendaSetter_SpinBox.setValue(50)
        self.opacityAgendaSetter_SpinBox.setMaximum(100)
        
        self.sizeAgendaSetter_SpinBox = QtWidgets.QSpinBox()
        self.sizeAgendaSetter_SpinBox.setValue(60)
        
        self.colorAgendaSetter_Button = QtWidgets.QPushButton()
        self.colorAgendaSetter_Button.clicked.connect(self.setAgendaSetterColor)
        
        self.colorAgendaSetterCircle_Button = QtWidgets.QPushButton()
        self.colorAgendaSetterCircle_Button.clicked.connect(self.setAgendaSetterCircleColor)
        
        """""""""""
        Veto Player
        """""""""""
        self.lineWidthVetoPlayer_SpinBox = QtWidgets.QSpinBox()
        self.lineWidthVetoPlayer_SpinBox.setValue(1)
        
        self.opacityVetoPlayer_SpinBox = QtWidgets.QSpinBox()
        self.opacityVetoPlayer_SpinBox.setValue(50)
        self.opacityVetoPlayer_SpinBox.setMaximum(100)
        
        self.sizeVetoPlayer_SpinBox = QtWidgets.QSpinBox()
        self.sizeVetoPlayer_SpinBox.setValue(60)
        
        self.colorVetoPlayer_Button = QtWidgets.QPushButton()
        self.colorVetoPlayer_Button.clicked.connect(self.setVetoPlayerColor)
                
        self.colorVetoPlayerCircle_Button = QtWidgets.QPushButton()
        self.colorVetoPlayerCircle_Button.clicked.connect(self.setVetoPlayerCircleColor)
        
        """""""""""
        Normal Voter
        """""""""""
        self.lineWidthNormalVoter_SpinBox = QtWidgets.QSpinBox()
        self.lineWidthNormalVoter_SpinBox.setValue(1)
        
        self.opacityNormalVoter_SpinBox = QtWidgets.QSpinBox()
        self.opacityNormalVoter_SpinBox.setValue(50)
        self.opacityNormalVoter_SpinBox.setMaximum(100)
        
        self.sizeNormalVoter_SpinBox = QtWidgets.QSpinBox()
        self.sizeNormalVoter_SpinBox.setValue(60)       
        
        self.colorNormalVoter_Button = QtWidgets.QPushButton()
        self.colorNormalVoter_Button.clicked.connect(self.setNormalVoterColor)
        
        self.colorNormalVoterCircle_Button = QtWidgets.QPushButton()
        self.colorNormalVoterCircle_Button.clicked.connect(self.setNormalVoterCircleColor)
        
        """""""""""
        Status Quo
        """""""""""
        self.sizeStatusQuo_SpinBox = QtWidgets.QSpinBox()
        self.sizeStatusQuo_SpinBox.setValue(60)
        
        self.colorStatusQuo_Button = QtWidgets.QPushButton()
        self.colorStatusQuo_Button.clicked.connect(self.setStatusQuoColor)
        
        """""""""""
        Outcome
        """""""""""       
        self.sizeOutcome_SpinBox = QtWidgets.QSpinBox()
        self.sizeOutcome_SpinBox.setValue(60)
        
        self.colorOutcome_Button = QtWidgets.QPushButton()
        self.colorOutcome_Button.clicked.connect(self.setStatusQuoColor)
        
        """""""""""
        Trace Line
        """""""""""
        self.lineWidthTracer_SpinBox = QtWidgets.QSpinBox()
        self.lineWidthTracer_SpinBox.setValue(1)
        
        self.opacityTracer_SpinBox = QtWidgets.QSpinBox()
        self.opacityTracer_SpinBox.setValue(50)

        self.colorTracer_Button = QtWidgets.QPushButton()
        self.colorTracer_Button.clicked.connect(self.setTracerColor)
        
        """""""""""
        Winset
        """""""""""
        self.lineWidthWinset_SpinBox = QtWidgets.QSpinBox()
        self.lineWidthWinset_SpinBox.setValue(1)
        
        self.opacityWinset_SpinBox = QtWidgets.QSpinBox()
        self.opacityWinset_SpinBox.setValue(50)
        
        self.colorWinset_Button = QtWidgets.QPushButton()
        self.colorWinset_Button.clicked.connect(self.setWinsetColor)
        
        """""""""""
        Other Options
        """""""""""
        self.checkBox_drawAnimation = QtWidgets.QCheckBox()
        self.checkBox_drawAnimation.setChecked(True)
        
        self.checkBox_drawSingle = QtWidgets.QCheckBox()
        self.checkBox_drawSingle.setChecked(True)
        
        self.buttonGroup_traceTotalChange = QtWidgets.QButtonGroup()
        self.radioButton_traceTotalChange_Yes = QtWidgets.QRadioButton("Yes")
        self.radioButton_traceTotalChange_Separate = QtWidgets.QRadioButton("Separate")
        self.radioButton_traceTotalChange_No = QtWidgets.QRadioButton("No")
        self.radioButton_traceTotalChange_Yes.setChecked(True)
        self.buttonGroup_traceTotalChange.addButton(self.radioButton_traceTotalChange_Yes)
        self.buttonGroup_traceTotalChange.addButton(self.radioButton_traceTotalChange_Separate)
        self.buttonGroup_traceTotalChange.addButton(self.radioButton_traceTotalChange_No)
        
        self.buttonGroup_plotRoleArray = QtWidgets.QButtonGroup()
        self.radioButton_plotRoleArray_Yes = QtWidgets.QRadioButton("Yes")
        self.radioButton_plotRoleArray_Separate = QtWidgets.QRadioButton("Separate")
        self.radioButton_plotRoleArray_No = QtWidgets.QRadioButton("No")
        self.radioButton_plotRoleArray_Yes.setChecked(True)
        self.buttonGroup_plotRoleArray.addButton(self.radioButton_plotRoleArray_Yes)
        self.buttonGroup_plotRoleArray.addButton(self.radioButton_plotRoleArray_Separate)
        self.buttonGroup_plotRoleArray.addButton(self.radioButton_plotRoleArray_No)
        
        self.__buttonBGColorInit__()

    def __buttonBGColorInit__(self):
        """""""""""
        Button BG Color Init
        """""""""""
        for button, color in zip([self.colorVetoPlayer_Button, self.colorNormalVoter_Button, self.colorAgendaSetter_Button, self.colorStatusQuo_Button,
                                  self.colorOutcome_Button, self.colorVetoPlayerCircle_Button, self.colorNormalVoterCircle_Button, 
                                  self.colorAgendaSetterCircle_Button, self.colorWinset_Button, self.colorTracer_Button],
                                  [self.colorVetoPlayer, self.colorNormalVoter, self.colorAgendaSetter, self.colorStatusQuo, self.colorOutcome,
                                   self.colorVetoPlayerCircle, self.colorNormalVoterCircle, self.colorAgendaSetterCircle, self.colorWinset, self.colorTracer]):
            self.setBG(button, color)
            
    def __layout__(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignLeft)
        
        """""""""""
        Players
        """""""""""
        groupBox_Players = QtWidgets.QGroupBox("Players")
                
        players_grid = QtWidgets.QGridLayout(self)
        players_grid.setAlignment(QtCore.Qt.AlignLeft)
        
        [players_grid.addWidget(widget, 0, i + 1) for i, widget in enumerate([self.label_lineWidth, self.label_opacity, self.label_size, 
         self.label_color, self.label_colorCircle])]
        
        [players_grid.addWidget(widget, 1, i) for i, widget in enumerate([self.label_agendaSetter, self.lineWidthAgendaSetter_SpinBox, 
         self.opacityAgendaSetter_SpinBox, self.sizeAgendaSetter_SpinBox, self.colorAgendaSetter_Button, self.colorAgendaSetterCircle_Button])]
        
        [players_grid.addWidget(widget, 2, i) for i, widget in enumerate([self.label_vetoPlayer, self.lineWidthVetoPlayer_SpinBox, 
         self.opacityVetoPlayer_SpinBox, self.sizeVetoPlayer_SpinBox, self.colorVetoPlayer_Button, self.colorVetoPlayerCircle_Button])]
        
        [players_grid.addWidget(widget, 3, i) for i, widget in enumerate([self.label_normalVoter, self.lineWidthNormalVoter_SpinBox,
         self.opacityNormalVoter_SpinBox, self.sizeNormalVoter_SpinBox, self.colorNormalVoter_Button, self.colorNormalVoterCircle_Button])]     
        
        groupBox_Players.setLayout(players_grid)
        
        layout.addWidget(groupBox_Players)
        
        """""""""""
        Objects
        """""""""""
        groupBox_Objects = QtWidgets.QGroupBox("Objects")
        
        objects_grid = QtWidgets.QGridLayout()
        
        [objects_grid.addWidget(widget, 0, i + 1) for i, widget in enumerate([self.label2_lineWidth, self.label2_opacity, self.label2_color])]
        
        [objects_grid.addWidget(widget, 1, i) for i, widget in enumerate([self.label_trace, self.lineWidthTracer_SpinBox,
         self.opacityTracer_SpinBox, self.colorTracer_Button])]

        [objects_grid.addWidget(widget, 2, i) for i, widget in enumerate([self.label_winset, self.lineWidthWinset_SpinBox, 
         self.opacityWinset_SpinBox, self.colorWinset_Button])]
        
        groupBox_Objects.setLayout(objects_grid)
        
        layout.addWidget(groupBox_Objects)        
        
        """""""""""
        Additional Plots
        """""""""""
        groupBox_plotTotalChange = QtWidgets.QGroupBox("Plot Total Change")
        
        plotTotalChange_hbox = QtWidgets.QHBoxLayout()
        [plotTotalChange_hbox.addWidget(widget) for widget in [
                self.radioButton_traceTotalChange_Yes, self.radioButton_traceTotalChange_Separate, self.radioButton_traceTotalChange_No]]
        
        groupBox_plotTotalChange.setLayout(plotTotalChange_hbox)
         
        layout.addWidget(groupBox_plotTotalChange)
        
        groupBox_plotRoleArray = QtWidgets.QGroupBox("Plot Role Array")
        
        plotRoleArray_hbox = QtWidgets.QHBoxLayout()
        
        [plotRoleArray_hbox.addWidget(widget) for widget in [
                self.radioButton_plotRoleArray_Yes, self.radioButton_plotRoleArray_Separate, self.radioButton_plotRoleArray_No]]
        
        groupBox_plotRoleArray.setLayout(plotRoleArray_hbox)
        
        layout.addWidget(groupBox_plotRoleArray)
        
        layout.addStretch(1)
        self.setLayout(layout)        

    def __labelVBox__(self, widget, label):
        """
        VBox for Label over Widget
        """
        vbox = QtWidgets.QVBoxLayout(self)
        
        label = QtWidgets.QLabel(label)
        label.setAlignment(QtCore.Qt.AlignLeft)

        vbox.addWidget(label)
        vbox.addWidget(widget)

        return vbox        
        
    def __radioButtonSetup__(self, buttons, rows, label = None):
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setAlignment(QtCore.Qt.AlignLeft)
        
        if label is not None:
            vbox.addWidget(label)
        
        if rows == 1:
            hbox = QtWidgets.QHBoxLayout(self)
            
            for i, button in enumerate(buttons):
                hbox.addWidget(button)
                
            vbox.addLayout(hbox)

        elif rows == 2:
            grid = QtWidgets.QGridLayout(self)
            for i, button in enumerate(buttons[:2]):
                grid.addWidget(button, 0, i)
                
            for i, button in enumerate(buttons[2:]):
                grid.addWidget(button, 1, i)
                
            vbox.addLayout(grid)
            
        return vbox
        
    def setNormalVoterColor(self):
        color = self.colorPicker(self.colorNormalVoter_Button)
        self.colorNormalVoter = color.name()
    
    def setVetoPlayerColor(self):
        color = self.colorPicker(self.colorVetoPlayer_Button)
        self.colorVetoPlayer = color.name()
        
    def setAgendaSetterColor(self):
        color = self.colorPicker(self.colorAgendaSetter_Button)
        self.colorAgendaSetter = color.name()
        
    def setStatusQuoColor(self):
        color = self.colorPicker(self.colorStatusQuo_Button)
        self.colorStatusQuo = color.name()
        
    def setNormalVoterCircleColor(self):
        color = self.colorPicker(self.colorNormalVoterCircle_Button)
        self.colorNormalVoterCircle = color.name()
    
    def setVetoPlayerCircleColor(self):
        color = self.colorPicker(self.colorVetoPlayerCircle_Button)
        self.colorVetoPlayerCircle = color.name()
        
    def setAgendaSetterCircleColor(self):
        color = self.colorPicker(self.colorAgendaSetterCircle_Button)
        self.colorAgendaSetterCircle = color.name()
        
    def setWinsetColor(self):
        color = self.colorPicker(self.colorWinset_Button)
        self.colorWinset = color.name()
        
    def setTracerColor(self):
        color = self.colorPicker(self.colorTracer_Button)
        self.colorTracer = color.name()
        
    def colorPicker(self, button):
        color =  QtWidgets.QColorDialog.getColor()
        if not color.isValid():
            return
        button.setStyleSheet("background-color: {0}".format(color.name()))
        
    def setBG(self, button, color):
        button.setStyleSheet("background-color: {0}".format(color))
 
           
class AdvancedOptions(QtWidgets.QWidget):
    """
    Advanced Options
    """
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.__setup__()
        self.__layout__()
        
    def __setup__(self):
        self.spin = QtWidgets.QSpinBox()
    
    def __layout__(self):
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.spin)
        self.setLayout(layout)
        

class StatusDockWidget(QtWidgets.QWidget):
    """
    Tab Widget for Log and Environment
    """
    def __init__(self, parent):
        super(StatusDockWidget, self).__init__(parent)
        self.__setup__()
        self.__layout__()
        
    def __setup__(self):
        self.tabWidget = QtWidgets.QTabWidget()
        
        logTab = QtWidgets.QTextEdit()
        environmentTab = QtWidgets.QTableWidget()
        
        self.tabWidget.addTab(logTab, "A")
        self.tabWidget.addTab(environmentTab, "B")
        
    def __layout__(self):
        pass
    
            
class plotViewDockWidget(QtWidgets.QWidget):
    """
    Matplotlib Viewer for Image Output
    """
    def __init__(self, parent):
        super(plotViewDockWidget, self).__init__(parent)
        self.__setup__()
        self.__layout__()
        

        
    def __setup__(self):
        pass
    
    def __layout__(self):
        pass
    

class VisualizeDockWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super(VisualizeDockWidget, self).__init__(parent)
        
    def __initFigure__(self, figure):
        self.canvas = FigureCanvas(figure)
        
    def __layout__(self):
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
    
class LogDockWidget(QtWidgets.QTextEdit):
    def __init__(self, parent):
        super(LogDockWidget, self).__init__(parent)
        self.setDisabled(True)
        self.__setup__()
        self.__layout__()
        
    def __setup__(self):
#        self.log = QtWidgets.QTextEdit()
#        self.log.setDisabled(True)
        pass
    def __layout__(self):
#        layout = QtWidgets.QVBoxLayout()
#        layout.addWidget(self.log)
#        self.setLayout(layout)
        pass
    
    
class ManifestoPyDockWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super(ManifestoPyDockWidget, self).__init__(parent)
        self.__setup__()
        self.__layout__()
        
        self.api_connected = False
                
    def __setup__(self):
        """
        Setup Widgets + Signals
        """
        self.connect_GroupBox = QtWidgets.QGroupBox("Connect to Manifesto Project API")
        
        self.lineEdit_APIkey = QtWidgets.QLineEdit()
        self.lineEdit_APIkey.setEchoMode(QtWidgets.QLineEdit.Password)

        self.pushButton_APIconnect = QtWidgets.QPushButton("Connect")
        self.pushButton_APIconnect.clicked.connect(self.__apiConnect__)

        self.listWidget_APIcountry = QtWidgets.QListWidget()
        self.listWidget_APIcountry.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.listWidget_APIcountry.itemDoubleClicked.connect(self.__manifestoAPI_country__)  
        
        self.listWidget_APIparty = QtWidgets.QListWidget()
        self.listWidget_APIparty.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.listWidget_APIparty.selectionModel().selectionChanged.connect(self.__manifestoAPI_addIssues__)

        self.listWidget_APIparty = QtWidgets.QListWidget()
        self.listWidget_APIparty.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        
        self.listWidget_APIyear = QtWidgets.QListWidget()
        self.listWidget_APIyear.selectionModel().selectionChanged.connect(self.___manifestoAPI_year__)
        
        self.listWidget_APIissue = QtWidgets.QListWidget()
        self.listWidget_APIissue.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.listWidget_APIissue.selectionModel().selectionChanged.connect(self.__manifestoAPI_addYears__)
        
        self.pushButton_APIadd = QtWidgets.QPushButton("Add")
        
    def __layout__(self):
        """
        Layout
        """
        layout = QtWidgets.QHBoxLayout(self)
        
        self.connect_hbox = QtWidgets.QHBoxLayout()
        self.connect_hbox.addStretch(1)
        
        connect_vbox = QtWidgets.QVBoxLayout()
        connect_vbox.setAlignment(QtCore.Qt.AlignCenter)
        connect_vbox.addWidget(self.lineEdit_APIkey)
        connect_vbox.addWidget(self.pushButton_APIadd)
        
        self.connect_hbox.addLayout(connect_vbox)
        self.connect_hbox.addStretch(1)
        layout.addLayout(self.connect_hbox)
        
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        
        for widget in [self.listWidget_APIcountry, self.listWidget_APIparty, self.listWidget_APIissue, self.listWidget_APIyear]:
            self.splitter.addWidget(widget)
        
        layout.addWidget(self.splitter)
        self.splitter.hide()
        
        self.setLayout(layout)
        
    def sizeHint(self):
        return QtCore.QSize(100, 100)
    
    def __apiConnect__(self):
        """
        Connect to Manifesto Project API via manifestoPY and load main dataset
        """
        import manifestoPY
        
        key = self.lineEdit_APIkey.text()
        
        try:
            manifesto = manifestoPY.Manifesto(key)
            self.APIconnected = True
        except:
            raise
            
        try:
            self.manifesto_maindf = manifesto.mp_maindataset()
        except:
            raise
            
        self.listWidget_APIcountry.addItems(list(self.manifesto_maindf["countryname"].sort_values().unique()))
        
        self.connect_hbox.hide()
        self.splitter.show()
        
    def ___manifestoAPI_year__(self):
        """
        Get the year selected in the Manifesto API year list widget
        """
        self.year = self.listWidget_APIyear.currentItem().text()
        
    def __manifestoAPI_addYears__(self):
        """
        Add years for which datasets are available for the given party/parties
        to the Manifesto API year list widget
        """
        self.listWidget_APIyear.clear()
        self.issue_selection = [item.text() for item in self.listWidget_APIissue.selectedItems()]
        self.listWidget_APIyear.addItems([str(item)[:10] for item in list(
                self.manifesto_maindf[["edate"] + self.issue_selection][self.manifesto_maindf["partyname"].isin(self.party_selection)].
                dropna(axis = 0, how = "any").iloc[:, 0])])
            
    def __manifestoAPI_addIssues__(self):
        """
        Add issues for which datasets are available for the given party/parties
        to the Manifesto API list widget
        """
        self.listWidget_APIissue.clear()
        self.party_selection = [item.text() for item in self.listWidget_APIparty.selectedItems()]

        self.listWidget_APIissue.addItems(list(
                self.manifesto_maindf.loc[(self.manifesto_maindf["partyname"].isin(self.party_selection))].
                dropna(how = "any", axis = 1).iloc[:, 25:-1]))
        
    def __manifestoAPI_country__(self, item):
        """
        Add countries for which datasets are available to the Manifesto API list widget
        """
        self.listWidget_APIparty.clear()
        self.country = item.text()
        self.listWidget_APIparty.addItems(list(
                self.manifesto_maindf["partyname"][self.manifesto_maindf["countryname"] == self.country].sort_values().unique()))
        
        
class TableWidget(QtWidgets.QTableWidget):
    """
    QTableWidget Subclass for Custom Context Menu
    """
    def __init__(self, parent = None):
        QtWidgets.QTableWidget.__init__(self, parent)
        
    def addRow(self):
        self.insertRow(self.rowCount())
        
    def delRow(self):
        if self.rowCount() > 2:
            self.removeRow(self.rowCount() - 1)
        else:
            return
        
    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu(self)
        addAction = menu.addAction("Add Voter")
        duplicateAction = menu.addAction("Duplicate Voter") #TODO a
        quitAction = menu.addAction("Remove Voter")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        
        if action == quitAction:
            indices = self.selectedIndexes()
            for item in indices:
                self.removeRow(item.row())
        
        elif action == addAction:
            if self.rowCount() == 0:
                self.setRowCount(1)
            else:
                self.insertRow(self.selectedIndexes()[0].row() + 1)
                
        else:
            return


class SimulationVariables:
    def __init__(self, **kwargs):
        self.votercount = kwargs["votercount"]
        self.runs = kwargs["runs"]
        self.dimensions = kwargs["dimensions"]
        self.breaks = kwargs["breaks"]
        self.save = kwargs["save"]
        self.visualize = kwargs["visualize"]
        self.alterPreferences = kwargs["alterPreferences"] 
        self.alterStatusQuo = kwargs["alterStatusQuo"]
        self.distanceType = kwargs["distanceType"]
        self.distribution = kwargs["distribution"]
        
        self.trace = True
        self.directory = kwargs["directory"]
        
        self.statusQuoPosition = kwargs["statusQuoPosition"]
        self.statusQuoDrift = kwargs["statusQuoDrift"]
        self.voterNames = kwargs["voterNames"]
        self.voterRoles = kwargs["voterRoles"]
        self.voterPositions = kwargs["voterPositions"]
        
        self.customRoleArray = kwargs["customRoleArray"]
        
        self.randomAgendaSetter = kwargs["randomAgendaSetter"]
        self.randomVetoPlayer = kwargs["randomVetoPlayer"]
           
        self.method = kwargs["method"]
        
        
class EditableTabBar(QtWidgets.QTabBar):
    def __init__(self, parent):
        QtWidgets.QTabBar.__init__(self, parent)
        self._editor = QtWidgets.QLineEdit(self)
        self._editor.setWindowFlags(QtCore.Qt.Popup)
        self._editor.setFocusProxy(self)
        self._editor.editingFinished.connect(self.handleEditingFinished)
        self._editor.installEventFilter(self)

    def eventFilter(self, widget, event):
        if ((event.type() == QtCore.QEvent.MouseButtonPress and not self._editor.geometry().contains(event.globalPos())) or (event.type() == QtCore.QEvent.KeyPress and event.key() == QtCore.Qt.Key_Escape)):
            self._editor.hide()
            return True
        return QtWidgets.QTabBar.eventFilter(self, widget, event)

    def mouseDoubleClickEvent(self, event):
        index = self.tabAt(event.pos())
        if index >= 0:
            self.editTab(index)

    def editTab(self, index):
        rect = self.tabRect(index)
        self._editor.setFixedSize(rect.size())
        self._editor.move(self.parent().mapToGlobal(rect.topLeft()))
        self._editor.setText(self.tabText(index))
        if not self._editor.isVisible():
            self._editor.show()

    def handleEditingFinished(self):
        index = self.currentIndex()
        if index >= 0:
            self._editor.hide()
            self.setTabText(index, self._editor.text())
        

def main():
    app = QtWidgets.QApplication(sys.argv) 
    app.setWindowIcon(QtGui.QIcon("./assets/logo.png"))
    window = MainWindow() 
    window.show() 
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()

 
