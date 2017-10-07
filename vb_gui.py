# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets

import vb_var as var
import vb_sim as vb_simulation
import os
import errno
import time
import json
import logging

logging.basicConfig(filename = 'vb_log.log', level = logging.DEBUG)
logging.info('-----------------New Run--------------------')

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(682, 869)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label_logo = QtWidgets.QLabel(self.centralwidget)
        self.label_logo.setGeometry(QtCore.QRect(10, 0, 601, 91))
        self.label_logo.setObjectName("label_logo")
        self.label_logo.setText("")
        self.label_logo.setPixmap(QtGui.QPixmap("vetoboxing.png"))
        self.stackedWidget = QtWidgets.QStackedWidget(self.centralwidget)
        self.stackedWidget.setGeometry(QtCore.QRect(180, 330, 481, 181))
        self.stackedWidget.setObjectName("stackedWidget")
        self.page = QtWidgets.QWidget()
        self.page.setObjectName("page")
        self.tableWidget_votersOverview = QtWidgets.QTableWidget(self.page)
        self.tableWidget_votersOverview.setGeometry(QtCore.QRect(10, 0, 471, 181))
        self.tableWidget_votersOverview.setObjectName("tableWidget_votersOverview")
        self.tableWidget_votersOverview.setColumnCount(0)
        self.tableWidget_votersOverview.setRowCount(0)
        self.stackedWidget.addWidget(self.page)
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setObjectName("page_2")
        self.tableWidget_VotersPositions = QtWidgets.QTableWidget(self.page_2)
        self.tableWidget_VotersPositions.setGeometry(QtCore.QRect(10, 0, 471, 181))
        self.tableWidget_VotersPositions.setObjectName("tableWidget_VotersPositions")
        self.tableWidget_VotersPositions.setColumnCount(0)
        self.tableWidget_VotersPositions.setRowCount(0)
        self.stackedWidget.addWidget(self.page_2)
        self.page_3 = QtWidgets.QWidget()
        self.page_3.setObjectName("page_3")
        self.tableWidget_VotersDrift = QtWidgets.QTableWidget(self.page_3)
        self.tableWidget_VotersDrift.setGeometry(QtCore.QRect(10, 0, 471, 181))
        self.tableWidget_VotersDrift.setObjectName("tableWidget_VotersDrift")
        self.tableWidget_VotersDrift.setColumnCount(0)
        self.tableWidget_VotersDrift.setRowCount(0)
        self.stackedWidget.addWidget(self.page_3)
        self.groupBox_voterSetup = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_voterSetup.setGeometry(QtCore.QRect(10, 120, 331, 51))
        self.groupBox_voterSetup.setTitle("")
        self.groupBox_voterSetup.setObjectName("groupBox_voterSetup")
        self.label_voterCount = QtWidgets.QLabel(self.groupBox_voterSetup)
        self.label_voterCount.setGeometry(QtCore.QRect(10, 0, 81, 16))
        self.label_voterCount.setObjectName("label_voterCount")
        self.spinBox_voterCount = QtWidgets.QSpinBox(self.groupBox_voterSetup)
        self.spinBox_voterCount.setGeometry(QtCore.QRect(10, 20, 91, 22))
        self.spinBox_voterCount.setObjectName("spinBox_voterCount")
        self.label_vetoCount = QtWidgets.QLabel(self.groupBox_voterSetup)
        self.label_vetoCount.setGeometry(QtCore.QRect(120, 0, 111, 16))
        self.label_vetoCount.setObjectName("label_vetoCount")
        self.spinBox_playerCount = QtWidgets.QSpinBox(self.groupBox_voterSetup)
        self.spinBox_playerCount.setGeometry(QtCore.QRect(120, 20, 91, 22))
        self.spinBox_playerCount.setObjectName("spinBox_playerCount")
        self.pushButton_setUp = QtWidgets.QPushButton(self.groupBox_voterSetup)
        self.pushButton_setUp.setGeometry(QtCore.QRect(230, 5, 91, 40))
        self.pushButton_setUp.setObjectName("pushButton_setUp")
        self.label_Setup_Manual = QtWidgets.QLabel(self.centralwidget)
        self.label_Setup_Manual.setGeometry(QtCore.QRect(10, 90, 241, 31))
        self.label_Setup_Manual.setObjectName("label_Setup_Manual")
        self.label_Setup_StatusQuo = QtWidgets.QLabel(self.centralwidget)
        self.label_Setup_StatusQuo.setGeometry(QtCore.QRect(10, 300, 121, 31))
        self.label_Setup_StatusQuo.setObjectName("label_Setup_StatusQuo")
        self.groupBox_ManifestoAPI = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_ManifestoAPI.setGeometry(QtCore.QRect(350, 120, 311, 51))
        self.groupBox_ManifestoAPI.setTitle("")
        self.groupBox_ManifestoAPI.setObjectName("groupBox_ManifestoAPI")
        self.lineEdit_APIkey = QtWidgets.QLineEdit(self.groupBox_ManifestoAPI)
        self.lineEdit_APIkey.setGeometry(QtCore.QRect(10, 20, 181, 21))
        self.lineEdit_APIkey.setObjectName("lineEdit_APIkey")
        self.label_APIKey = QtWidgets.QLabel(self.groupBox_ManifestoAPI)
        self.label_APIKey.setGeometry(QtCore.QRect(10, 0, 81, 16))
        self.label_APIKey.setObjectName("label_APIKey")
        self.lineEdit_APIkey.setEchoMode(QtWidgets.QLineEdit.Password)
        self.pushButton_APIconnect = QtWidgets.QPushButton(self.groupBox_ManifestoAPI)
        self.pushButton_APIconnect.setGeometry(QtCore.QRect(210, 5, 91, 40))
        self.pushButton_APIconnect.setObjectName("pushButton_APIconnect")
        self.groupBox_ManifestoAPI2 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_ManifestoAPI2.setGeometry(QtCore.QRect(10, 200, 651, 101))
        self.groupBox_ManifestoAPI2.setTitle("")
        self.groupBox_ManifestoAPI2.setObjectName("groupBox_ManifestoAPI2")
        self.pushButton_APIadd = QtWidgets.QPushButton(self.groupBox_ManifestoAPI2)
        self.pushButton_APIadd.setGeometry(QtCore.QRect(550, 10, 91, 81))
        self.pushButton_APIadd.setObjectName("pushButton_APIadd")
        self.label_APIcountry = QtWidgets.QLabel(self.groupBox_ManifestoAPI2)
        self.label_APIcountry.setGeometry(QtCore.QRect(10, 0, 47, 16))
        self.label_APIcountry.setObjectName("label_APIcountry")
        self.label_APIparty = QtWidgets.QLabel(self.groupBox_ManifestoAPI2)
        self.label_APIparty.setGeometry(QtCore.QRect(170, 0, 31, 16))
        self.label_APIparty.setObjectName("label_APIparty")
        self.label_APIissue = QtWidgets.QLabel(self.groupBox_ManifestoAPI2)
        self.label_APIissue.setGeometry(QtCore.QRect(320, 0, 31, 16))
        self.label_APIissue.setObjectName("label_APIissue")
        self.label_APIyear = QtWidgets.QLabel(self.groupBox_ManifestoAPI2)
        self.label_APIyear.setGeometry(QtCore.QRect(450, 0, 31, 16))
        self.label_APIyear.setObjectName("label_APIyear")
        self.listWidget_APIcountry = QtWidgets.QListWidget(self.groupBox_ManifestoAPI2)
        self.listWidget_APIcountry.setGeometry(QtCore.QRect(10, 20, 151, 71))
        self.listWidget_APIcountry.setObjectName("listWidget_APIcountry")
        self.listWidget_APIcountry.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.listWidget_APIparty = QtWidgets.QListWidget(self.groupBox_ManifestoAPI2)
        self.listWidget_APIparty.setGeometry(QtCore.QRect(170, 20, 141, 71))
        self.listWidget_APIparty.setObjectName("listWidget_APIparty")
        self.listWidget_APIparty.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.listWidget_APIyear = QtWidgets.QListWidget(self.groupBox_ManifestoAPI2)
        self.listWidget_APIyear.setGeometry(QtCore.QRect(450, 20, 91, 71))
        self.listWidget_APIyear.setObjectName("listWidget_APIyear")
        self.listWidget_APIissue = QtWidgets.QListWidget(self.groupBox_ManifestoAPI2)
        self.listWidget_APIissue.setGeometry(QtCore.QRect(320, 20, 121, 71))
        self.listWidget_APIissue.setObjectName("listWidget_APIissue")
        self.listWidget_APIissue.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.label_Setup_Manifesto = QtWidgets.QLabel(self.centralwidget)
        self.label_Setup_Manifesto.setGeometry(QtCore.QRect(350, 90, 311, 31))
        self.label_Setup_Manifesto.setObjectName("label_Setup_Manifesto")
        self.label_Setup_VoterTable = QtWidgets.QLabel(self.centralwidget)
        self.label_Setup_VoterTable.setGeometry(QtCore.QRect(240, 300, 91, 31))
        self.label_Setup_VoterTable.setObjectName("label_Setup_VoterTable")
        self.groupBox_SQ = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_SQ.setGeometry(QtCore.QRect(10, 330, 171, 181))
        self.groupBox_SQ.setTitle("")
        self.groupBox_SQ.setObjectName("groupBox_SQ")
        self.tableWidget_StatusQuoPositions = QtWidgets.QTableWidget(self.groupBox_SQ)
        self.tableWidget_StatusQuoPositions.setGeometry(QtCore.QRect(10, 10, 151, 161))
        self.tableWidget_StatusQuoPositions.setRowCount(2)
        self.tableWidget_StatusQuoPositions.setColumnCount(2)
        self.tableWidget_StatusQuoPositions.setObjectName("tableWidget_StatusQuoPositions")
        self.tableWidget_StatusQuoPositions.horizontalHeader().setCascadingSectionResizes(False)
        self.tableWidget_StatusQuoPositions.horizontalHeader().setDefaultSectionSize(50)
        self.groupBox_Options = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_Options.setGeometry(QtCore.QRect(10, 540, 651, 161))
        self.groupBox_Options.setTitle("")
        self.groupBox_Options.setObjectName("groupBox_Options")
        self.radioButton_visualizeYes = QtWidgets.QRadioButton(self.groupBox_Options)
        self.radioButton_visualizeYes.setGeometry(QtCore.QRect(90, 20, 51, 17))
        self.radioButton_visualizeYes.setChecked(True)
        self.radioButton_visualizeYes.setObjectName("radioButton_visualizeYes")
        self.buttonGroup_3 = QtWidgets.QButtonGroup(MainWindow)
        self.buttonGroup_3.setObjectName("buttonGroup_3")
        self.buttonGroup_3.addButton(self.radioButton_visualizeYes)
        self.radioButton_visualizeNo = QtWidgets.QRadioButton(self.groupBox_Options)
        self.radioButton_visualizeNo.setGeometry(QtCore.QRect(140, 20, 41, 17))
        self.radioButton_visualizeNo.setObjectName("radioButton_visualizeNo")
        self.buttonGroup_3.addButton(self.radioButton_visualizeNo)
        self.label_visualize = QtWidgets.QLabel(self.groupBox_Options)
        self.label_visualize.setGeometry(QtCore.QRect(90, 0, 51, 16))
        self.label_visualize.setObjectName("label_visualize")
        self.radioButton_saveNo = QtWidgets.QRadioButton(self.groupBox_Options)
        self.radioButton_saveNo.setGeometry(QtCore.QRect(140, 70, 41, 17))
        self.radioButton_saveNo.setObjectName("radioButton_saveNo")
        self.buttonGroup_4 = QtWidgets.QButtonGroup(MainWindow)
        self.buttonGroup_4.setObjectName("buttonGroup_4")
        self.buttonGroup_4.addButton(self.radioButton_saveNo)
        self.radioButton_saveYes = QtWidgets.QRadioButton(self.groupBox_Options)
        self.radioButton_saveYes.setGeometry(QtCore.QRect(90, 70, 51, 17))
        self.radioButton_saveYes.setChecked(True)
        self.radioButton_saveYes.setObjectName("radioButton_saveYes")
        self.buttonGroup_4.addButton(self.radioButton_saveYes)
        self.label_saveResults = QtWidgets.QLabel(self.groupBox_Options)
        self.label_saveResults.setGeometry(QtCore.QRect(90, 50, 81, 16))
        self.label_saveResults.setObjectName("label_saveResults")
        self.label_dimensions = QtWidgets.QLabel(self.groupBox_Options)
        self.label_dimensions.setGeometry(QtCore.QRect(10, 50, 71, 16))
        self.label_dimensions.setObjectName("label_dimensions")
        self.label_breaks = QtWidgets.QLabel(self.groupBox_Options)
        self.label_breaks.setGeometry(QtCore.QRect(10, 0, 41, 16))
        self.label_breaks.setObjectName("label_breaks")
        self.doubleSpinBox_breaks = QtWidgets.QDoubleSpinBox(self.groupBox_Options)
        self.doubleSpinBox_breaks.setGeometry(QtCore.QRect(10, 20, 61, 22))
        self.doubleSpinBox_breaks.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.doubleSpinBox_breaks.setDecimals(4)
        self.doubleSpinBox_breaks.setSingleStep(0.0001)
        self.doubleSpinBox_breaks.setProperty("value", 0.01)
        self.doubleSpinBox_breaks.setObjectName("doubleSpinBox_breaks")
        self.label_runs = QtWidgets.QLabel(self.groupBox_Options)
        self.label_runs.setGeometry(QtCore.QRect(10, 100, 31, 16))
        self.label_runs.setObjectName("label_runs")
        self.spinBox_dimensions = QtWidgets.QSpinBox(self.groupBox_Options)
        self.spinBox_dimensions.setGeometry(QtCore.QRect(10, 70, 62, 22))
        self.spinBox_dimensions.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.spinBox_dimensions.setProperty("value", 2)
        self.spinBox_dimensions.setObjectName("spinBox_dimensions")
        self.spinBox_runs = QtWidgets.QSpinBox(self.groupBox_Options)
        self.spinBox_runs.setGeometry(QtCore.QRect(10, 120, 62, 22))
        self.spinBox_runs.setProperty("value", 1)
        self.spinBox_runs.setObjectName("spinBox_runs")
        self.label_alterPrefs = QtWidgets.QLabel(self.groupBox_Options)
        self.label_alterPrefs.setGeometry(QtCore.QRect(200, 0, 101, 16))
        self.label_alterPrefs.setObjectName("label_alterPrefs")
        self.radioButton_alterPrefsYes = QtWidgets.QRadioButton(self.groupBox_Options)
        self.radioButton_alterPrefsYes.setGeometry(QtCore.QRect(250, 20, 51, 17))
        self.radioButton_alterPrefsYes.setChecked(True)
        self.radioButton_alterPrefsYes.setObjectName("radioButton_alterPrefsYes")
        self.buttonGroup_5 = QtWidgets.QButtonGroup(MainWindow)
        self.buttonGroup_5.setObjectName("buttonGroup_5")
        self.buttonGroup_5.addButton(self.radioButton_alterPrefsYes)
        self.radioButtonalterPrefsNo = QtWidgets.QRadioButton(self.groupBox_Options)
        self.radioButtonalterPrefsNo.setGeometry(QtCore.QRect(200, 20, 41, 17))
        self.radioButtonalterPrefsNo.setObjectName("radioButtonalterPrefsNo")
        self.buttonGroup_5.addButton(self.radioButtonalterPrefsNo)
        self.buttonGroup_6 = QtWidgets.QButtonGroup(MainWindow)
        self.buttonGroup_6.setObjectName("buttonGroup_6")
        self.radioButton_distParetian_2 = QtWidgets.QRadioButton(self.groupBox_Options)
        self.radioButton_distParetian_2.setGeometry(QtCore.QRect(200, 110, 81, 17))
        self.radioButton_distParetian_2.setChecked(False)
        self.radioButton_distParetian_2.setObjectName("radioButton_distParetian_2")
        self.radioButton_distNormal_2 = QtWidgets.QRadioButton(self.groupBox_Options)
        self.radioButton_distNormal_2.setGeometry(QtCore.QRect(200, 70, 61, 17))
        self.radioButton_distNormal_2.setChecked(False)
        self.radioButton_distNormal_2.setObjectName("radioButton_distNormal_2")
        self.radioButton_distExponential_2 = QtWidgets.QRadioButton(self.groupBox_Options)
        self.radioButton_distExponential_2.setGeometry(QtCore.QRect(200, 130, 121, 17))
        self.radioButton_distExponential_2.setChecked(True)
        self.radioButton_distExponential_2.setObjectName("radioButton_distExponential_2")
        self.radioButton_distExponential_2.setChecked(True)
        self.radioButton_distUniform_2 = QtWidgets.QRadioButton(self.groupBox_Options)
        self.radioButton_distUniform_2.setGeometry(QtCore.QRect(200, 90, 61, 17))
        self.radioButton_distUniform_2.setObjectName("radioButton_distUniform_2")
        self.buttonGroup_6.addButton(self.radioButton_distParetian_2)
        self.buttonGroup_6.addButton(self.radioButton_distNormal_2)
        self.buttonGroup_6.addButton(self.radioButton_distExponential_2)
        self.buttonGroup_6.addButton(self.radioButton_distUniform_2)
        self.label_AlterStatusQuo = QtWidgets.QLabel(self.groupBox_Options)
        self.label_AlterStatusQuo.setGeometry(QtCore.QRect(200, 50, 101, 16))
        self.label_AlterStatusQuo.setObjectName("label_AlterStatusQuo")
        self.radioButton_distanceManh = QtWidgets.QRadioButton(self.groupBox_Options)
        self.radioButton_distanceManh.setGeometry(QtCore.QRect(320, 100, 111, 17))
        self.radioButton_distanceManh.setObjectName("radioButton_distanceManh")
        self.buttonGroup_2 = QtWidgets.QButtonGroup(MainWindow)
        self.buttonGroup_2.setObjectName("buttonGroup_2")
        self.buttonGroup_2.addButton(self.radioButton_distanceManh)
        self.radioButton_distancePyth = QtWidgets.QRadioButton(self.groupBox_Options)
        self.radioButton_distancePyth.setGeometry(QtCore.QRect(320, 80, 101, 17))
        self.radioButton_distancePyth.setChecked(True)
        self.radioButton_distancePyth.setObjectName("radioButton_distancePyth")
        self.buttonGroup_2.addButton(self.radioButton_distancePyth)
        self.label_distanceType = QtWidgets.QLabel(self.groupBox_Options)
        self.label_distanceType.setGeometry(QtCore.QRect(320, 60, 91, 16))
        self.label_distanceType.setObjectName("label_distanceType")
        self.radioButton_distParetian = QtWidgets.QRadioButton(self.groupBox_Options)
        self.radioButton_distParetian.setGeometry(QtCore.QRect(390, 20, 71, 17))
        self.radioButton_distParetian.setChecked(False)
        self.radioButton_distParetian.setObjectName("radioButton_distParetian")
        self.buttonGroup = QtWidgets.QButtonGroup(MainWindow)
        self.buttonGroup.setObjectName("buttonGroup")
        self.buttonGroup.addButton(self.radioButton_distParetian)
        self.radioButton_distUniform = QtWidgets.QRadioButton(self.groupBox_Options)
        self.radioButton_distUniform.setGeometry(QtCore.QRect(320, 40, 71, 17))
        self.radioButton_distUniform.setObjectName("radioButton_distUniform")
        self.buttonGroup.addButton(self.radioButton_distUniform)
        self.radioButton_distExponential = QtWidgets.QRadioButton(self.groupBox_Options)
        self.radioButton_distExponential.setGeometry(QtCore.QRect(390, 40, 91, 17))
        self.radioButton_distExponential.setObjectName("radioButton_distExponential")
        self.buttonGroup.addButton(self.radioButton_distExponential)
        self.radioButton_distNormal = QtWidgets.QRadioButton(self.groupBox_Options)
        self.radioButton_distNormal.setGeometry(QtCore.QRect(320, 20, 71, 17))
        self.radioButton_distNormal.setChecked(True)
        self.radioButton_distNormal.setObjectName("radioButton_distNormal")
        self.buttonGroup.addButton(self.radioButton_distNormal)
        self.label_distribution = QtWidgets.QLabel(self.groupBox_Options)
        self.label_distribution.setGeometry(QtCore.QRect(320, 0, 71, 16))
        self.label_distribution.setObjectName("label_distribution")
        self.label_outputFolder = QtWidgets.QLabel(self.groupBox_Options)
        self.label_outputFolder.setGeometry(QtCore.QRect(480, 100, 81, 16))
        self.label_outputFolder.setObjectName("label_outputFolder")
        self.lineEdit_OutputDir = QtWidgets.QLineEdit(self.groupBox_Options)
        self.lineEdit_OutputDir.setGeometry(QtCore.QRect(480, 120, 121, 20))
        self.lineEdit_OutputDir.setObjectName("lineEdit_OutputDir")
        self.pushButton_OutputCD = QtWidgets.QPushButton(self.groupBox_Options)
        self.pushButton_OutputCD.setGeometry(QtCore.QRect(600, 120, 41, 20))
        self.pushButton_OutputCD.setObjectName("pushButton_OutputCD")
        self.label_LoadSettings = QtWidgets.QLabel(self.groupBox_Options)
        self.label_LoadSettings.setGeometry(QtCore.QRect(480, 0, 81, 16))
        self.label_LoadSettings.setObjectName("label_LoadSettings")
        self.lineEdit_loadSettingsDir = QtWidgets.QLineEdit(self.groupBox_Options)
        self.lineEdit_loadSettingsDir.setGeometry(QtCore.QRect(480, 20, 121, 20))
        self.lineEdit_loadSettingsDir.setObjectName("lineEdit_loadSettingsDir")
        self.pushButton_loadSettingsCD = QtWidgets.QPushButton(self.groupBox_Options)
        self.pushButton_loadSettingsCD.setGeometry(QtCore.QRect(600, 20, 41, 20))
        self.pushButton_loadSettingsCD.setObjectName("pushButton_loadSettingsCD")
        self.graph_trace_no = QtWidgets.QRadioButton(self.groupBox_Options)
        self.graph_trace_no.setGeometry(QtCore.QRect(140, 120, 51, 20))
        self.graph_trace_no.setChecked(False)
        self.graph_trace_no.setObjectName("graph_trace_no")
        self.buttonGroup_7 = QtWidgets.QButtonGroup(MainWindow)
        self.buttonGroup_7.setObjectName("buttonGroup_7")
        self.buttonGroup_7.addButton(self.graph_trace_no)
        self.graph_trace_yes = QtWidgets.QRadioButton(self.groupBox_Options)
        self.graph_trace_yes.setGeometry(QtCore.QRect(90, 120, 51, 20))
        self.graph_trace_yes.setChecked(True)
        self.graph_trace_yes.setObjectName("graph_trace_yes")
        self.buttonGroup_7.addButton(self.graph_trace_yes)
        self.label_saveResults_2 = QtWidgets.QLabel(self.groupBox_Options)
        self.label_saveResults_2.setGeometry(QtCore.QRect(90, 100, 91, 16))
        self.label_saveResults_2.setObjectName("label_saveResults_2")
        self.label_sequenceFolder = QtWidgets.QLabel(self.groupBox_Options)
        self.label_sequenceFolder.setGeometry(QtCore.QRect(480, 50, 91, 16))
        self.label_sequenceFolder.setObjectName("label_sequenceFolder")
        self.lineEdit_sequenceDir = QtWidgets.QLineEdit(self.groupBox_Options)
        self.lineEdit_sequenceDir.setGeometry(QtCore.QRect(480, 70, 121, 20))
        self.lineEdit_sequenceDir.setObjectName("lineEdit_sequenceDir")
        self.pushButton_SequenceCD = QtWidgets.QPushButton(self.groupBox_Options)
        self.pushButton_SequenceCD.setGeometry(QtCore.QRect(600, 70, 41, 20))
        self.pushButton_SequenceCD.setObjectName("pushButton_SequenceCD")
        self.radioButton_visualizeYes.raise_()
        self.radioButton_visualizeNo.raise_()
        self.label_visualize.raise_()
        self.radioButton_saveNo.raise_()
        self.radioButton_saveYes.raise_()
        self.label_saveResults.raise_()
        self.label_dimensions.raise_()
        self.label_breaks.raise_()
        self.doubleSpinBox_breaks.raise_()
        self.label_runs.raise_()
        self.spinBox_dimensions.raise_()
        self.spinBox_runs.raise_()
        self.label_alterPrefs.raise_()
        self.radioButton_alterPrefsYes.raise_()
        self.radioButtonalterPrefsNo.raise_()
        self.radioButton_distParetian_2.raise_()
        self.radioButton_distNormal_2.raise_()
        self.radioButton_distExponential_2.raise_()
        self.label_AlterStatusQuo.raise_()
        self.radioButton_distUniform_2.raise_()
        self.radioButton_distanceManh.raise_()
        self.radioButton_distancePyth.raise_()
        self.label_distanceType.raise_()
        self.radioButton_distParetian.raise_()
        self.radioButton_distUniform.raise_()
        self.radioButton_distExponential.raise_()
        self.radioButton_distNormal.raise_()
        self.label_distribution.raise_()
        self.label_outputFolder.raise_()
        self.lineEdit_OutputDir.raise_()
        self.pushButton_OutputCD.raise_()
        self.label_LoadSettings.raise_()
        self.lineEdit_loadSettingsDir.raise_()
        self.pushButton_loadSettingsCD.raise_()
        self.graph_trace_no.raise_()
        self.graph_trace_yes.raise_()
        self.label_saveResults_2.raise_()
        self.label_sequenceFolder.raise_()
        self.lineEdit_sequenceDir.raise_()
        self.pushButton_SequenceCD.raise_()
        self.label_Setup_Options = QtWidgets.QLabel(self.centralwidget)
        self.label_Setup_Options.setGeometry(QtCore.QRect(10, 510, 81, 31))
        self.label_Setup_Options.setObjectName("label_Setup_Options")
        self.pushButton_runSim = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_runSim.setGeometry(QtCore.QRect(340, 710, 321, 101))
        self.pushButton_runSim.setObjectName("pushButton_runSim")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(340, 310, 41, 20))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(190, 310, 41, 20))
        self.pushButton_2.setObjectName("pushButton_2")
        self.logConsole = QtWidgets.QTextEdit(self.centralwidget)
        self.logConsole.setGeometry(QtCore.QRect(10, 710, 321, 101))
        self.logConsole.setObjectName("logConsole")
        self.label_Setup_Manifesto_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_Setup_Manifesto_2.setGeometry(QtCore.QRect(10, 170, 311, 31))
        self.label_Setup_Manifesto_2.setObjectName("label_Setup_Manifesto_2")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 682, 26))
        self.menubar.setObjectName("menubar")
        self.menuAbout = QtWidgets.QMenu(self.menubar)
        self.menuAbout.setObjectName("menuAbout")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar.addAction(self.menuAbout.menuAction())

        self.retranslateUi(MainWindow)
        self.stackedWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
        #%%
        # var inits, button connects
        self.logConsole.append('LOG\n-----')
        
        self.status_quo_table_set = False
                
        self.APIconnected = False
        
        self.var_save_dir = None
        
        self.pushButton_setUp.clicked.connect(self.VoterSetup)
        self.pushButton_APIadd.clicked.connect(lambda: self.VoterSetup(manifesto = True))
        
        self.pushButton_APIconnect.clicked.connect(self.manifestoAPI_connect)

        self.lineEdit_loadSettingsDir.setDisabled(True)
        self.lineEdit_OutputDir.setDisabled(True)
        self.lineEdit_sequenceDir.setDisabled(True)
        self.pushButton_OutputCD.clicked.connect(self.selectDirectory)
        self.pushButton_loadSettingsCD.clicked.connect(self.loadSettings)
        self.pushButton_SequenceCD.clicked.connect(self.loadCustomSequences)
        
        self.pushButton_2.clicked.connect(lambda: self.StackedWidgetPages(0))
        self.pushButton.clicked.connect(lambda: self.StackedWidgetPages(1))
        
        self.stackedWidgetIndex = 0
        self.stackedWidgetLabels = ['Voters', 'Positions', 'Drift']
        
        self.stackedWidget.setCurrentIndex(self.stackedWidgetIndex)
        
        self.tableWidget_votersOverview.setColumnCount(3)
        self.headerNames_Overview = ['Name', 'Agenda Setter', 'Veto Player']
        self.tableWidget_votersOverview.setHorizontalHeaderLabels(self.headerNames_Overview)
        
        self.pushButton_runSim.clicked.connect(self.runSimulation)
        
        #%%
        self.spinBox_dimensions.valueChanged.connect(self.changeDimensions)
        
        #%%
        # api list widget signals
        self.listWidget_APIcountry.itemDoubleClicked.connect(self.manifestoAPI_country)   
        
        self.listWidget_APIparty.selectionModel().selectionChanged.connect(self.manifestoAPI_addissues)
        
        self.listWidget_APIissue.selectionModel().selectionChanged.connect(self.manifestoAPI_addyears)
        
        self.listWidget_APIyear.selectionModel().selectionChanged.connect(self.manifestoAPI_year)
        
        #%%
        #table widget inits
        dimensions = self.spinBox_dimensions.value()
        
        self.tableWidget_votersOverview.setColumnCount(3)
        self.headerNames_Overview = ['Name', 'Agenda Setter', 'Veto Player']
        self.tableWidget_votersOverview.setHorizontalHeaderLabels(self.headerNames_Overview)
        
        dimensions = self.spinBox_dimensions.value()
        voterposition_h_headers = ['Dimension ' + str(i + 1) for i in range(dimensions)]
            
        self.tableWidget_VotersPositions.setColumnCount(dimensions)
        self.tableWidget_VotersPositions.setHorizontalHeaderLabels(voterposition_h_headers)

        self.tableWidget_VotersDrift.setColumnCount(dimensions)
        self.tableWidget_VotersDrift.setHorizontalHeaderLabels(voterposition_h_headers)
        
        self.tableWidget_StatusQuoPositions.setColumnCount(dimensions)
        self.tableWidget_StatusQuoPositions.setHorizontalHeaderLabels(['Dim ' + str(dim + 1) for dim in range(dimensions)])

        for i in range(2):
            rowPosition = self.tableWidget_StatusQuoPositions.rowCount()
            self.tableWidget_StatusQuoPositions.insertRow(rowPosition)
        
        self.tableWidget_StatusQuoPositions.setVerticalHeaderLabels(['Position', 'Drift'])
        
        self.custom_sequence = False
        self.custom_role_array = False
        self.randomize_as = False
        self.randomize_veto = False
        #%%
        
    def manifestoAPI_year(self):
        '''
        Get the year selected in the Manifesto API list widget
        '''
        self.year = self.listWidget_APIyear.currentItem().text()
        
        
    def manifestoAPI_addyears(self):
        '''
        Add years for which datasets are available for the given party/parties
        to the Manifesto API list widget
        '''
        self.listWidget_APIyear.clear()
        self.issue_selection = [item.text() for item in self.listWidget_APIissue.selectedItems()]
        self.listWidget_APIyear.addItems([str(item)[:10] for item in list(
                self.manifesto_maindf[['edate'] + self.issue_selection][self.manifesto_maindf['partyname'].isin(self.party_selection)].
                dropna(axis = 0, how = 'any').iloc[:, 0])])
    
    def manifestoAPI_addissues(self):
        '''
        Add issues for which datasets are available for the given party/parties
        to the Manifesto API list widget
        '''
        self.listWidget_APIissue.clear()
        self.party_selection = [item.text() for item in self.listWidget_APIparty.selectedItems()]

        self.listWidget_APIissue.addItems(list(
                self.manifesto_maindf.loc[(self.manifesto_maindf['partyname'].isin(self.party_selection))].
                dropna(how = 'any', axis = 1).iloc[:, 25:-1]))
        
    def manifestoAPI_country(self, item):
        '''
        Add countries for which datasets are available to the Manifesto API list widget
        '''
        self.listWidget_APIparty.clear()
        self.country = item.text()
        self.listWidget_APIparty.addItems(list(
                self.manifesto_maindf['partyname'][self.manifesto_maindf['countryname'] == self.country].sort_values().unique()))
        
    def manifestoAPI_connect(self):
        '''
        Connect to the Manifesto Project API via manifestoPY and load the main dataset
        '''
        import manifestoPY
        key = self.lineEdit_APIkey.text()
        
        try:
            manifesto = manifestoPY.Manifesto(key)
            self.APIconnected = True
            logging.info('Connected to Manifesto API')
        except:
            logging.error('Request Error – Check API Key')
            raise
            
        try:
            self.manifesto_maindf = manifesto.mp_maindataset()
        except:
            logging.error('Request Error – Error when accessing main dataset')
            raise
            
        self.listWidget_APIcountry.addItems(list(self.manifesto_maindf['countryname'].sort_values().unique()))
    

    def StackedWidgetPages(self, direction):
        '''
        Stores the index (page nr) and displays the current page
        of the stacked widget which is central to the GUI
        '''
        if direction == 0:
            self.stackedWidgetIndex -= 1
            
            if self.stackedWidgetIndex < 0:
                self.stackedWidgetIndex = 0
            
        elif direction == 1:
            self.stackedWidgetIndex += 1
            
            if self.stackedWidgetIndex > 2:
                self.stackedWidgetIndex = 2

        self.stackedWidget.setCurrentIndex(self.stackedWidgetIndex)
        self.label_Setup_VoterTable.setText(self.stackedWidgetLabels[self.stackedWidgetIndex])
        self.label_Setup_VoterTable.setStyleSheet('QLabel#label_Setup_VoterTable {font-size: 12pt; font-weight: 600}')
        
        
    def changeDimensions(self):
        '''
        Alter the table widgets of voters and status quo 
        depending on the dimension count
        '''
        dimensions = self.spinBox_dimensions.value()
        
        self.tableWidget_StatusQuoPositions.setColumnCount(dimensions)
        self.tableWidget_StatusQuoPositions.setHorizontalHeaderLabels(['Dim ' + str(dim + 1) for dim in range(dimensions)])
        
        voterposition_h_headers = ['Dimension ' + str(i + 1) for i in range(dimensions)]
        
        self.tableWidget_VotersPositions.setColumnCount(dimensions)
        self.tableWidget_VotersPositions.setHorizontalHeaderLabels(voterposition_h_headers)

        self.tableWidget_VotersDrift.setColumnCount(dimensions)
        self.tableWidget_VotersDrift.setHorizontalHeaderLabels(voterposition_h_headers)
        
        
    def toBool(self, string):
        '''
        Convert strings to boolean
        '''
        if string == 'True' or string == '1' or string == 'Yes':
             return True
         
        elif string == 'False' or string == '0' or string == 'No':
             return False
         
        else:
             raise ValueError
             
    
    def create_dir(self, directory):
        '''
        Create directory if needed.
        '''
        try:
            os.makedirs(directory)
        except OSError as e:
            if e.errno != errno.EEXIST:
                logging.error('Failed to create directory {0}'.format(directory))
                raise
                
                
    def resultsDir(self, model_number, number_dimensions, runs, parent_dir):
        '''
        Create a directory for the simulation results
        '''
        timestr = time.strftime("%Y-%m-%d_%H%M")
    
        foldername = ''.join(('results', '-', str(model_number), '-', str(number_dimensions), '-', str(runs), '__', timestr))

        results_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), parent_dir, foldername)
        self.create_dir(results_dir)
        return results_dir
                
             
    def setModelNumber(self, alter_status_quo, alter_preferences):    
        '''
        This function sets the model number of the simulation. It is only used for classifying the model
        in the csv.
        '''
        if alter_status_quo == 'no':
            return 0
        
        elif alter_status_quo == 'random':
            return 1
        
        elif alter_status_quo == 'history':
            return 2
        
        elif alter_status_quo == 'history + drift' and alter_preferences == 'no':
            return 3
        
        elif alter_status_quo == 'history + drift' and alter_preferences == 'drift':
            return 4
        
        else:
            return 'NA'
        

    def VoterSetup(self, manifesto = False, load = False):
        '''
        Add voters to the table widgets based on the number of players
        
        '''
        if manifesto is False:          
            for table in [self.tableWidget_VotersDrift, self.tableWidget_votersOverview, self.tableWidget_VotersPositions]:
                table.setRowCount(0)
                
            voterCount = self.spinBox_voterCount.value()
            vetoCount = self.spinBox_playerCount.value()

            data = []
            
            for i in range(voterCount):
                if i == 0:
                    data.append(['', 'True', 'False'])
                
                elif vetoCount != 0 and i in range(1, vetoCount + 1):
                        data.append(['', 'False', 'True'])
                        
                else:
                    data.append(['', 'False', 'False'])
            
            for item in data:
                rowPosition = self.tableWidget_votersOverview.rowCount()
                self.tableWidget_votersOverview.insertRow(rowPosition)
        
                [self.tableWidget_votersOverview.setItem(rowPosition, p, QtWidgets.QTableWidgetItem(it)) for p, it in enumerate(item)]

#            dimensions = self.spinBox_dimensions.value()
#            voterposition_h_headers = ['Dimension ' + str(i + 1) for i in range(dimensions)]
#            
#            self.tableWidget_VotersPositions.setColumnCount(dimensions)
#            self.tableWidget_VotersPositions.setHorizontalHeaderLabels(voterposition_h_headers)
#
            for i in range(voterCount):
                rowPosition = self.tableWidget_VotersPositions.rowCount()
                self.tableWidget_VotersPositions.insertRow(rowPosition)
#        
#            self.tableWidget_VotersDrift.setColumnCount(dimensions)
#            self.tableWidget_VotersDrift.setHorizontalHeaderLabels(voterposition_h_headers)
#            
            for i in range(voterCount):
                rowPosition = self.tableWidget_VotersDrift.rowCount()
                self.tableWidget_VotersDrift.insertRow(rowPosition)
#                
#            self.tableWidget_StatusQuoPositions.setColumnCount(dimensions)
#            self.tableWidget_StatusQuoPositions.setHorizontalHeaderLabels(['Dim ' + str(dim + 1) for dim in range(dimensions)])
#            
#            for i in range(2):
#                rowPosition = self.tableWidget_StatusQuoPositions.rowCount()
#                self.tableWidget_StatusQuoPositions.insertRow(rowPosition)
            
            v_headers = ['Voter ' + str(i + 1) for i in range(voterCount)]
            
            self.tableWidget_VotersDrift.verticalHeader().show()
            self.tableWidget_votersOverview.verticalHeader().show()
            self.tableWidget_VotersPositions.verticalHeader().show()
            self.tableWidget_StatusQuoPositions.verticalHeader().show()
            
            self.tableWidget_VotersPositions.setVerticalHeaderLabels(v_headers)
            self.tableWidget_VotersDrift.setVerticalHeaderLabels(v_headers)
            self.tableWidget_votersOverview.setVerticalHeaderLabels(v_headers)
            
            logging.info('{0} Voters, including {1} Veto Players added'.format(voterCount, vetoCount))
            
        if manifesto is True:
            if self.APIconnected is False:
                return
            
            for party in self.party_selection:
                rowPosition = self.tableWidget_votersOverview.rowCount()
                self.tableWidget_votersOverview.insertRow(rowPosition)
                
                [self.tableWidget_votersOverview.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(
                        party + ' (' + self.country + ')'))]
            
                rowPosition = self.tableWidget_VotersPositions.rowCount()
                self.tableWidget_VotersPositions.insertRow(rowPosition)
                
                [self.tableWidget_VotersPositions.setItem(rowPosition, i, QtWidgets.QTableWidgetItem(str(
                        self.manifesto_maindf[issue][(self.manifesto_maindf['partyname'] == party) & 
                                             (self.manifesto_maindf['edate'] == self.year)].iloc[0]))) for i, issue in enumerate(self.issue_selection)]
                        
            
    def selectDirectory(self):
        '''
        Get folder name
        '''
        self.var_save_dir = self.lineEdit_OutputDir.setText(QtWidgets.QFileDialog.getExistingDirectory())
        

    def readValues(self):
        '''
        Store the table widget data and chosen settings in var.py
        '''
        voterCount = self.tableWidget_votersOverview.rowCount()
        dimensions = self.spinBox_dimensions.value()
        
        try:
            var.status_quo = [float(self.tableWidget_StatusQuoPositions.item(0, dim).text()) for
                              dim in range(dimensions)]
            
        except:
            logging.error('Value Error – Invalid Status Quo Position')
            raise
            
        try:
            var.driftStatusQuo = [float(self.tableWidget_StatusQuoPositions.item(1, dim).text()) for
                                  dim in range(dimensions)]
        except:
            if not self.radioButton_distExponential_2.isChecked():
                pass
            else:
                logging.error('Value Error – Invalid Status Quo Position')
                raise
            ##TODO ^fix namepsace
        var.voters['voter_names'] = [self.tableWidget_votersOverview.item(row, 0).text() for
                  row in range(voterCount)]
        
        try:
            var.voters['voter_agendasetter'] = [self.toBool(self.tableWidget_votersOverview.item(row, 1).text()) for row in range(voterCount)]
            var.voters['voter_vetoplayer'] = [self.toBool(self.tableWidget_votersOverview.item(row, 2).text()) for row in range(voterCount)]
            
            if sum(var.voters['voter_agendasetter']) == 0:
                logging.error('Input Error. There must be at least 1 Agenda Setter')
                raise
            
            elif sum(var.voters['voter_agendasetter']) > 1:
                logging.error('Input Error. There can only be 1 Agenda Setter')
                raise
            
        except:
            logging.error('Wrong Agenda Setter / Veto Player Input. Use Booleans (True / False or 1 / 0)')
            raise
        
        try:
            var.voters['voter_positions'] = [[float(self.tableWidget_VotersPositions.item(row, dim).text()) for dim in
                      range(dimensions)] for row in range(voterCount)]
            
        except:
            logging.error('Value Error – Invalid Voter Position')
            raise
            
        try:
            var.voters['voter_drift'] = [[float(self.tableWidget_VotersDrift.item(row, dim).text()) for dim in
                      range(dimensions)] for row in range(voterCount)]
        except:
            if self.radioButtonalterPrefsNo.isChecked():
                pass
            else:
                logging.error('Value Error – Invalid Drift Value')
                raise
            
        var.runs = self.spinBox_runs.value()
        var.breaks = self.doubleSpinBox_breaks.value()
        var.number_dimensions = dimensions
        
        var.trace = self.toBool(self.buttonGroup_7.checkedButton().text())
        
        var.alter_status_quo = self.buttonGroup_6.checkedButton().text().lower()
        var.alterPreferences = self.buttonGroup_5.checkedButton().text().lower()
        
        if self.radioButton_visualizeYes.isChecked():
            var.visualize = True
        else:
            var.visualize = False
            
        if self.radioButton_saveYes.isChecked():
            var.saveResults = True
            
        else:
            var.saveResults = False
            
        var.distribution = self.buttonGroup.checkedButton().text().lower()
        
        if self.radioButton_distancePyth.isChecked():
            var.distance_type = 'euclidean'
        else:
            var.distance_type = 'manhattan'
                    
        if var.saveResults is True or var.visualize is True:            
            var.model_number = self.setModelNumber(var.alter_status_quo, var.alterPreferences)
            
            if self.var_save_dir is None:
                parent_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'RESULTS')
                self.create_dir(parent_dir)
                results_dir = self.resultsDir(var.model_number, var.number_dimensions, var.runs, parent_dir)
                self.var_save_dir = results_dir
                
            self.saveSettings(voterCount, dimensions)

            var.directory = self.var_save_dir
            logging.info('Output Directory: {0}'.format(self.var_save_dir))
            
        if var.visualize is True and var.number_dimensions > 3:
            logging.info('Visualization not possible for games with > 3 dimensions')
            var.visualize = False
                            
        var.custom_sequence = self.custom_sequence
        var.custom_role_array = self.custom_role_array
        
        if var.custom_sequence is True:
            var.randomize_as = self.randomize_as
            var.randomize_veto = self.randomize_veto
            
        elif var.custom_role_array is True:
            var.role_array = self.role_array
              
        logging.info('All values read')
        logging.info('Voter Names: {0}\nVoter Positions: {1}\nVoter Drift: {2}\nStatus Quo: {3}'.format(var.voters['voter_names'],
                     var.voters['voter_positions'], var.voters['voter_drift'], var.status_quo))
        
        
    def runSimulation(self):
        '''
        Run the simulation (vetoboxing.py) 
        '''
        self.readValues()
        sim = vb_simulation.Simulation()
        sim.run()
        

    def loadSettings(self):
        '''
        Load voter settings in json format
        '''
        file = QtWidgets.QFileDialog.getOpenFileName(filter = 'Text Files (*.txt)')
        
        try:
            with open(file[0]) as config:
                settings = json.load(config)
        except:
            logging.error('Failed to load settings')
            raise

        try:
            if settings['settings']['AlterPreferences'] == 'No':
                self.radioButtonalterPrefsNo.setChecked(True)
            else:
                self.radioButton_alterPrefsYes.setChecked(True)
                
            if settings['settings']['AlterStatusQuo'] == 'No':
                self.radioButton_distNormal_2.setChecked(True)
            
            elif settings['settings']['AlterStatusQuo'] == 'Random':
                self.radioButton_distParetian_2.setChecked(True)
                
            elif settings['settings']['AlterStatusQuo'] == 'History':
                self.radioButton_distUniform_2.setChecked(True)
                
            else: 
                self.radioButton_distExponential_2.setChecked(True)
                
            self.doubleSpinBox_breaks.setValue(float(settings['settings']['Breaks']))
            
            self.spinBox_dimensions.setValue(int(settings['settings']['Dimensions']))
            
            self.spinBox_runs.setValue(int(settings['settings']['Runs']))
            
            if settings['settings']['DistanceType'] == 'Pythagorean':
                self.radioButton_distancePyth.setChecked(True)
            
            else:
                self.radioButton_distanceManh.setChecked(True)
                
            if settings['settings']['Distribution'] == 'Normal':
                self.radioButton_distNormal.setChecked(True)
            
            elif settings['settings']['Distribution'] == 'Paretian':
                self.radioButton_distParetian.setChecked(True)
            
            elif settings['settings']['Distribution'] == 'Uniform':
                self.radioButton_distUniform.setChecked(True)
                
            else:
                self.radioButton_distExponential.setChecked(True)
                
            if settings['settings']['Visualize'] == 'Yes':
                self.radioButton_visualizeYes.setChecked(True)
                
            else:
                self.radioButton_visualizeNo.setChecked(True)
                
            if settings['settings']['Save'] is True:
                self.radioButton_saveYes.setChecked(True)
            
            else:
                self.radioButton_saveNo.setChecked(True)
                
            for table in [self.tableWidget_VotersDrift, self.tableWidget_votersOverview, self.tableWidget_VotersPositions]:
                table.setRowCount(0)
                
            for voter in range(len(settings['voters']['names'])):
                rowPosition = self.tableWidget_votersOverview.rowCount()
                self.tableWidget_votersOverview.insertRow(rowPosition)
                
                [self.tableWidget_votersOverview.setItem(rowPosition, p, QtWidgets.QTableWidgetItem(item)) for
                 p, item in enumerate([settings['voters']['names'][voter], 
                                       settings['voters']['agendasetter'][voter],
                                       settings['voters']['vetoplayer'][voter]])]
                
                rowPosition = self.tableWidget_VotersPositions.rowCount()
                self.tableWidget_VotersPositions.insertRow(rowPosition)
                
                [self.tableWidget_VotersPositions.setItem(rowPosition, p, QtWidgets.QTableWidgetItem(item)) for
                 p, item in enumerate(settings['voters']['positions'][voter])]
#                
                rowPosition = self.tableWidget_VotersDrift.rowCount()
                self.tableWidget_VotersDrift.insertRow(rowPosition)
                
                [self.tableWidget_VotersDrift.setItem(rowPosition, p, QtWidgets.QTableWidgetItem(item)) for
                 p, item in enumerate(settings['voters']['drift'][voter])]
            
            [self.tableWidget_StatusQuoPositions.setItem(0, p, QtWidgets.QTableWidgetItem(item)) for
             p, item in enumerate(settings['status_quo']['position'])]
            
            [self.tableWidget_StatusQuoPositions.setItem(1, p, QtWidgets.QTableWidgetItem(item)) for
             p, item in enumerate(settings['status_quo']['drift'])]
            
            if 'sequence' in settings['voters']:
                self.sequence = settings['voters']['sequence']
                logging.info('Custom Sequence added')
                      
        except:
            logging.error('Failed to read config.txt')
                    

    def saveSettings(self, voterCount, dimensions):
        ###create dir/file
        '''
        Save current settings and voter setup
        '''
        save = {
                'settings' : {
                          'AlterPreferences' : self.buttonGroup_5.checkedButton().text(),
                          'AlterStatusQuo' : self.buttonGroup_6.checkedButton().text(),
                          'Breaks' : str(self.doubleSpinBox_breaks.value()),
                          'Dimensions' : str(self.spinBox_dimensions.value()),
                          'Runs' : str(self.spinBox_runs.value()),
                          'DistanceType' : self.buttonGroup_2.checkedButton().text(),
                          'Distribution' : self.buttonGroup.checkedButton().text(),
                          'Visualize' : self.buttonGroup_3.checkedButton().text(),
                          'Save' : True
                          },
                'voters' : {
                        'names' : [self.tableWidget_votersOverview.item(row, 0).text() for
                                   row in range(voterCount)],
                        'agendasetter' : [self.tableWidget_votersOverview.item(row, 1).text() for 
                                          row in range(voterCount)],
                        'vetoplayer' : [self.tableWidget_votersOverview.item(row, 2).text() for 
                                        row in range(voterCount)],
                        'positions' : [[self.tableWidget_VotersPositions.item(row, dim).text() for 
                                        dim in range(dimensions)] for row in range(voterCount)],
                        'drift' : [[self.tableWidget_VotersDrift.item(row, dim).text() for 
                                    dim in range(dimensions)] for row in range(voterCount)]
                        },
                'status_quo' : {
                        'position' : [self.tableWidget_StatusQuoPositions.item(0, dim).text() for
                              dim in range(dimensions)],
                        'drift' : [self.tableWidget_StatusQuoPositions.item(1, dim).text() for
                                  dim in range(dimensions)]
                        }
                }
                
        with open(os.path.join(self.var_save_dir, 'config.txt'), 'w') as f:
            json.dump(save, f)
            
    
    def loadCustomSequences(self):
        '''
        Load custom sequence (which is a custom voter_role_array) from json file
        '''
        file = QtWidgets.QFileDialog.getOpenFileName(filter = 'Text Files (*.txt)')
        
        try:
            with open(file[0]) as sequence:
                seq = json.load(sequence)
        except:
            logging.error('Failed to load sequence')
            raise
            
        try:     
            if any(rand in seq['sequence'] for rand in ['randomize_as', 'randomize_veto']):                
                self.custom_sequence = True
                
                if 'randomize_as' in seq['sequence']:
                    self.randomize_as = True
                    
                if 'randomize_veto' in seq['sequence']:
                    self.randomize_veto = True
            else:
                self.custom_role_array = True
                self.role_array = seq['sequence']        
                   
        except:
            logging.error('Failed to read sequence')
            raise
        
        

    
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
#        self.label_logo.setText(_translate("MainWindow", "<html><head/><body><p><img src=\":/logo/vetoboxing.png\"/></p></body></html>"))
        self.label_voterCount.setText(_translate("MainWindow", "Voter Count"))
        self.spinBox_voterCount.setToolTip(_translate("MainWindow", "Voter Count"))
        self.label_vetoCount.setText(_translate("MainWindow", "Veto Player Count"))
        self.spinBox_playerCount.setToolTip(_translate("MainWindow", "Veto Player Count"))
        self.pushButton_setUp.setText(_translate("MainWindow", "Setup"))
        self.label_Setup_Manual.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">Setup Voters – Manual</span></p></body></html>"))
        self.label_Setup_StatusQuo.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">Status Quo</span></p></body></html>"))
        self.lineEdit_APIkey.setToolTip(_translate("MainWindow", "API key from Manifesto Project profile"))
        self.label_APIKey.setText(_translate("MainWindow", "API Key"))
        self.pushButton_APIconnect.setText(_translate("MainWindow", "Connect"))
        self.pushButton_APIadd.setText(_translate("MainWindow", "Add"))
        self.label_APIcountry.setText(_translate("MainWindow", "Country"))
        self.label_APIparty.setText(_translate("MainWindow", "Party"))
        self.label_APIissue.setText(_translate("MainWindow", "Issue"))
        self.label_APIyear.setText(_translate("MainWindow", "Year"))
        self.label_Setup_Manifesto.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">Setup Voters – Manifesto API</span></p></body></html>"))
        self.label_Setup_VoterTable.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">Voters</span></p></body></html>"))
        self.radioButton_visualizeYes.setText(_translate("MainWindow", "Yes"))
        self.radioButton_visualizeNo.setText(_translate("MainWindow", "No"))
        self.label_visualize.setText(_translate("MainWindow", "Visualize"))
        self.radioButton_saveNo.setText(_translate("MainWindow", "No"))
        self.radioButton_saveYes.setText(_translate("MainWindow", "Yes"))
        self.label_saveResults.setText(_translate("MainWindow", "Save Results"))
        self.label_dimensions.setText(_translate("MainWindow", "Dimensions"))
        self.label_breaks.setText(_translate("MainWindow", "Breaks"))
        self.doubleSpinBox_breaks.setToolTip(_translate("MainWindow", "Breaks at which the positions are evaluated"))
        self.label_runs.setText(_translate("MainWindow", "Runs"))
        self.spinBox_dimensions.setToolTip(_translate("MainWindow", "Number of dimensions"))
        self.label_alterPrefs.setText(_translate("MainWindow", "Alter Preferences"))
        self.radioButton_alterPrefsYes.setToolTip(_translate("MainWindow", "Voter positions drift a specified amount every run"))
        self.radioButton_alterPrefsYes.setText(_translate("MainWindow", "Drift"))
        self.radioButtonalterPrefsNo.setToolTip(_translate("MainWindow", "Voter positions are constant for every run"))
        self.radioButtonalterPrefsNo.setText(_translate("MainWindow", "No"))
        self.radioButton_distParetian_2.setToolTip(_translate("MainWindow", "Status Quo is set randomly every run"))
        self.radioButton_distParetian_2.setText(_translate("MainWindow", "Random"))
        self.radioButton_distNormal_2.setToolTip(_translate("MainWindow", "Status Quo is constant for every run"))
        self.radioButton_distNormal_2.setText(_translate("MainWindow", "No"))
        self.radioButton_distExponential_2.setToolTip(_translate("MainWindow", "Status Quo is based on voting outcome and specified drift"))
        self.radioButton_distExponential_2.setText(_translate("MainWindow", "History + Drift"))
        self.label_AlterStatusQuo.setText(_translate("MainWindow", "Alter Status Quo"))
        self.radioButton_distUniform_2.setToolTip(_translate("MainWindow", "Status Quo is based on voting outcome every run"))
        self.radioButton_distUniform_2.setText(_translate("MainWindow", "History"))
        self.radioButton_distanceManh.setText(_translate("MainWindow", "Manhattan"))
        self.radioButton_distancePyth.setText(_translate("MainWindow", "Pythagorean"))
        self.label_distanceType.setText(_translate("MainWindow", "Distance Type"))
        self.radioButton_distParetian.setText(_translate("MainWindow", "Paretian"))
        self.radioButton_distUniform.setText(_translate("MainWindow", "Uniform"))
        self.radioButton_distExponential.setText(_translate("MainWindow", "Exponential"))
        self.radioButton_distNormal.setText(_translate("MainWindow", "Normal"))
        self.label_distribution.setText(_translate("MainWindow", "Distribution"))
        self.label_outputFolder.setText(_translate("MainWindow", "Output Folder"))
        self.pushButton_OutputCD.setText(_translate("MainWindow", "CD"))
        self.label_LoadSettings.setText(_translate("MainWindow", "Load Settings"))
        self.pushButton_loadSettingsCD.setText(_translate("MainWindow", "CD"))
        self.graph_trace_no.setText(_translate("MainWindow", "No"))
        self.graph_trace_yes.setText(_translate("MainWindow", "Yes"))
        self.label_saveResults_2.setToolTip(_translate("MainWindow", "Trace changes of the status quo in the visualization"))
        self.label_saveResults_2.setText(_translate("MainWindow", "Trace Changes"))
        self.label_sequenceFolder.setText(_translate("MainWindow", "Load Sequence"))
        self.pushButton_SequenceCD.setText(_translate("MainWindow", "CD"))
        self.label_Setup_Options.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">Options</span></p></body></html>"))
        self.pushButton_runSim.setText(_translate("MainWindow", "Run Simulation"))
        self.pushButton.setText(_translate("MainWindow", ">>"))
        self.pushButton_2.setText(_translate("MainWindow", "<<"))
        self.label_Setup_Manifesto_2.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">Setup Voters – Manifesto</span></p></body></html>"))
        self.menuAbout.setTitle(_translate("MainWindow", "About"))

if __name__ == "__main__":
    import sys
    app = QtCore.QCoreApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())