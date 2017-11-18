# -*- coding: utf-8 -*-
"""
Created on Thu Oct 19 00:55:58 2017

@author: Frederik
"""
# TODO enter Random -> random... general error handling
import sys
import os
import warnings
import json
import errno
import time
import numpy as np
import random
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from PyQt5 import QtCore, QtWidgets, QtGui

_DOCK_OPTS = QtWidgets.QMainWindow.AnimatedDocks | QtWidgets.QMainWindow.AllowNestedDocks | \
             QtWidgets.QMainWindow.AllowTabbedDocks


class GameTableOptions:
    def __init__(self, from_load: bool = False, settings: object = None) -> object:
        if from_load is False:
            """Run"""
            self.runs = 1
            self.dimensions = 2
            self.method = "grid"
            self.save = "yes"
            self.visualize = "yes"
            self.alter_preferences = "no"
            self.alter_statusquo = "history+drift"
            self.distribution = "uniform"
            self.save_visualize = "no"

            """Advanced Run"""
            self.breaks = 0.01
            self.density = 1
            self.distance_type = "euclidean"
            self.sq_vibration_distribution = "uniform"
            self.vibrate_sq = "no"

        else:
            """Run"""
            self.runs = settings["runs"]
            self.dimensions = settings["dimensions"]
            self.method = settings["method"]
            print(self.method)
            self.save = settings["save"]
            self.visualize = settings["visualize"]
            self.alter_preferences = settings["alter_preferences"]
            self.alter_statusquo = settings["alter_statusquo"]
            self.save_visualize = settings["save_visualize"]
            
            """Advanced Run"""
            self.density = settings["density"]
            self.breaks = settings["breaks"]
            self.distance_type = settings["distance_type"]
            self.sq_vibration_distribution = settings["sq_vibration_distribution"]
            self.vibrate_sq = settings["vibrate_sq"]


class MainWindow(QtWidgets.QMainWindow):
    """
    Main Window
    """

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setup_dockwidgets()
        self.setup_menu()
        self.initialize_connections()
        self.setup_toolbar()

        self.setDockOptions(_DOCK_OPTS)

    def setup_toolbar(self):
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
        load_action = QtWidgets.QAction(QtGui.QIcon("./assets/iconOpenFolder.png"), "Import Data", self)
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self.load)

        save_action = QtWidgets.QAction(QtGui.QIcon("./assets/iconSave.png"), "Save Data", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save)

        save_all_action = QtWidgets.QAction(QtGui.QIcon("./assets/iconSaveAll.png"), "Save All", self)

        run_action = QtWidgets.QAction(QtGui.QIcon("./assets/iconRun.png"), "Run", self)
        run_action.triggered.connect(self.run_simulation)

        run_all_action = QtWidgets.QAction(QtGui.QIcon("./assets/iconRunAll.png"), "Run All", self)

        run_last_action = QtWidgets.QAction(QtGui.QIcon("./assets/iconRunLast.png"), "Repeat Last Run", self)

        settings_action = QtWidgets.QAction(QtGui.QIcon("./assets/iconSettings.png"), "Settings", self)
        settings_action.triggered.connect(self.show_preference_window)

        manifesto_action = QtWidgets.QAction(QtGui.QIcon("./assets/iconManifesto.png"), "Manifesto Window", self)
        manifesto_action.triggered.connect(self.show_manifesto)

        plot_action = QtWidgets.QAction(QtGui.QIcon("./assets/iconPlot.png"), "Plot Window", self)
        plot_action.triggered.connect(self.show_plot)

        clear_action = QtWidgets.QAction(QtGui.QIcon("./assets/iconClear.png"), "Clear All", self)
        clear_action.setShortcut("Ctrl+C")
        clear_action.triggered.connect(lambda: self.visualizeWidget.adjust_axes(2))

        stretcher = QtWidgets.QWidget()
        stretcher.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        """
        add actions to toolbar
        """
        self.toolbar_fileHandling.addActions([load_action, save_action, save_all_action])

        self.toolbar_runSim.addActions([run_action, run_all_action, run_last_action])

        self.toolbar_dockWindows.addActions([settings_action, manifesto_action, plot_action])

        self.toolbar_clear.addAction(clear_action)

        self.toolbar_logo.addWidget(stretcher)
        self.toolbar_logo.addWidget(vb_label)

    def load(self):
        options = None

        file = QtWidgets.QFileDialog.getOpenFileName(filter="Text Files (*.txt)")

        if file[0]:
            with open(file[0]) as sequence:
                seq = json.load(sequence)
        else:
            return

        if "run_settings" in seq:
            try:
                options = GameTableOptions(from_load=True, settings=seq["run_settings"])
            except KeyError:
                warnings.warn("Can't read settings -- invalid keys")

        if "voters" and "statusquo" in seq or "sequence" in seq:
            self.voterWidget.load_table(seq, options)

        if "visualization_settings" in seq:
            self.optionsWidget.load_options(seq["visualization_settings"])

    def save(self):
        file = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory"))

        if not file:
            return

        run_options = self.voterWidget.tabWidget.currentWidget().save_options()
        other_options = self.optionsWidget.save_options()
        tables = self.voterWidget.tabWidget.currentWidget().save_table()

#        """2.7 way for pyinstaller support"""  # TODO fix
#        out1 = run_options.copy()
#        out1.update(other_options)
#        out1.update(tables)
        out = dict(**run_options, **other_options, **tables)

        with open(os.path.join(file, "save.txt"), "w") as outfile:
            json.dump(out, outfile)

    def show_preference_window(self):
        if self.preferencesDock.isVisible():
            return

        if not self.preferencesDock.isWindow():
            self.preferencesDock.setFloating(True)

        self.preferencesDock.setGeometry(QtCore.QRect(100, 100, 400, 400))
        self.preferencesDock.show()

    def show_manifesto(self):
        if self.manifestoDock.isVisible():
            return

        self.manifestoDock.show()

    def show_plot(self):
        if self.visualizeDock.isVisible():
            return
        self.visualizeDock.show()

    def setup_menu(self):
        """
        Menu Bar
        """
        menu = self.menuBar()
        menu.addMenu("&Help")
        menu.addMenu("&About")

    def setup_dockwidgets(self):
        self.setWindowTitle("Vetoboxing")
        self.resize(1000, 1000)

        manifesto_widget = ManifestoPyDockWidget(self)
        self.manifestoDock = QtWidgets.QDockWidget()
        self.manifestoDock.setWidget(manifesto_widget)
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
        self.logWidget.append("Init")

        self.visualizeWidget = VisualizeDockWidget(self)
        #        self.visualizeWidget = VisualizeCanvas(self)
        self.visualizeDock = QtWidgets.QDockWidget()
        self.visualizeDock.setWindowTitle("Plots")
        self.visualizeDock.setWidget(self.visualizeWidget)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.visualizeDock)

        self.voterWidget = VoterSetup(self, init_dim=self.optionsWidget.run_options.spinBox_dimensions.value())
        self.setCentralWidget(self.voterWidget)

        #        self.voterWidget.tabWidget.currentChanged.connect(self.voterWidget.__addTab__)
        self.voterWidget.tabWidget.currentChanged.connect(self.tabwidget_changed_connect)

    def initialize_connections(self):
        """
        On-change Functions that continuously pass changes in run options
        and in advanced run options to the respective Game Table's option class
        """

        """Run Options"""
        self.optionsWidget.run_options.spinBox_dimensions.valueChanged.connect(
            lambda: self.voterWidget.tabWidget.currentWidget().change_dim(
                self.optionsWidget.run_options.spinBox_dimensions.value()))

        self.optionsWidget.run_options.spinBox_runs.valueChanged.connect(
            lambda: self.update_gametable_options("runs",
                                                  self.optionsWidget.run_options.spinBox_runs.value()))

        self.optionsWidget.run_options.spinBox_dimensions.valueChanged.connect(
            lambda: self.update_gametable_options("dimensions",
                                                  self.optionsWidget.run_options.spinBox_dimensions.value()))

        self.optionsWidget.run_options.doubleSpinBox_breaks.valueChanged.connect(
            lambda: self.update_gametable_options("breaks",
                                                  self.optionsWidget.run_options.doubleSpinBox_breaks.value()))

        self.optionsWidget.run_options.spinBox_density.valueChanged.connect(
            lambda: self.update_gametable_options("density",
                                                  self.optionsWidget.run_options.spinBox_density.value()))

        self.optionsWidget.run_options.buttonGroup_method.buttonToggled.connect(
            lambda: self.update_gametable_options("method",
                                                  self.optionsWidget.run_options.
                                                  buttonGroup_method.checkedButton().text().lower()))

        self.optionsWidget.run_options.buttonGroup_save.buttonToggled.connect(
            lambda: self.update_gametable_options("save",
                                                  self.optionsWidget.run_options.
                                                  buttonGroup_save.checkedButton().text().lower()))

        self.optionsWidget.run_options.buttonGroup_visualize.buttonToggled.connect(
            lambda: self.update_gametable_options("visualize",
                                                  self.optionsWidget.run_options.
                                                  buttonGroup_visualize.checkedButton().text().lower()))

        self.optionsWidget.run_options.buttongroup_alter_preferences. \
            buttonToggled.connect(lambda: self.
                                  update_gametable_options("alter_preferences",
                                                           self.
                                                           optionsWidget.run_options.buttongroup_alter_preferences.
                                                           checkedButton().text().lower()))

        self.optionsWidget.run_options.buttonGroup_alterStatusQuo.buttonToggled.connect(
            lambda: self.update_gametable_options("alter_statusquo",
                                                  self.optionsWidget.run_options.
                                                  buttonGroup_alterStatusQuo.checkedButton().text().lower()))

        self.optionsWidget.run_options.buttonGroup_saveVisualize.buttonToggled.connect(
            lambda: self.update_gametable_options("save_visualize",
                                                  self.optionsWidget.
                                                  run_options.buttonGroup_saveVisualize.checkedButton().text().lower()))

        """Advanced Run Options"""
        self.optionsWidget.advanced_run_options.buttongroup_distance_type.buttonToggled.connect(
            lambda: self.update_gametable_options("distance_type",
                                                  self.optionsWidget.advanced_run_options.
                                                  buttongroup_distance_type.checkedButton().text().lower()))

        self.optionsWidget.advanced_run_options.buttonGroup_distribution.buttonToggled.connect(
            lambda: self.update_gametable_options("sq_vibration_distribution",
                                                  self.optionsWidget.advanced_run_options.
                                                  buttonGroup_distribution.checkedButton().text().lower()))

        self.optionsWidget.advanced_run_options.buttongroup_statusquo_vibration.buttonToggled.connect(
            lambda: self.update_gametable_options("vibrate_sq",
                                                  self.optionsWidget.advanced_run_options.
                                                  buttongroup_statusquo_vibration.checkedButton().text().lower()))

        self.optionsWidget.advanced_run_options.spinBox_density.valueChanged.connect(
            lambda: self.update_gametable_options("density",
                                                  self.optionsWidget.advanced_run_options.
                                                  spinBox_density.value()))

        self.optionsWidget.advanced_run_options.doubleSpinBox_breaks.valueChanged.connect(
            lambda: self.update_gametable_options("breaks",
                                                  self.optionsWidget.advanced_run_options.
                                                  doubleSpinBox_breaks.value()))

        # TODO catch error here when no game is connected
        self.visualizeWidget.pushButton_next.clicked.connect(self.plot_window_forward)
        self.visualizeWidget.pushButton_prev.clicked.connect(self.plot_window_backward)

    def update_gametable_options(self, option, value):
        """run options"""
        if option == "runs":
            self.voterWidget.tabWidget.currentWidget().options.runs = value

        elif option == "dimensions":
            self.voterWidget.tabWidget.currentWidget().options.dimensions = value

        elif option == "method":
            self.voterWidget.tabWidget.currentWidget().options.method = value

        elif option == "save":
            self.voterWidget.tabWidget.currentWidget().options.save = value

        elif option == "visualize":
            self.voterWidget.tabWidget.currentWidget().options.visualize = value

        elif option == "alter_preferences":
            self.voterWidget.tabWidget.currentWidget().options.alter_preferences = value

        elif option == "alter_statusquo":
            self.voterWidget.tabWidget.currentWidget().options.alter_statusquo = value

        elif option == "save_visualize":
            self.voterWidget.tabWidget.currentWidget().options.save_visualize = value

            """advanced run options"""
        elif option == "sq_vibration_distribution":
            self.voterWidget.tabWidget.currentWidget().options.sq_vibration_distribution = value

        elif option == "vibrate_sq":
            self.voterWidget.tabWidget.currentWidget().options.vibrate_sq = value

        elif option == "distance_type":
            self.voterWidget.tabWidget.currentWidget().options.distance_type = value

        elif option == "breaks":
            self.voterWidget.tabWidget.currentWidget().options.breaks = value

        elif option == "density":
            self.voterWidget.tabWidget.currentWidget().options.density = value

    def tabwidget_changed_connect(self, index):
        self.voterWidget.add_tab(index)
        self.optionsWidget.set_run_options(self.voterWidget.tabWidget.currentWidget().options)

    def plot_window_forward(self):
        try:
            if self.index == self.var.runs - 1:
                return
            else:
                self.sim.visualize_draw_on_axis(self.var.dimensions, self.visualizeWidget.canvas.axes, self.index + 1,
                                                self.sim.visualize_limits, fromUI=True)
                self.index += 1
                self.visualizeWidget.canvas.draw()
        except AttributeError:
            return

    def plot_window_backward(self):
        try:
            if self.index == 0:
                return
            else:
                self.sim.visualize_draw_on_axis(self.var.dimensions, self.visualizeWidget.canvas.axes, self.index - 1,
                                                self.sim.visualize_limits, fromUI=True)
                self.index -= 1
                self.visualizeWidget.canvas.draw()
        except AttributeError:
            return

    def run_simulation(self):
        try:
            self.var = self.read_values()

        except ValueError:
            return

        except AttributeError:
            return

        except:
            raise

        self.index = 0
        to_ui_plot = False

        import simulation as vb

        self.sim = vb.Simulation(self.var, self)
        self.sim.simulation()

        if self.var.visualize == "yes" and self.var.save_visualize == "yes":
            self.sim.visualize_init(save=True)
            to_ui_plot = True

        elif self.var.visualize == "no" and self.var.save_visualize == "yes":
            self.sim.visualize_init(save=True)

        elif self.var.visualize == "yes" and self.var.save_visualize == "no":
            self.sim.visualize_init(save=False)
            to_ui_plot = True

        if to_ui_plot is True:
            self.visualizeWidget.adjust_axes(self.var.dimensions)

            """Init draw (draw first run)"""
            self.sim.visualize_draw_on_axis(self.var.dimensions, self.visualizeWidget.canvas.axes, 0,
                                            self.sim.visualize_limits, fromUI=True)
            self.visualizeWidget.canvas.draw()
            
    @staticmethod
    def to_bool(item):
        if str(item.lower()) == "yes":
            return True
        else:
            return False

    def read_values(self):
        """
        Convert tables to arrays and transfer arrays + settings to 
        var.py for sim to read
        """
        
        votercount = self.voterWidget.tabWidget.currentWidget().voter_table.rowCount()
        
        """Run Options"""
        dimensions = self.voterWidget.tabWidget.currentWidget().options.dimensions
        method = self.voterWidget.tabWidget.currentWidget().options.method
        runs = self.voterWidget.tabWidget.currentWidget().options.runs
        save = self.voterWidget.tabWidget.currentWidget().options.save
        visualize = self.voterWidget.tabWidget.currentWidget().options.visualize
        save_visualize = self.voterWidget.tabWidget.currentWidget().options.save_visualize
        alter_preferences = self.voterWidget.tabWidget.currentWidget().options.alter_preferences
        alter_statusquo = self.voterWidget.tabWidget.currentWidget().options.alter_statusquo
        
        """Adv Run Options"""
        breaks = self.voterWidget.tabWidget.currentWidget().options.breaks
        density = self.voterWidget.tabWidget.currentWidget().options.density
        distance_type = self.voterWidget.tabWidget.currentWidget().options.distance_type
        sq_vibration_distribution = self.voterWidget.tabWidget.currentWidget().options.sq_vibration_distribution
        vibrate_sq = self.voterWidget.tabWidget.currentWidget().options.vibrate_sq

        statusquo_position, statusquo_drift, voter_names, voter_roles, voter_positions, \
        random_agenda_setter, random_veto_player = self.voterWidget.tabWidget.currentWidget().return_init_arrays()

        if statusquo_drift is None and alter_statusquo == "history+drift":
            warnings.warn("No Status Quo Drift specified, but History+Drift selected")
            raise ValueError("No Status Quo Drift specified, but History+Drift selected")

        custom_role_array = self.voterWidget.tabWidget.currentWidget().custom_role_array

        directory = None

        if save or visualize:
            model_number = self.set_model_number(alter_statusquo, alter_preferences)

            if directory is None:
                parent_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "RESULTS")
                self.create_dir(parent_dir)
                results_dir = self.results_dir(model_number, dimensions, runs, parent_dir)
                directory = results_dir

        return SimulationVariables(votercount=votercount, 
                                   runs=runs, breaks=breaks, 
                                   density=density,
                                   dimensions=dimensions, 
                                   save=save, 
                                   visualize=visualize,
                                   alter_preferences=alter_preferences, 
                                   alter_statusquo=alter_statusquo,
                                   distance_type=distance_type, 
                                   sq_vibration_distribution=sq_vibration_distribution,
                                   directory=directory, 
                                   statusquo_position=statusquo_position,
                                   statusquo_drift=statusquo_drift, 
                                   voter_names=voter_names,
                                   voter_roles=voter_roles, 
                                   voter_positions=voter_positions,
                                   random_agenda_setter=random_agenda_setter,
                                   random_veto_player=random_veto_player, 
                                   method=method,
                                   custom_role_array=custom_role_array,
                                   save_visualize=save_visualize, 
                                   vibrate_sq = self.to_bool(vibrate_sq))

    @staticmethod
    def set_model_number(alter_statusquo, alter_preferences):
        """
        Set the model number of the simulation for classifying the model in the csv
        """
        if alter_statusquo == "no":
            return 0

        elif alter_statusquo == "random":
            return 1

        elif alter_statusquo == "history":
            return 2

        elif alter_statusquo == "history+drift" and alter_preferences == "no":
            return 3

        elif alter_statusquo == "history + drift" and alter_preferences == "drift":
            return 4

        else:
            return "NA"

    @staticmethod
    def create_dir(directory):
        """
        Create directory
        """
        try:
            os.makedirs(directory)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    def results_dir(self, model_number, dimensions, runs, parent_dir):
        """
        Create a directory for the simulation results
        """
        timestr = time.strftime("%Y-%m-%d_%H%M")

        foldername = "".join(("results", "-", str(model_number), "-", str(dimensions), "-", str(runs), "__", timestr))

        results_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), parent_dir, foldername)
        self.create_dir(results_dir)
        return results_dir


# noinspection PyTypeChecker
class VoterSetup(QtWidgets.QWidget):
    """
    Tab Widget for Voter Position / Drift /  Role Tables
    """

    def __init__(self, parent, init_dim):
        super(VoterSetup, self).__init__(parent)
        self.fromLoadAdd = False
        self.set_random_agenda_setter = False
        self.set_random_veto_player = False

        self.initDim = init_dim
        self.setup_tabwidget()
        self.setup_toolbar()

        self.set_layout()

    def setup_toolbar(self):
        self.toolbar = QtWidgets.QToolBar()
        self.toolbar.setIconSize(QtCore.QSize(14, 14))

        stretcher = QtWidgets.QWidget()
        stretcher.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        clear_action = QtWidgets.QAction(QtGui.QIcon("./assets/iconClear.png"), "Remove Voter", self)
        clear_action.setShortcut("Ctrl+X")
        clear_action.triggered.connect(self.del_voter_table_row)

        add_action = QtWidgets.QAction(QtGui.QIcon("./assets/iconAdd.png"), "Add Voter", self)
        add_action.setShortcut("Ctrl+A")
        add_action.triggered.connect(self.add_voter_table_row)

        randomize_action = QtWidgets.QAction(QtGui.QIcon("./assets/iconRandom.png"), "Random Roles", self)
        randomize_action.setShortcut("Ctrl+R")
        randomize_action.triggered.connect(self.random_roles)

        self.random_veto_spinbox = QtWidgets.QSpinBox()
        self.random_veto_spinbox.setToolTip("Number of Veto Players")

        self.random_veto_action = QtWidgets.QAction(QtGui.QIcon("./assets/iconVeto.png"),
                                                    "Select Random Veto Player(s)", self)
        self.random_veto_action.triggered.connect(lambda: self.set_random_player_states("vetoplayer"))

        self.random_agenda_setter_action = QtWidgets.QAction(QtGui.QIcon("./assets/iconAS"),
                                                             "Select Random Agenda Setter", self)

        self.random_agenda_setter_action.triggered.connect(lambda: self.set_random_player_states("agendasetter"))

        self.toolbar.addAction(add_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(clear_action)

        self.toolbar.addWidget(stretcher)

        self.toolbar.addWidget(self.random_veto_spinbox)
        self.toolbar.addAction(self.random_veto_action)
        self.toolbar.addAction(self.random_agenda_setter_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(randomize_action)

    def set_random_player_states(self, player):
        if player == "agendasetter":
            if self.set_random_agenda_setter is False:
                self.set_random_agenda_setter = True
                self.random_agenda_setter_action.setIcon(QtGui.QIcon("./assets/iconASTriggered.png"))
            else:
                self.set_random_agenda_setter = False
                self.random_agenda_setter_action.setIcon(QtGui.QIcon("./assets/iconAS.png"))
        else:
            if self.set_random_veto_player is False:
                self.set_random_veto_player = True
                self.random_veto_action.setIcon(QtGui.QIcon("./assets/iconVetoTriggered.png"))
            else:
                self.set_random_veto_player = False
                self.random_veto_action.setIcon(QtGui.QIcon("./assets/iconVeto.png"))

    def random_roles(self):
        if self.set_random_agenda_setter:
            """clear row first"""
            [self.tabWidget.currentWidget().voter_table.setItem(row, 1, None)
             for row in range(self.tabWidget.currentWidget().voter_table.rowCount())]

            """select rnd index"""
            random_agenda_setter = random.choice(range(self.tabWidget.currentWidget().voter_table.rowCount()))
            self.tabWidget.currentWidget().voter_table.setItem(random_agenda_setter, 1,
                                                               QtWidgets.QTableWidgetItem("True"))

        if self.set_random_veto_player:
            """clear row"""
            [self.tabWidget.currentWidget().voter_table.setItem(row, 2, None)
             for row in range(self.tabWidget.currentWidget().voter_table.rowCount())]

            """select rnd indexes"""
            if self.set_random_agenda_setter:
                random_veto_player_sample = [i for i in range(self.tabWidget.currentWidget().voter_table.rowCount()) if
                                             i != random_agenda_setter]
            else:
                random_veto_player_sample = [i for i in range(self.tabWidget.currentWidget().voter_table.rowCount())]

            if self.random_veto_spinbox.value() >= self.tabWidget.currentWidget().voter_table.rowCount():
                warnings.warn("Vetoplayer sample larger than number of voters.")
                return
            else:
                random_veto_players = random.sample(random_veto_player_sample, self.random_veto_spinbox.value())

                [self.tabWidget.currentWidget().voter_table.setItem(row, 2, QtWidgets.QTableWidgetItem("True")) for row
                 in
                 random_veto_players]

        """fill remainder with false"""
        for col in [index for index in [1 * self.set_random_agenda_setter,
                                        2 * self.set_random_veto_player] if index != 0]:
            for row in range(self.tabWidget.currentWidget().voter_table.rowCount()):
                if self.tabWidget.currentWidget().voter_table.item(row, col) is None:
                    self.tabWidget.currentWidget().voter_table.setItem(row, col, QtWidgets.QTableWidgetItem("False"))

    def add_voter_table_row(self):
        self.tabWidget.currentWidget().voter_table.add_row()

    def del_voter_table_row(self):
        self.tabWidget.currentWidget().voter_table.del_row()

    def setup_tabwidget(self):
        self.tabWidget = QtWidgets.QTabWidget()
        self.tabbar = EditableTabBar(self)
        self.tabbar.setSelectionBehaviorOnRemove(QtWidgets.QTabBar.SelectLeftTab)

        self.tabWidget.setTabBar(self.tabbar)
        self.tabWidget.setTabPosition(0)

        self.setup_tables()

        self.tabWidget.addTab(QtWidgets.QWidget(), "+")
        self.tabWidget.setUpdatesEnabled(True)

        self.tabWidget.setTabsClosable(True)
        self.tabbar.tabButton(self.tabWidget.count() - 1, QtWidgets.QTabBar.RightSide).resize(0, 0)
        self.tabWidget.tabCloseRequested.connect(self.remove_tab)

    def add_tab(self, index):
        if index == self.tabWidget.count() - 1 and not self.fromLoadAdd:
            """last tab was clicked. add tab"""
            self.tabWidget.insertTab(index, GameTable(self), "Sim {0}".format(index + 1))
            self.tabWidget.setCurrentIndex(index)
        else:
            return

    def remove_tab(self, index):
        widget = self.tabWidget.widget(index)

        if widget is not None:
            widget.deleteLater()

        self.tabWidget.removeTab(index)

    def set_layout(self):
        self.layout = QtWidgets.QVBoxLayout()

        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.tabWidget)

        self.setLayout(self.layout)

    def setup_tables(self):
        for i in range(3):
            self.tabWidget.addTab(GameTable(self, 2), "Test")

    def load_table(self, seq, options=None):
        if "sequence" in seq:
            self.tabWidget.currentWidget().custom_role_array = seq["sequence"]

        else:
            self.fromLoadAdd = True
            self.tabWidget.insertTab(self.tabWidget.count() - 1,
                                     GameTable(self, from_load=True, file=seq, options=options), "Test2")
            self.tabWidget.setCurrentIndex(self.tabWidget.count() - 2)
            self.fromLoadAdd = False


class GameTable(QtWidgets.QWidget):
    def __init__(self, parent, dim_init=2, from_load=False, file=None, options=None):
        super(GameTable, self).__init__(parent)

        self.custom_role_array = None

        if not from_load:
            self.options = GameTableOptions()
            self.setup(dim_init)
            self.set_layout()

        else:
            if options:
                self.options = options
            else:
                self.options = GameTableOptions()

            self.load_table(file)
            self.set_layout()

    def setup(self, dim_init):
        self.voter_table = TableWidget()
        self.voter_table.setColumnCount(3 + dim_init)
        self.voter_table.setRowCount(3)
        self.voter_table.setHorizontalHeaderLabels(["Name", "Agenda Setter", "Veto Player"] +
                                                   ["Dim" + str(dim + 1) for dim in range(dim_init)])

        self.statusquo_table = QtWidgets.QTableWidget()
        self.statusquo_table.setColumnCount(dim_init)
        self.statusquo_table.setRowCount(2)
        self.statusquo_table.setHorizontalHeaderLabels(["Dim" + str(dim + 1) for dim in range(dim_init)])
        self.statusquo_table.setVerticalHeaderLabels(["Position", "Drift"])

    #        self.statusQuoTable.setCornerButtonEnabled()

    def set_layout(self):
        splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        splitter.addWidget(self.voter_table)
        splitter.addWidget(self.statusquo_table)
        splitter.setStretchFactor(0, 10)
        splitter.setStretchFactor(1, 3)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(splitter)
        self.setLayout(layout)

    def change_dim(self, dim_value):
        self.voter_table.setColumnCount(3 + dim_value)
        self.voter_table.setHorizontalHeaderLabels(["Name", "Agenda Setter", "Veto Player"] +
                                                   ["Dim " + str(dim + 1) for dim in range(dim_value)])

        self.statusquo_table.setColumnCount(dim_value)
        self.statusquo_table.setHorizontalHeaderLabels(["Dim" + str(dim + 1) for dim in range(dim_value)])

    def save_options(self):
        save = {
            "run_settings": {
                "alter_preferences": self.options.alter_preferences,
                "alter_statusquo": self.options.alter_statusquo,
                "dimensions": self.options.dimensions,
                "runs": self.options.runs,
                "save": self.options.save,
                "visualize": self.options.visualize,
                "save_visualize": self.options.save_visualize,
                "method": self.options.method,
                "sq_vibration_distribution": self.options.sq_vibration_distribution,
                "breaks": self.options.breaks,
                "distance_type": self.options.distance_type,
                "density": self.options.density,
                "vibrate_sq" : self.options.vibrate_sq
                }
        }

        return save

    def save_table(self):
        """
        Save voter and SQ setup
        """
        save = {
            "voters": {
                "votercount": self.voter_table.rowCount(),
                "names": [self.voter_table.item(row, 0).text() for
                          row in range(self.voter_table.rowCount())],
                "agendasetter": [self.voter_table.item(row, 1).text() for
                                 row in range(self.voter_table.rowCount())],
                "vetoplayer": [self.voter_table.item(row, 2).text() for
                               row in range(self.voter_table.rowCount())],
                "positions": [[self.voter_table.item(row, dim + 3).text() for
                               dim in range(self.voter_table.columnCount() - 3)]
                              for row in range(self.voter_table.rowCount())]
                #                        "drift" : [[self.voterTable.item(row, dim).text() for
                #                                    dim in range(dimensions)] for row in range(voterCount)]
            },
            "statusquo": {
                "position": [self.statusquo_table.item(0, dim).text() for
                             dim in range(self.statusquo_table.columnCount())],
                "drift": [self.statusquo_table.item(1, dim).text() for
                          dim in range(self.statusquo_table.columnCount())]
            }
        }

        return save

    def load_table(self, sequence):
        """
        Load voter and SQ table data
        """
        seq = sequence
        try:
            """Setup"""
            self.voter_table = TableWidget()
            self.voter_table.setRowCount(seq["voters"]["votercount"])
            self.voter_table.setColumnCount(len(seq["voters"]["positions"][0]) + 3)

            self.voter_table.setHorizontalHeaderLabels(["Name", "Agenda Setter", "Veto Player"] +
                                                       ["Dim" + str(dim + 1) for dim in
                                                        range(len(seq["voters"]["positions"][0]))])

            self.statusquo_table = QtWidgets.QTableWidget()
            self.statusquo_table.setColumnCount(len(seq["statusquo"]["position"]))
            self.statusquo_table.setRowCount(2)
            self.statusquo_table.setHorizontalHeaderLabels(["Dim" + str(dim + 1) for dim in
                                                            range(len(seq["statusquo"]["position"]))])
            self.statusquo_table.setVerticalHeaderLabels(["Position", "Drift"])

            """Names"""
            if "names" in seq["voters"]:
                [self.voter_table.setItem(row, 0, QtWidgets.QTableWidgetItem(item))
                 for row, item in zip(range(self.voter_table.rowCount()), seq["voters"]["names"])]

            else:
                [self.voter_table.setItem(i, 0, QtWidgets.QTableWidgetItem("Voter " + str(i + 1)))
                 for i in range(self.voter_table.rowCount())]

            """Agenda Setter"""
            if seq["voters"]["agendasetter"] == "random":
                [self.voter_table.setItem(row, 1, QtWidgets.QTableWidgetItem("random"))
                 for row in range(self.voter_table.rowCount())]

            else:
                [self.voter_table.setItem(row, 1, QtWidgets.QTableWidgetItem(item))
                 for row, item in zip(range(self.voter_table.rowCount()), seq["voters"]["agendasetter"])]

            """Veto Player"""
            if seq["voters"]["vetoplayer"] == "random":
                [self.voter_table.setItem(row, 2, QtWidgets.QTableWidgetItem("random"))
                 for row in range(self.voter_table.rowCount())]

            else:
                [self.voter_table.setItem(row, 2, QtWidgets.QTableWidgetItem(item))
                 for row, item in zip(range(self.voter_table.rowCount()), seq["voters"]["agendasetter"])]

            """Positions"""
            if "positions" in seq["voters"]:
                for row, item in zip(range(self.voter_table.rowCount()), seq["voters"]["positions"]):
                    for col, it in enumerate(item):
                        self.voter_table.setItem(row, col + 3, QtWidgets.QTableWidgetItem(str(it)))

            """Status Quo"""
            [[self.statusquo_table.setItem(row, col, QtWidgets.QTableWidgetItem(str(it)))
              for col, it in enumerate(item)] for row, item in zip(range(self.statusquo_table.rowCount()),
                                                                   [seq["statusquo"]["position"],
                                                                    seq["statusquo"]["drift"]])]

        except:
            raise

    @staticmethod
    def to_bool(item):
        if str(item.lower()) == "true" or str(item) == "1":
            return True
        else:
            return

    def return_init_arrays(self):
        """Status Quo Values"""

        try:
            statusquo_position = [float(self.statusquo_table.item(0, dim).text()) for dim in
                                  range(self.statusquo_table.columnCount())]
        except ValueError:
            warnings.warn("Value Error - Wrong Status Quo Position input")
            raise

        except AttributeError:
            warnings.warn("Attribute Error - No Status Quo Position specified")
            raise

        try:
            statusquo_drift = np.array(
                [[float(self.statusquo_table.item(1, dim).text()) for
                  dim in range(self.statusquo_table.columnCount())]])

        except ValueError:
            warnings.warn("Value Error - Wrong Status Quo Drift input")
            statusquo_drift = None

        except AttributeError:
            warnings.warn("Type Error - No Status Quo Drift specified")
            statusquo_drift = None

        """Voter Values"""
        voter_names = [self.voter_table.item(row, 0).text() for row in range(self.voter_table.rowCount())]

        if None in voter_names:
            warnings.warn("No Voter Names specified")

        random_agendasetter = False
        random_vetoplayer = False

        if "random" in self.voter_table.item(0, 1).text() and not\
                        "random" in self.voter_table.item(0, 2).text().lower():
            random_agendasetter = True
            voter_roles = [0 if not self.to_bool(self.voter_table.item(row, 2).text()) else 1 for
                           row in range(self.voter_table.rowCount())]

        elif "random" in self.voter_table.item(0, 2).text() and not "random" in \
                self.voter_table.item(0, 1).text().lower():
            random_vetoplayer = True
            voter_roles = [0 if not self.to_bool(self.voter_table.item(row, 1).text()) else 2 for
                           row in range(self.voter_table.rowCount())]

        elif "random" in self.voter_table.item(0, 1).text() and "random" in \
                self.voter_table.item(0, 2).text().lower():
            random_agendasetter = True
            random_vetoplayer = True
            voter_roles = None

        else:
            voter_roles = [0 if not self.to_bool(self.voter_table.item(row, 1).text()) and not self.to_bool(
                self.voter_table.item(row, 2).text()) else 2 if
            self.to_bool(self.voter_table.item(row, 1).text()) else 1 for row in range(self.voter_table.rowCount())]

        print("----", voter_roles)
        if voter_roles is not None and random_agendasetter is not True:
            if not 2 in voter_roles:
                warnings.warn("No Agenda-Setter selected")
                raise ValueError("No Agenda Setter selected")

        try:
            voter_positions = [
                [float(self.voter_table.item(row, col + 3).text()) for col in range(self.voter_table.columnCount() - 3)]
                for row in range(self.voter_table.rowCount())]
        except ValueError:
            warnings.warn("Value Error - Wrong Voter Position input")
            raise

        except AttributeError:
            warnings.warn("Attribute Error - No Voter Positions specified")
            raise

        return statusquo_position, statusquo_drift, \
               voter_names, voter_roles, voter_positions, random_agendasetter, random_vetoplayer


class OptionsWidget(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setup()
        self.layout()

    def setup(self):
        self.general_options = GeneralOptions()
        self.run_options = RunOptions()
        self.advanced_run_options = AdvancedRunOptions()
        self.visualization_options = VisualizeOptions()

        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.addTab(self.general_options, "General")
        self.tab_widget.addTab(self.run_options, "Run")
        self.tab_widget.addTab(self.advanced_run_options, "Advanced Run")
        self.tab_widget.addTab(self.visualization_options, "Visualization")

        self.tab_widget.setTabPosition(0)

    def layout(self):
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)

    def set_index(self, current, previous):
        """
        List Widget Click Indexing
        """
        ind_old = self.listWidget_selection.indexFromItem(previous).row()
        ind_new = self.listWidget_selection.indexFromItem(current).row()

        self.optionsIndex[ind_old].hide()
        self.optionsIndex[ind_new].show()

    def set_run_options(self, game_table_options):
        """
        Set Run Options for specific GameTable Widget every time tab changes
        """

        """Run Options"""
        self.run_options.spinBox_runs.setValue(game_table_options.runs)
        self.run_options.spinBox_dimensions.setValue(game_table_options.dimensions)

        """method"""
        if game_table_options.method == "grid":
            self.run_options.radioButton_pointGrid.setChecked(True)
        elif game_table_options.method == "random grid":
            self.run_options.radioButton_randomGrid.setChecked(True)
        else:
            self.run_options.radioButton_optimization.setChecked(True)

        """save"""
        if game_table_options.save == "yes":
            self.run_options.radioButton_save_yes.setChecked(True)
        else:
            self.run_options.radioButton_save_no.setChecked(True)

        """visualize"""
        if game_table_options.visualize == "yes":
            self.run_options.radioButton_visualize_yes.setChecked(True)
        else:
            self.run_options.radioButton_visualize_no.setChecked(True)

        """alter Preferences"""
        if game_table_options.alter_preferences == "drift":
            self.run_options.radiobutton_alter_preferences_drift.setChecked(True)

        else:
            self.run_options.radioButton_alter_preferences_no.setChecked(True)

        """alter Status Quo"""
        if game_table_options.alter_statusquo == "history+drift":
            self.run_options.radioButton_alterStatusQuo_historyAndDrift.setChecked(True)

        elif game_table_options.alter_statusquo == "history":
            self.run_options.radioButton_alterStatusQuo_history.setChecked(True)

        elif game_table_options.alter_statusquo == "random":
            self.run_options.radioButton_alterStatusQuo_random.setChecked(True)

        else:
            self.run_options.radioButton_alterStatusQuo_no.setChecked(True)

        """save visualize"""
        if game_table_options.save_visualize == "yes":
            self.run_options.radioButton_saveVisualize_yes.setChecked(True)

        else:
            self.run_options.radioButton_saveVisualize_no.setChecked(True)

        """""""""""""""""""""""
        advanced run options
        """""""""""""""""""""""
        self.advanced_run_options.doubleSpinBox_breaks.setValue(game_table_options.breaks)
        self.advanced_run_options.spinBox_density.setValue(game_table_options.density)

        """distance Type"""
        if game_table_options.distance_type == "euclidean":
            self.advanced_run_options.radioButton_distanceEuclidean.setChecked(True)

        else:
            self.advanced_run_options.radioButton_distanceManhattan.setChecked(True)

        """distribution"""
        if game_table_options.sq_vibration_distribution == "normal":
            self.advanced_run_options.radioButton_distributionNormal.setChecked(True)

        elif game_table_options.sq_vibration_distribution == "uniform":
            self.advanced_run_options.radioButton_distributionUniform.setChecked(True)

        elif game_table_options.sq_vibration_distribution == "pareto":
            self.advanced_run_options.radioButton_distributionPareto.setChecked(True)

        else:
            self.advanced_run_options.radioButton_distributionExponential.setChecked(True)

        """vibrate status quo"""
        if game_table_options.vibrate_sq == "yes":
            self.advanced_run_options.radioButton_vibrate_sq_yes.setChecked(True)
        else:
            self.advanced_run_options.radioButton_vibrate_sq_no.setChecked(True)

    def load_options(self, options):
        """TODO SET RUN OPTIONS IN GAMETABLEWIDGET IN MAIN LOAD FUN"""
        """
        Load all options other than run options here
        """
        self.visualization_options.lineWidthAgendaSetter_SpinBox.setValue(options["agendaSetter_lineWidth"])
        self.visualization_options.opacityAgendaSetter_SpinBox.setValue(options["agendaSetter_opacity"])
        self.visualization_options.sizeAgendaSetter_SpinBox.setValue(options["agendaSetter_size"])
        self.visualization_options.colorAgendaSetter = options["agendaSetter_mainColor"]
        self.visualization_options.colorAgendaSetterCircle = options["agendaSetter_circleColor"]

        self.visualization_options.lineWidthVetoPlayer_SpinBox.setValue(options["vetoPlayer_lineWidth"])
        self.visualization_options.opacityVetoPlayer_SpinBox.setValue(options["vetoPlayer_opacity"])
        self.visualization_options.sizeVetoPlayer_SpinBox.setValue(options["vetoPlayer_size"])
        self.visualization_options.colorVetoPlayer = options["vetoPlayer_mainColor"]
        self.visualization_options.colorVetoPlayerCircle = options["vetoPlayer_circleColor"]

        self.visualization_options.lineWidthNormalVoter_SpinBox.setValue(options["normalVoter_lineWidth"])
        self.visualization_options.opacityNormalVoter_SpinBox.setValue(options["normalVoter_opacity"])
        self.visualization_options.sizeNormalVoter_SpinBox.setValue(options["normalVoter_size"])
        self.visualization_options.colorNormalVoter = options["normalVoter_mainColor"]
        self.visualization_options.colorNormalVoterCircle = options["normalVoter_circleColor"]

        self.visualization_options.lineWidthTracer_SpinBox.setValue(options["traceLine_lineWidth"])
        self.visualization_options.opacityTracer_SpinBox.setValue(options["traceLine_opacity"])
        self.visualization_options.colorTracer = options["traceLine_color"]

        self.visualization_options.lineWidthWinset_SpinBox.setValue(options["winset_lineWidth"])
        self.visualization_options.opacityWinset_SpinBox.setValue(options["winset_opacity"])
        self.visualization_options.colorWinset = options["winset_color"]

        if options["plotTotalChange"] == "yes":
            self.visualization_options.radioButton_traceTotalChange_Yes.setChecked(True)
        elif options["plotTotalChange"] == "no":
            self.visualization_options.radioButton_traceTotalChange_No.setChecked(True)
        else:
            self.visualization_options.radioButton_traceTotalChange_Separate.setChecked(True)

        if options["plotRoleArray"] == "yes":
            self.visualization_options.radioButton_plotRoleArray_Yes.setChecked(True)
        elif options["plotRoleArray"] == "no":
            self.visualization_options.radioButton_plotRoleArray_No.setChecked(True)
        else:
            self.visualization_options.radioButton_plotRoleArray_Separate.setChecked(True)

        self.visualization_options.button_bgcolor_init()

    def save_options(self):
        """
        Save current settings and voter setup
        """
        save = {"visualization_settings": {
            "agendaSetter_lineWidth": self.visualization_options.lineWidthAgendaSetter_SpinBox.value(),
            "agendaSetter_opacity": self.visualization_options.opacityAgendaSetter_SpinBox.value(),
            "agendaSetter_size": self.visualization_options.sizeAgendaSetter_SpinBox.value(),
            "agendaSetter_mainColor": self.visualization_options.colorAgendaSetter,
            "agendaSetter_circleColor": self.visualization_options.colorAgendaSetterCircle,

            "vetoPlayer_lineWidth": self.visualization_options.lineWidthVetoPlayer_SpinBox.value(),
            "vetoPlayer_opacity": self.visualization_options.opacityVetoPlayer_SpinBox.value(),
            "vetoPlayer_size": self.visualization_options.sizeVetoPlayer_SpinBox.value(),
            "vetoPlayer_mainColor": self.visualization_options.colorVetoPlayer,
            "vetoPlayer_circleColor": self.visualization_options.colorVetoPlayerCircle,

            "normalVoter_lineWidth": self.visualization_options.lineWidthNormalVoter_SpinBox.value(),
            "normalVoter_opacity": self.visualization_options.opacityNormalVoter_SpinBox.value(),
            "normalVoter_size": self.visualization_options.sizeNormalVoter_SpinBox.value(),
            "normalVoter_mainColor": self.visualization_options.colorNormalVoter,
            "normalVoter_circleColor": self.visualization_options.colorNormalVoterCircle,

            "traceLine_lineWidth": self.visualization_options.lineWidthTracer_SpinBox.value(),
            "traceLine_opacity": self.visualization_options.opacityTracer_SpinBox.value(),
            "traceLine_color": self.visualization_options.colorTracer,

            "winset_lineWidth": self.visualization_options.lineWidthWinset_SpinBox.value(),
            "winset_opacity": self.visualization_options.opacityWinset_SpinBox.value(),
            "winset_color": self.visualization_options.colorWinset,

            "plotTotalChange": self.visualization_options.buttonGroup_traceTotalChange.checkedButton().text().lower(),
            "plotRoleArray": self.visualization_options.buttonGroup_plotRoleArray.checkedButton().text().lower()
        }
        }

        return save


# with open(os.path.join(self.var_save_dir, "config.txt"), "w") as f:
#            json.dump(save, f)


class GeneralOptions(QtWidgets.QWidget):
    """
    General Options
    """

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setup()
        self.set_layout()

        self.outputDir = None
        self.visualizationDir = None
        self.configDir = None

    def setup(self):
        """
        Setup Textedits
        """
        self.lineEdit_outputDir = QtWidgets.QLineEdit()
        self.lineEdit_visualizationDir = QtWidgets.QLineEdit()
        self.lineEdit_configDir = QtWidgets.QLineEdit()

        self.pushButton_outputDir = QtWidgets.QPushButton("Set")
        self.pushButton_outputDir.clicked.connect(self.set_output_dir)

        self.pushButton_visualizationDir = QtWidgets.QPushButton("Set")
        self.pushButton_visualizationDir.clicked.connect(self.set_visualization_dir)

        self.pushButton_configDir = QtWidgets.QPushButton("Set")
        self.pushButton_configDir.clicked.connect(self.set_config_dir)

    def set_layout(self):
        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignLeft)

        groupbox_output_dir = QtWidgets.QGroupBox("Savefile Directory")
        output_hbox = QtWidgets.QHBoxLayout()
        output_hbox.addWidget(self.lineEdit_outputDir)
        output_hbox.addWidget(self.pushButton_outputDir)
        groupbox_output_dir.setLayout(output_hbox)

        layout.addWidget(groupbox_output_dir)

        groupbox_visualization_dir = QtWidgets.QGroupBox("Visualization Directory")
        visualization_hbox = QtWidgets.QHBoxLayout()
        visualization_hbox.addWidget(self.lineEdit_visualizationDir)
        visualization_hbox.addWidget(self.pushButton_visualizationDir)
        groupbox_visualization_dir.setLayout(visualization_hbox)

        layout.addWidget(groupbox_visualization_dir)

        group_box_config_dir = QtWidgets.QGroupBox("Startup File Directory")
        config_hbox = QtWidgets.QHBoxLayout()
        config_hbox.addWidget(self.lineEdit_configDir)
        config_hbox.addWidget(self.pushButton_configDir)
        group_box_config_dir.setLayout(config_hbox)

        layout.addWidget(group_box_config_dir)
        layout.addStretch(1)

        self.setLayout(layout)

    def set_config_dir(self):
        self.lineEdit_configDir.setText(QtWidgets.QFileDialog.getExistingDirectory())

    def set_visualization_dir(self):
        self.lineEdit_visualizationDir.setText(QtWidgets.QFileDialog.getExistingDirectory())

    def set_output_dir(self):
        self.lineEdit_outputDir.setText(QtWidgets.QFileDialog.getExistingDirectory())


class RunOptions(QtWidgets.QWidget):
    """
    Basic Options
    """

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setup()
        self.set_layout()

    def setup(self):
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

        self.spinBox_density = QtWidgets.QSpinBox()
        self.spinBox_density.setMinimum(1)

        """""""""""
        Setup Radiobuttons
        """""""""""
        """""""""""
        Method
        """""""""""
        self.buttonGroup_method = QtWidgets.QButtonGroup()
        self.radioButton_pointGrid = QtWidgets.QRadioButton("Grid")
        self.radioButton_optimization = QtWidgets.QRadioButton("Optimization")
        self.radioButton_randomGrid = QtWidgets.QRadioButton("Random Grid")
        self.radioButton_pointGrid.setChecked(True)
        self.buttonGroup_method.addButton(self.radioButton_pointGrid)
        self.buttonGroup_method.addButton(self.radioButton_optimization)
        self.buttonGroup_method.addButton(self.radioButton_randomGrid)

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
        Visualize Save
        """""""""""
        self.buttonGroup_saveVisualize = QtWidgets.QButtonGroup()
        self.radioButton_saveVisualize_yes = QtWidgets.QRadioButton("Yes")
        self.radioButton_saveVisualize_no = QtWidgets.QRadioButton("No")
        self.radioButton_saveVisualize_yes.setChecked(True)
        self.buttonGroup_saveVisualize.addButton(self.radioButton_saveVisualize_yes)
        self.buttonGroup_saveVisualize.addButton(self.radioButton_saveVisualize_no)

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
        self.buttongroup_alter_preferences = QtWidgets.QButtonGroup()
        self.radiobutton_alter_preferences_drift = QtWidgets.QRadioButton("Drift")
        self.radioButton_alter_preferences_no = QtWidgets.QRadioButton("No")
        self.radioButton_alter_preferences_no.setChecked(True)
        self.buttongroup_alter_preferences.addButton(self.radiobutton_alter_preferences_drift)
        self.buttongroup_alter_preferences.addButton(self.radioButton_alter_preferences_no)

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

    def set_layout(self):
        layout = QtWidgets.QVBoxLayout(self)

        """""""""""
        General
        """""""""""
        group_box_general = QtWidgets.QGroupBox("General")

        spin_box_vbox = QtWidgets.QVBoxLayout()

        for widget in [self.spinbox_setup(spinBox, label) for
                       spinBox, label in zip(
                [self.spinBox_runs, self.spinBox_dimensions], ["Runs", "Dimensions"])]:
            spin_box_vbox.addLayout(widget)

        group_box_general.setLayout(spin_box_vbox)

        layout.addWidget(group_box_general)

        """""""""""
        Method
        """""""""""
        group_box_method = QtWidgets.QGroupBox("Method")

        method_hbox = QtWidgets.QHBoxLayout()

        for widget in [self.radioButton_pointGrid, self.radioButton_randomGrid, self.radioButton_optimization]:
            method_hbox.addWidget(widget)

        group_box_method.setLayout(method_hbox)

        layout.addWidget(group_box_method)

        """""""""""
        Save
        """""""""""
        group_box_save = QtWidgets.QGroupBox("Save")

        save_hbox = QtWidgets.QHBoxLayout()

        for widget in [self.radioButton_save_yes, self.radioButton_save_no]:
            save_hbox.addWidget(widget)

        group_box_save.setLayout(save_hbox)

        layout.addWidget(group_box_save)

        """""""""""
        Visualize
        """""""""""
        group_box_visualize = QtWidgets.QGroupBox("Visualize")

        visualization_hbox = QtWidgets.QHBoxLayout()

        for widget in [self.radioButton_visualize_yes, self.radioButton_visualize_no]:
            visualization_hbox.addWidget(widget)

        group_box_visualize.setLayout(visualization_hbox)

        layout.addWidget(group_box_visualize)

        """""""""""
        Save Visualize
        """""""""""
        group_box_save_visualize = QtWidgets.QGroupBox("Save Plots")

        save_visualize_hbox = QtWidgets.QHBoxLayout()

        for widget in [self.radioButton_saveVisualize_yes, self.radioButton_saveVisualize_no]:
            save_visualize_hbox.addWidget(widget)

        group_box_save_visualize.setLayout(save_visualize_hbox)

        layout.addWidget(group_box_save_visualize)

        """""""""""
        Alter Preferences
        """""""""""
        group_box_alter_preferences = QtWidgets.QGroupBox("Alter Preferences")

        alter_preferences_hbox = QtWidgets.QHBoxLayout()

        for widget in [self.radiobutton_alter_preferences_drift, self.radioButton_alter_preferences_no]:
            alter_preferences_hbox.addWidget(widget)

        group_box_alter_preferences.setLayout(alter_preferences_hbox)

        layout.addWidget(group_box_alter_preferences)

        """""""""""
        Alter Status Quo
        """""""""""
        group_box_alter_status_quo = QtWidgets.QGroupBox("Alter Status Quo")

        alter_status_quo_vbox = self.radiobutton_setup(
            [self.radioButton_alterStatusQuo_historyAndDrift, self.radioButton_alterStatusQuo_history,
             self.radioButton_alterStatusQuo_random, self.radioButton_alterStatusQuo_no], 2)

        group_box_alter_status_quo.setLayout(alter_status_quo_vbox)

        layout.addWidget(group_box_alter_status_quo)

        """Set Layout"""
        layout.setAlignment(QtCore.Qt.AlignLeft)
        layout.addStretch(1)

    #        self.setLayout(layout)

    @staticmethod
    def radiobutton_setup(buttons, rows, label=None):
        vbox = QtWidgets.QVBoxLayout()
        vbox.setAlignment(QtCore.Qt.AlignLeft)

        if label is not None:
            vbox.addWidget(label)

        if rows == 1:
            hbox = QtWidgets.QHBoxLayout()

            for i, button in enumerate(buttons):
                hbox.addWidget(button)

            vbox.addLayout(hbox)

        elif rows == 2:
            grid = QtWidgets.QGridLayout()
            for i, button in enumerate(buttons[:2]):
                grid.addWidget(button, 0, i)

            for i, button in enumerate(buttons[2:]):
                grid.addWidget(button, 1, i)

            vbox.addLayout(grid)

        return vbox

    @staticmethod
    def spinbox_setup(spin_box, label):
        layout = QtWidgets.QVBoxLayout()

        label = QtWidgets.QLabel(label)
        label.setAlignment(QtCore.Qt.AlignBottom)

        layout.addWidget(label)
        layout.addWidget(spin_box)

        return layout


class AdvancedRunOptions(QtWidgets.QWidget):
    """
    Advanced Options
    """

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setup()
        self.layout()

    def setup(self):
        self.doubleSpinBox_breaks = QtWidgets.QDoubleSpinBox()
        self.doubleSpinBox_breaks.setDecimals(4)
        self.doubleSpinBox_breaks.setSingleStep(0.0001)
        self.doubleSpinBox_breaks.setValue(0.01)
        self.doubleSpinBox_breaks.setMinimum(0.0001)

        self.spinBox_density = QtWidgets.QDoubleSpinBox()
        self.spinBox_density.setDecimals(2)
        self.spinBox_density.setMinimum(0.01)

        """""""""""
        Status Quo Vibration
        """""""""""
        self.buttongroup_statusquo_vibration = QtWidgets.QButtonGroup()
        self.radioButton_vibrate_sq_yes = QtWidgets.QRadioButton("Yes")
        self.radioButton_vibrate_sq_no = QtWidgets.QRadioButton("no")
        self.buttongroup_statusquo_vibration.addButton(self.radioButton_vibrate_sq_yes)
        self.buttongroup_statusquo_vibration.addButton(self.radioButton_vibrate_sq_no)

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
        self.buttongroup_distance_type = QtWidgets.QButtonGroup()
        self.radioButton_distanceEuclidean = QtWidgets.QRadioButton("Euclidean")
        self.radioButton_distanceEuclidean.setChecked(True)
        self.radioButton_distanceManhattan = QtWidgets.QRadioButton("Manhattan")
        self.buttongroup_distance_type.addButton(self.radioButton_distanceEuclidean)
        self.buttongroup_distance_type.addButton(self.radioButton_distanceManhattan)

    def layout(self):
        layout = QtWidgets.QVBoxLayout(self)

        """
        Grid Options
        """
        group_box_grid_options = QtWidgets.QGroupBox("Grid Options")

        spin_box_vbox = QtWidgets.QVBoxLayout()

        for widget in [self.spinbox_setup(spinBox, label) for
                       spinBox, label in zip(
                [self.doubleSpinBox_breaks, self.spinBox_density], ["Grid - Breaks", "Random Grid - Density"])]:
            spin_box_vbox.addLayout(widget)

        group_box_grid_options.setLayout(spin_box_vbox)

        layout.addWidget(group_box_grid_options)

        """
        Status Quo Vibration
        """
        group_box_statusquo_vibration = QtWidgets.QGroupBox("Vibrate Status Quo")

        sq_vibration_vbox = self.radiobutton_setup(
            [self.radioButton_vibrate_sq_yes, self.radioButton_vibrate_sq_no], 1)

        group_box_statusquo_vibration.setLayout(sq_vibration_vbox)

        layout.addWidget(group_box_statusquo_vibration)

        """""""""""
        Distribution
        """""""""""
        group_box_distribution = QtWidgets.QGroupBox("Vibration Distribution")

        distribution_vbox = self.radiobutton_setup(
            [self.radioButton_distributionNormal, self.radioButton_distributionUniform,
             self.radioButton_distributionPareto, self.radioButton_distributionExponential], 2)

        group_box_distribution.setLayout(distribution_vbox)

        layout.addWidget(group_box_distribution)

        """""""""""
        Distance Type
        """""""""""
        group_box_distance_type = QtWidgets.QGroupBox("Distance Type")

        distance_type_vbox = self.radiobutton_setup(
            [self.radioButton_distanceEuclidean, self.radioButton_distanceManhattan], 1)

        group_box_distance_type.setLayout(distance_type_vbox)

        layout.addWidget(group_box_distance_type)

        """Set Layout"""

        layout.setAlignment(QtCore.Qt.AlignLeft)
        layout.addStretch(1)

    #        self.setLayout(layout)

    @staticmethod
    def spinbox_setup(spin_box, label):
        layout = QtWidgets.QVBoxLayout()

        label = QtWidgets.QLabel(label)
        label.setAlignment(QtCore.Qt.AlignBottom)

        layout.addWidget(label)
        layout.addWidget(spin_box)

        return layout

    @staticmethod
    def radiobutton_setup(buttons, rows, label=None):
        vbox = QtWidgets.QVBoxLayout()
        vbox.setAlignment(QtCore.Qt.AlignLeft)

        if label is not None:
            vbox.addWidget(label)

        if rows == 1:
            hbox = QtWidgets.QHBoxLayout()

            for i, button in enumerate(buttons):
                hbox.addWidget(button)

            vbox.addLayout(hbox)

        elif rows == 2:
            grid = QtWidgets.QGridLayout()
            for i, button in enumerate(buttons[:2]):
                grid.addWidget(button, 0, i)

            for i, button in enumerate(buttons[2:]):
                grid.addWidget(button, 1, i)

            vbox.addLayout(grid)

        return vbox


# noinspection PyUnresolvedReferences
class VisualizeOptions(QtWidgets.QWidget):
    """
    Visualization Options
    """

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setup()
        self.set_layout()

    def setup(self):
        """""""""""
        Plot Colors
        """""""""""
        self.colorVetoPlayer = "#d62728"
        self.colorNormalVoter = "#6d6c6c"
        self.colorAgendaSetter = "#1f77b4"
        self.colorStatusQuo = "#8c564b"
        self.colorOutcome = "#ff7f0e"
        self.colorVetoPlayerCircle = "#d62728"
        self.colorNormalVoterCircle = "#6d6c6c"
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
        self.colorAgendaSetter_Button.clicked.connect(self.set_agenda_color)

        self.colorAgendaSetterCircle_Button = QtWidgets.QPushButton()
        self.colorAgendaSetterCircle_Button.clicked.connect(self.set_agenda_circle_color)

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
        self.colorVetoPlayer_Button.clicked.connect(self.set_veto_color)

        self.colorVetoPlayerCircle_Button = QtWidgets.QPushButton()
        self.colorVetoPlayerCircle_Button.clicked.connect(self.set_veto_circle_color)

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
        self.colorNormalVoter_Button.clicked.connect(self.set_normal_color)

        self.colorNormalVoterCircle_Button = QtWidgets.QPushButton()
        self.colorNormalVoterCircle_Button.clicked.connect(self.set_normal_circle_color)

        """""""""""
        Status Quo
        """""""""""
        self.sizeStatusQuo_SpinBox = QtWidgets.QSpinBox()
        self.sizeStatusQuo_SpinBox.setValue(60)

        self.colorStatusQuo_Button = QtWidgets.QPushButton()
        self.colorStatusQuo_Button.clicked.connect(self.set_statusquo_color)

        """""""""""
        Outcome
        """""""""""
        self.sizeOutcome_SpinBox = QtWidgets.QSpinBox()
        self.sizeOutcome_SpinBox.setValue(60)

        self.colorOutcome_Button = QtWidgets.QPushButton()
        self.colorOutcome_Button.clicked.connect(self.set_statusquo_color)

        """""""""""
        Trace Line
        """""""""""
        self.lineWidthTracer_SpinBox = QtWidgets.QSpinBox()
        self.lineWidthTracer_SpinBox.setValue(1)

        self.opacityTracer_SpinBox = QtWidgets.QSpinBox()
        self.opacityTracer_SpinBox.setValue(50)

        self.colorTracer_Button = QtWidgets.QPushButton()
        self.colorTracer_Button.clicked.connect(self.set_tracer_color)

        """""""""""
        Winset
        """""""""""
        self.lineWidthWinset_SpinBox = QtWidgets.QSpinBox()
        self.lineWidthWinset_SpinBox.setValue(1)

        self.opacityWinset_SpinBox = QtWidgets.QSpinBox()
        self.opacityWinset_SpinBox.setValue(50)

        self.colorWinset_Button = QtWidgets.QPushButton()
        self.colorWinset_Button.clicked.connect(self.set_winset_color)

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

        self.button_bgcolor_init()

    def button_bgcolor_init(self):
        """""""""""
        Button BG Color Init
        """""""""""
        for button, color in zip(
                [self.colorVetoPlayer_Button, self.colorNormalVoter_Button, self.colorAgendaSetter_Button,
                 self.colorStatusQuo_Button,
                 self.colorOutcome_Button, self.colorVetoPlayerCircle_Button, self.colorNormalVoterCircle_Button,
                 self.colorAgendaSetterCircle_Button, self.colorWinset_Button, self.colorTracer_Button],
                [self.colorVetoPlayer, self.colorNormalVoter, self.colorAgendaSetter, self.colorStatusQuo,
                 self.colorOutcome,
                 self.colorVetoPlayerCircle, self.colorNormalVoterCircle, self.colorAgendaSetterCircle,
                 self.colorWinset, self.colorTracer]):
            self.set_bg(button, color)

    def set_layout(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignLeft)

        """""""""""
        Players
        """""""""""
        group_box_players = QtWidgets.QGroupBox("Players")

        players_grid = QtWidgets.QGridLayout()
        players_grid.setAlignment(QtCore.Qt.AlignLeft)

        [players_grid.addWidget(widget, 0, i + 1) for i, widget in
         enumerate([self.label_lineWidth, self.label_opacity, self.label_size,
                    self.label_color, self.label_colorCircle])]

        [players_grid.addWidget(widget, 1, i) for i, widget in
         enumerate([self.label_agendaSetter, self.lineWidthAgendaSetter_SpinBox,
                    self.opacityAgendaSetter_SpinBox, self.sizeAgendaSetter_SpinBox, self.colorAgendaSetter_Button,
                    self.colorAgendaSetterCircle_Button])]

        [players_grid.addWidget(widget, 2, i) for i, widget in
         enumerate([self.label_vetoPlayer, self.lineWidthVetoPlayer_SpinBox,
                    self.opacityVetoPlayer_SpinBox, self.sizeVetoPlayer_SpinBox, self.colorVetoPlayer_Button,
                    self.colorVetoPlayerCircle_Button])]

        [players_grid.addWidget(widget, 3, i) for i, widget in
         enumerate([self.label_normalVoter, self.lineWidthNormalVoter_SpinBox,
                    self.opacityNormalVoter_SpinBox, self.sizeNormalVoter_SpinBox, self.colorNormalVoter_Button,
                    self.colorNormalVoterCircle_Button])]

        group_box_players.setLayout(players_grid)

        layout.addWidget(group_box_players)

        """""""""""
        Objects
        """""""""""
        group_box_objects = QtWidgets.QGroupBox("Objects")

        objects_grid = QtWidgets.QGridLayout()

        [objects_grid.addWidget(widget, 0, i + 1) for i, widget in
         enumerate([self.label2_lineWidth, self.label2_opacity, self.label2_color])]

        [objects_grid.addWidget(widget, 1, i) for i, widget in
         enumerate([self.label_trace, self.lineWidthTracer_SpinBox,
                    self.opacityTracer_SpinBox, self.colorTracer_Button])]

        [objects_grid.addWidget(widget, 2, i) for i, widget in
         enumerate([self.label_winset, self.lineWidthWinset_SpinBox,
                    self.opacityWinset_SpinBox, self.colorWinset_Button])]

        group_box_objects.setLayout(objects_grid)

        layout.addWidget(group_box_objects)

        """""""""""
        Additional Plots
        """""""""""
        group_box_plot_total_change = QtWidgets.QGroupBox("Plot Total Change")

        plot_total_change_hbox = QtWidgets.QHBoxLayout()
        [plot_total_change_hbox.addWidget(widget) for widget in [
            self.radioButton_traceTotalChange_Yes, self.radioButton_traceTotalChange_Separate,
            self.radioButton_traceTotalChange_No]]

        group_box_plot_total_change.setLayout(plot_total_change_hbox)

        layout.addWidget(group_box_plot_total_change)

        group_box_plot_role_array = QtWidgets.QGroupBox("Plot Role Array")

        plot_role_array_hbox = QtWidgets.QHBoxLayout()

        [plot_role_array_hbox.addWidget(widget) for widget in [
            self.radioButton_plotRoleArray_Yes, self.radioButton_plotRoleArray_Separate,
            self.radioButton_plotRoleArray_No]]

        group_box_plot_role_array.setLayout(plot_role_array_hbox)

        layout.addWidget(group_box_plot_role_array)

        layout.addStretch(1)
        self.setLayout(layout)

    def label_vbox(self, widget, label):
        """
        VBox for Label over Widget
        """
        vbox = QtWidgets.QVBoxLayout(self)

        label = QtWidgets.QLabel(label)
        label.setAlignment(QtCore.Qt.AlignLeft)

        vbox.addWidget(label)
        vbox.addWidget(widget)

        return vbox

    def radiobutton_setup(self, buttons, rows, label=None):
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

    def set_normal_color(self):
        color = self.color_picker(self.colorNormalVoter_Button)
        if color is not None:
            self.colorNormalVoter = color.name()

    def set_veto_color(self):
        color = self.color_picker(self.colorVetoPlayer_Button)
        if color is not None:
            self.colorVetoPlayer = color.name()

    def set_agenda_color(self):
        color = self.color_picker(self.colorAgendaSetter_Button)
        if color is not None:
            self.colorAgendaSetter = color.name()

    def set_statusquo_color(self):
        color = self.color_picker(self.colorStatusQuo_Button)
        if color is not None:
            self.colorStatusQuo = color.name()

    def set_normal_circle_color(self):
        color = self.color_picker(self.colorNormalVoterCircle_Button)
        if color is not None:
            self.colorNormalVoterCircle = color.name()

    def set_veto_circle_color(self):
        color = self.color_picker(self.colorVetoPlayerCircle_Button)
        if color is not None:
            self.colorVetoPlayerCircle = color.name()

    def set_agenda_circle_color(self):
        color = self.color_picker(self.colorAgendaSetterCircle_Button)
        if color is not None:
            self.colorAgendaSetterCircle = color.name()

    def set_winset_color(self):
        color = self.color_picker(self.colorWinset_Button)
        if color is not None:
            self.colorWinset = color.name()

    def set_tracer_color(self):
        color = self.color_picker(self.colorTracer_Button)
        if color is not None:
            self.colorTracer = color.name()

    def color_picker(self, button):
        color = QtWidgets.QColorDialog.getColor()
        if not color.isValid():
            return
        button.setStyleSheet("background-color: {0}".format(color.name()))

    def set_bg(self, button, color):
        button.setStyleSheet("background-color: {0}".format(color))


class VisualizeCanvas(FigureCanvas):
    """
    Backend Canvas (see https://matplotlib.org/examples/user_interfaces/embedding_in_qt4.html)
    """

    def __init__(self, parent=None, width=5.4, height=4, dpi=100, dimensions=2):
        if dimensions == 1 or dimensions == 2:
            self.fig = Figure(figsize=(width, height), dpi=dpi)

            self.axes = self.fig.add_subplot(111, aspect="equal", position=[0.15, 0.15, 0.75, 0.75])

        self.fig.set_facecolor("none")
        self.fig.set_tight_layout(True)
        #        self.axes.set_axis_bgcolor("none")

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


class VisualizeDockWidget(QtWidgets.QWidget):
    """
    Matplotlib Viewer for Image Output
    """

    def __init__(self, parent=None):
        super(VisualizeDockWidget, self).__init__(parent)
        self.setup()
        self.set_layout()

    def setup(self):
        self.canvas = VisualizeCanvas()
        self.pushButton_next = QtWidgets.QPushButton()
        self.pushButton_next.setIcon(QtGui.QIcon("./assets/iconArrowRight.png"))

        self.pushButton_prev = QtWidgets.QPushButton()
        self.pushButton_prev.setIcon(QtGui.QIcon("./assets/iconArrowLeft.png"))

        self.toolbar = NavigationToolbar(self.canvas, self)

    def set_layout(self):
        layout = QtWidgets.QVBoxLayout()

        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        button_hbox = QtWidgets.QHBoxLayout()
        button_hbox.addStretch(1)
        button_hbox.addWidget(self.pushButton_prev)
        button_hbox.addWidget(self.pushButton_next)
        button_hbox.addStretch(1)

        layout.addLayout(button_hbox)

        self.setLayout(layout)

    def adjust_axes(self, dimension):
        if dimension == 1:
            self.canvas.fig.set_size_inches(7, 3)
            self.canvas.updateGeometry()

        if dimension == 2:
            self.canvas.fig.set_size_inches(7, 5)
            print("set new canvas")


# self.canvas.updateGeometry()


class LogDockWidget(QtWidgets.QTextEdit):
    def __init__(self, parent):
        super(LogDockWidget, self).__init__(parent)
        self.setDisabled(True)
        self.setup()
        self.set_layout()

    def setup(self):
        #        self.log = QtWidgets.QTextEdit()
        #        self.log.setDisabled(True)
        pass

    def set_layout(self):
        #        layout = QtWidgets.QVBoxLayout()
        #        layout.addWidget(self.log)
        #        self.setLayout(layout)
        pass


# noinspection PyUnresolvedReferences
class ManifestoPyDockWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super(ManifestoPyDockWidget, self).__init__(parent)
        self.setup()
        self.set_layout()

        self.api_connected = False

    def setup(self):
        """
        Setup Widgets + Signals
        """
        self.connect_GroupBox = QtWidgets.QGroupBox("Connect to Manifesto Project API")

        self.lineEdit_APIkey = QtWidgets.QLineEdit()
        self.lineEdit_APIkey.setEchoMode(QtWidgets.QLineEdit.Password)

        self.pushButton_APIconnect = QtWidgets.QPushButton("Connect")
        self.pushButton_APIconnect.clicked.connect(self.api_connect)

        self.listWidget_APIcountry = QtWidgets.QListWidget()
        self.listWidget_APIcountry.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.listWidget_APIcountry.itemDoubleClicked.connect(self.manifesto_api_country)

        self.listWidget_APIparty = QtWidgets.QListWidget()
        self.listWidget_APIparty.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.listWidget_APIparty.selectionModel().selectionChanged.connect(self.manifesto_api_add_issues)

        self.listWidget_APIparty = QtWidgets.QListWidget()
        self.listWidget_APIparty.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.listWidget_APIyear = QtWidgets.QListWidget()
        self.listWidget_APIyear.selectionModel().selectionChanged.connect(self.manifesto_api_year)

        self.listWidget_APIissue = QtWidgets.QListWidget()
        self.listWidget_APIissue.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.listWidget_APIissue.selectionModel().selectionChanged.connect(self.manifesto_api_add_years)

    #        self.pushButton_APIadd = QtWidgets.QPushButton("Add")

    def set_layout(self):
        """
        Layout
        """
        layout = QtWidgets.QHBoxLayout(self)

        self.connect_hbox = QtWidgets.QHBoxLayout()
        self.connect_hbox.addStretch(1)

        connect_vbox = QtWidgets.QVBoxLayout()
        connect_vbox.setAlignment(QtCore.Qt.AlignCenter)
        connect_vbox.addWidget(self.lineEdit_APIkey)
        connect_vbox.addWidget(self.pushButton_APIconnect)

        self.connect_hbox.addLayout(connect_vbox)
        self.connect_hbox.addStretch(1)
        layout.addLayout(self.connect_hbox)

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)

        for widget in [self.listWidget_APIcountry, self.listWidget_APIparty, self.listWidget_APIissue,
                       self.listWidget_APIyear]:
            self.splitter.addWidget(widget)

        layout.addWidget(self.splitter)
        self.splitter.hide()

        self.setLayout(layout)

    def sizeHint(self):
        return QtCore.QSize(100, 100)

    def api_connect(self):
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

        self.pushButton_APIconnect.hide()
        self.splitter.show()

    def manifesto_api_year(self):
        """
        Get the year selected in the Manifesto API year list widget
        """
        self.year = self.listWidget_APIyear.currentItem().text()

    def manifesto_api_add_years(self):
        """
        Add years for which datasets are available for the given party/parties
        to the Manifesto API year list widget
        """
        self.listWidget_APIyear.clear()
        self.issue_selection = [item.text() for item in self.listWidget_APIissue.selectedItems()]
        self.listWidget_APIyear.addItems([str(item)[:10] for item in list(
            self.manifesto_maindf[["edate"] + self.issue_selection][
                self.manifesto_maindf["partyname"].isin(self.party_selection)].
                dropna(axis=0, how="any").iloc[:, 0])])

    def manifesto_api_add_issues(self):
        """
        Add issues for which datasets are available for the given party/parties
        to the Manifesto API list widget
        """
        self.listWidget_APIissue.clear()
        self.party_selection = [item.text() for item in self.listWidget_APIparty.selectedItems()]

        self.listWidget_APIissue.addItems(list(
            self.manifesto_maindf.loc[(self.manifesto_maindf["partyname"].isin(self.party_selection))].
                dropna(how="any", axis=1).iloc[:, 25:-1]))

    def manifesto_api_country(self, item):
        """
        Add countries for which datasets are available to the Manifesto API list widget
        """
        self.listWidget_APIparty.clear()
        self.country = item.text()
        self.listWidget_APIparty.addItems(list(
            self.manifesto_maindf["partyname"][
                self.manifesto_maindf["countryname"] == self.country].sort_values().unique()))


class TableWidget(QtWidgets.QTableWidget):
    """
    QTableWidget Subclass for Custom Context Menu
    """

    def __init__(self, parent=None):
        QtWidgets.QTableWidget.__init__(self, parent)

    def add_row(self):
        self.insertRow(self.rowCount())

    def del_row(self):
        if self.rowCount() > 2:
            self.removeRow(self.rowCount() - 1)
        else:
            return

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu(self)
        add_action = menu.addAction("Add Voter")
        duplicate_action = menu.addAction("Duplicate Voter")  # TODO a
        quit_action = menu.addAction("Remove Voter")
        action = menu.exec_(self.mapToGlobal(event.pos()))

        if action == quit_action:
            indices = self.selectedIndexes()
            for item in indices:
                self.removeRow(item.row())

        elif action == add_action:
            if self.rowCount() == 0:
                self.setRowCount(1)
            else:
                self.insertRow(self.selectedIndexes()[0].row() + 1)

        elif action == duplicate_action:
            pass

        else:
            return


class SimulationVariables:
    def __init__(self, **kwargs):
        """run options"""
        self.votercount = kwargs["votercount"]
        self.method = kwargs["method"]
        self.runs = kwargs["runs"]
        self.dimensions = kwargs["dimensions"]
        self.save = kwargs["save"]
        self.save_visualize = kwargs["save_visualize"]
        self.visualize = kwargs["visualize"]
        self.alter_preferences = kwargs["alter_preferences"]
        self.alter_statusquo = kwargs["alter_statusquo"]

        self.random_agenda_setter = kwargs["random_agenda_setter"]
        self.random_veto_player = kwargs["random_veto_player"]
        
        self.trace = True # TODO a
        self.directory = kwargs["directory"] # TODO b

        self.statusquo_position = kwargs["statusquo_position"]
        self.statusquo_drift = kwargs["statusquo_drift"]
        self.voter_names = kwargs["voter_names"]
        self.voter_roles = kwargs["voter_roles"]
        self.voter_positions = kwargs["voter_positions"]

        self.custom_role_array = kwargs["custom_role_array"] # TODO c

        """adv run options"""
        self.breaks = kwargs["breaks"]
        self.density = kwargs["density"]
        self.distance_type = kwargs["distance_type"]
        self.sq_vibration_distribution = kwargs["sq_vibration_distribution"]
        self.vibrate_sq = kwargs["vibrate_sq"]

class EditableTabBar(QtWidgets.QTabBar):
    def __init__(self, parent):
        QtWidgets.QTabBar.__init__(self, parent)
        self._editor = QtWidgets.QLineEdit(self)
        self._editor.setWindowFlags(QtCore.Qt.Popup)
        self._editor.setFocusProxy(self)
        self._editor.editingFinished.connect(self.handle_editing_finished)
        self._editor.installEventFilter(self)

    def eventFilter(self, widget, event):
        if ((event.type() == QtCore.QEvent.MouseButtonPress and not self._editor.geometry().contains(
                event.globalPos())) or (
                        event.type() == QtCore.QEvent.KeyPress and event.key() == QtCore.Qt.Key_Escape)):
            self._editor.hide()
            return True
        return QtWidgets.QTabBar.eventFilter(self, widget, event)

    def mouseDoubleClickEvent(self, event):
        index = self.tabAt(event.pos())
        if index >= 0:
            self.edit_tab(index)

    def edit_tab(self, index):
        rect = self.tabRect(index)
        self._editor.setFixedSize(rect.size())
        self._editor.move(self.parent().mapToGlobal(rect.topLeft()))
        self._editor.setText(self.tabText(index))
        if not self._editor.isVisible():
            self._editor.show()

    def handle_editing_finished(self):
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
