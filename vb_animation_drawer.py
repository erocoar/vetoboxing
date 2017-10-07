# -*- coding: utf-8 -*-
"""
Created on Fri Jun  9 23:01:32 2017

@author: Frederik
"""
import sys 
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui

class AnimationDrawer(QtWidgets.QWidget): 
    def __init__(self, file, parent = None):
        super(AnimationDrawer, self).__init__(parent)
#        QtWidgets.QWidget.__init__(self, parent)
        print(file)
        
        self.setGeometry(50, 50, 650, 400)
        self.setWindowTitle('Animation')
        
        self.screen = QtWidgets.QLabel()
        self.screen.setSizePolicy(QtWidgets.QSizePolicy.Expanding, 
            QtWidgets.QSizePolicy.Expanding)        
        self.screen.setAlignment(QtCore.Qt.AlignCenter)
        
        stop_icon = QtGui.QIcon('stop_button.png')
        playpause_icon = QtGui.QIcon('pauseplay_button.png')
        
        btn_play = QtWidgets.QPushButton('')
        btn_play.clicked.connect(self.start)
        btn_play.setIcon(playpause_icon)
        
        btn_stop = QtWidgets.QPushButton('')
        btn_stop.clicked.connect(self.stop)
        btn_stop.setIcon(stop_icon)
        
        for button in [btn_play, btn_stop]:
            button.setFixedHeight(50)
            button.setFixedWidth(50)
            
        main_layout = QtWidgets.QVBoxLayout() 
        main_layout.addWidget(self.screen)
        
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch(1)
        [button_layout.addWidget(button) for button in [btn_play, btn_stop]]
        button_layout.addStretch(1)
        
        main_layout.addLayout(button_layout)

        self.movie = QtGui.QMovie(file, QtCore.QByteArray(), self)
        
        self.frame_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.frame_slider.setRange(0, self.movie.frameCount())
        self.frame_slider.valueChanged.connect(lambda value: self.movie.jumpToFrame(value))
        self.frame_slider.setProperty('value', 0)

        self.frame_layout = QtWidgets.QHBoxLayout()
        self.frame_layout.addStretch(0)
        self.frame_layout.addWidget(self.frame_slider)
        self.frame_layout.addStretch(0)

        main_layout.addLayout(self.frame_layout)
        
        self.setLayout(main_layout) 

        self.movie.setCacheMode(QtGui.QMovie.CacheAll) 
        self.movie.jumpToFrame(0)
        self.screen.setMovie(self.movie) 
        
        self.movie.frameCount()
        
    def start(self):
        if self.movie.state() == 2:
            self.movie.setPaused(True)
        
        else:
            self.movie.start()
            
        
    def stop(self):
        self.movie.stop()
        self.movie.jumpToFrame(0)
        
def main(folder):      
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    player = AnimationDrawer(folder) 
    player.show() 
#    sys.exit(app.exec_())