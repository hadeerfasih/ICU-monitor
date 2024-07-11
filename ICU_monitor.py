from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QVBoxLayout, QWidget, QMenu, QInputDialog, QMessageBox
from PyQt5.QtCore import  Qt, QTimer, QObject, pyqtSignal, QRect
from PyQt5.QtGui import QPainter, QColor
import pandas as pd
from pyqtgraph import PlotWidget
import math
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Spacer, Paragraph
from reportlab.platypus.flowables import KeepTogether
from reportlab.lib.styles import getSampleStyleSheet

class PlotUpdater(QObject):
    """
        Description:
            - QTimer object to periodically call the plotting function to update the plotted signal.
    """
    update_signal = pyqtSignal(int)

    def __init__(self, position, update_interval):
        super().__init__()
        self.position = position
        self.update_interval = update_interval
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)

    def start(self):
        """
        Description:
            - Start the timer.
        """
        self.timer.start(self.update_interval)

    def stop(self):
        """
        Description:
            - Stops the timer.
        """
        self.timer.stop()

    def set_update_interval(self, interval):
        """
        Description:
            - change the timer interval to change the speed of the running signal.
        """
        self.update_interval = interval
        
    def set_position(self, position):
        """
        Description:
            - To keep track of the index of the fisrt point of the part of the signal that should be displayed.
        """
        self.position = position

    def update(self):
        """
        Description:
            - The function which the timer calls after each update interval.
        """
        # send a pyqt signal with the index of the first point of the part of signal that should be currently displayed 
        self.update_signal.emit(self.position)
        # increament the index 
        self.position += 1 
        
class Overlay(QWidget):
    def __init__(self, side, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 150);")
        self.side= side
        self.animation_timer = QTimer(self)
        self.animation_timer.setInterval(5)  
        self.animation_timer.timeout.connect(self.updateAnimation)
        self.opacity = 0.0
        self.animation_step = 0.1  

    def showOverlay(self):
        if self.side == 'left':
            geometry = QRect((self.parent().geometry().left()), (self.parent().geometry().top()), int((self.parent().geometry().width()) / 2), (self.parent().geometry().height()))
        else:
            geometry = QRect(int((self.parent().geometry().left())  + ((self.parent().geometry().width()) / 2)), (self.parent().geometry().top()), int((self.parent().geometry().width()) / 2), (self.parent().geometry().height()))
        self.setGeometry(geometry)
        self.opacity = 0.0
        self.show()
        self.animation_timer.start()

    def resetOverlay(self):
        self.animation_timer.stop()
        self.opacity = 0.0
        self.hide()

    def updateAnimation(self):
        if self.opacity >= 1.0:
            self.animation_timer.stop()
            self.hide()
        else:
            self.opacity += self.animation_step
            self.repaint()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setOpacity(self.opacity)
        painter.fillRect(self.rect(), QColor(0, 0, 0))
        

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(984, 450)
        MainWindow.setAcceptDrops(False)
        MainWindow.setStyleSheet("font: 10pt \"Arial\";")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        style_sheet = """
            QWidget {
                font-family: Arial, sans-serif;
                font-size: 10pt;
            }
            QPushButton {
                border: 1px solid #8f8f91;
                border-radius: 5px;
                background-color: #e6e6e6;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
            QPushButton:pressed {
                background-color: #d4d4d4;
            }
            QComboBox {
                border: 1px solid #8f8f91;
                border-radius: 5px;
                padding: 1px 18px 1px 3px;
                min-width: 6em;
            }
            QComboBox:editable {
                background: white;
            }
            QComboBox:!editable, QComboBox::drop-down:editable {
                background: #e6e6e6;
            }
            QComboBox:!editable:on, QComboBox::drop-down:editable:on {
                background: #f0f0f0;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left: none; /* Remove the border */
            }
            QComboBox::down-arrow {
                width: 15px;
                height: 15px;
                image: url(down_arrow.png);
            }
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #d4d4d4;
                margin: 2px 0;
                border-radius: 5px;
            }
            QSlider::handle:horizontal {
                background: #8f8f91;
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0;
                border-radius: 5px;
            }
            QCheckBox {
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 13px;
                height: 13px;
                border: 1px solid #8f8f91;
                border-radius: 3px;
            }
            QCheckBox::indicator:unchecked {
                background: #e6e6e6;
            }
            QCheckBox::indicator:checked {
                background: #b1b1b1; 
            }
        """
        # Apply the style sheet to the entire application
        self.centralwidget.setStyleSheet(style_sheet)
        self.gridLayout_3 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.frame_5 = QtWidgets.QFrame(self.centralwidget)
        self.frame_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_5.setObjectName("frame_5")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame_5)
        self.verticalLayout.setObjectName("verticalLayout")
        self.widget = PlotWidget(self.frame_5)
        self.widget.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.widget.setObjectName("widget")
        self.verticalLayout.addWidget(self.widget)
        self.horizontalSlider = QtWidgets.QSlider(self.frame_5)
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.verticalLayout.addWidget(self.horizontalSlider)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.pause_graph1 = QtWidgets.QPushButton(self.frame_5)
        self.pause_graph1.setObjectName("pause_graph1")
        self.horizontalLayout_3.addWidget(self.pause_graph1)
        self.horizontalLayout_3.setStretch(0,1)
        self.zoom_in_graph1 = QtWidgets.QPushButton(self.frame_5)
        self.zoom_in_graph1.setObjectName("zoom_in_graph1")
        self.horizontalLayout_3.addWidget(self.zoom_in_graph1)
        self.horizontalLayout_3.setStretch(1,1)
        self.zoom_out_graph1 = QtWidgets.QPushButton(self.frame_5)
        self.zoom_out_graph1.setObjectName("zoom_out_graph1")
        self.horizontalLayout_3.addWidget(self.zoom_out_graph1)
        self.horizontalLayout_3.setStretch(2,1)
        self.rewind_graph1 = QtWidgets.QPushButton(self.frame_5)
        self.rewind_graph1.setObjectName("rewind_graph1")
        self.horizontalLayout_3.addWidget(self.rewind_graph1)
        self.horizontalLayout_3.setStretch(3,1)
        self.label_4 = QtWidgets.QLabel(self.frame_5)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_3.addWidget(self.label_4)
        self.horizontalLayout_3.setStretch(4,0)
        self.comboBox_speed_graph1 = QtWidgets.QComboBox(self.frame_5)
        self.comboBox_speed_graph1.setObjectName("comboBox_speed_graph1")
        self.comboBox_speed_graph1.addItem("")
        self.comboBox_speed_graph1.addItem("")
        self.comboBox_speed_graph1.addItem("")
        self.comboBox_speed_graph1.addItem("")
        self.horizontalLayout_3.addWidget(self.comboBox_speed_graph1)
        self.horizontalLayout_3.setStretch(5,1)
        self.save_photo_graph1 = QtWidgets.QPushButton(self.frame_5)
        self.save_photo_graph1.setObjectName("save_photo_graph1")
        self.horizontalLayout_3.addWidget(self.save_photo_graph1)
        self.horizontalLayout_3.setStretch(6,1)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_signal = QtWidgets.QLabel(self.frame_5)
        self.label_signal.setObjectName("label_signal")
        self.horizontalLayout_2.addWidget(self.label_signal)
        self.horizontalLayout_2.setStretch(0,0)
        self.comboBox_signals_graph1 = QtWidgets.QComboBox(self.frame_5)
        self.comboBox_signals_graph1.setObjectName("comboBox_signals_graph1")
        self.horizontalLayout_2.addWidget(self.comboBox_signals_graph1)
        self.horizontalLayout_2.setStretch(1,1)
        self.label_change_color_graph1 = QtWidgets.QLabel(self.frame_5)
        self.label_change_color_graph1.setObjectName("label_change_color_graph1")
        self.horizontalLayout_2.addWidget(self.label_change_color_graph1)
        self.horizontalLayout_2.setStretch(2,0)
        self.comboBox_colors_graph1 = QtWidgets.QComboBox(self.frame_5)
        self.comboBox_colors_graph1.setObjectName("comboBox_colors_graph1")
        self.comboBox_colors_graph1.addItem("")
        self.comboBox_colors_graph1.addItem("")
        self.comboBox_colors_graph1.addItem("")
        self.comboBox_colors_graph1.addItem("")
        self.comboBox_colors_graph1.addItem("")
        self.comboBox_colors_graph1.addItem("")
        self.horizontalLayout_2.addWidget(self.comboBox_colors_graph1)
        self.horizontalLayout_2.setStretch(3,1)
        self.addlabel_button1 = QtWidgets.QPushButton(self.frame_5)
        self.addlabel_button1.setObjectName("addlabel_button1")
        self.horizontalLayout_2.addWidget(self.addlabel_button1)
        self.horizontalLayout_2.setStretch(4,1)
        self.pushButton = QtWidgets.QPushButton(self.frame_5)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_2.addWidget(self.pushButton)
        self.horizontalLayout_2.setStretch(5,1)
        self.checkBox_show_graph1 = QtWidgets.QCheckBox(self.frame_5)
        self.checkBox_show_graph1.setObjectName("checkBox_show_graph1")
        self.horizontalLayout_2.addWidget(self.checkBox_show_graph1)
        self.horizontalLayout_2.setStretch(6,0)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_18 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_18.setObjectName("horizontalLayout_18")
        self.checkBox_link = QtWidgets.QCheckBox(self.frame_5)
        self.checkBox_link.setObjectName("checkBox_link")
        self.horizontalLayout_18.addWidget(self.checkBox_link)
        self.verticalLayout.addSpacing(30)
        self.verticalLayout.addLayout(self.horizontalLayout_18)
        self.gridLayout_3.addWidget(self.frame_5, 0, 0, 1, 1)
        self.frame_6 = QtWidgets.QFrame(self.centralwidget)
        self.frame_6.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_6.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_6.setObjectName("frame_6")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame_6)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.widget_2 = PlotWidget(self.frame_6)
        self.widget_2.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.widget_2.setObjectName("widget_2")
        self.verticalLayout_2.addWidget(self.widget_2)
        self.horizontalSlider_2 = QtWidgets.QSlider(self.frame_6)
        self.horizontalSlider_2.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_2.setObjectName("horizontalSlider_2")
        self.verticalLayout_2.addWidget(self.horizontalSlider_2)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.pause_graph2 = QtWidgets.QPushButton(self.frame_6)
        self.pause_graph2.setObjectName("pause_graph2")
        self.horizontalLayout_4.addWidget(self.pause_graph2)
        self.horizontalLayout_4.setStretch(0,1)
        self.zoom_in_graph2 = QtWidgets.QPushButton(self.frame_6)
        self.zoom_in_graph2.setObjectName("zoom_in_graph2")
        self.horizontalLayout_4.addWidget(self.zoom_in_graph2)
        self.horizontalLayout_4.setStretch(1,1)
        self.zoom_out_graph2 = QtWidgets.QPushButton(self.frame_6)
        self.zoom_out_graph2.setObjectName("zoom_out_graph2")
        self.horizontalLayout_4.addWidget(self.zoom_out_graph2)
        self.horizontalLayout_4.setStretch(2,1)
        self.rewind_graph2 = QtWidgets.QPushButton(self.frame_6)
        self.rewind_graph2.setObjectName("rewind_graph2")
        self.horizontalLayout_4.addWidget(self.rewind_graph2)
        self.horizontalLayout_4.setStretch(3,1)
        self.label_3 = QtWidgets.QLabel(self.frame_6)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_4.addWidget(self.label_3)
        self.horizontalLayout_4.setStretch(4,0)
        self.comboBox_speed_graph2 = QtWidgets.QComboBox(self.frame_6)
        self.comboBox_speed_graph2.setObjectName("comboBox_speed_graph2")
        self.comboBox_speed_graph2.addItem("")
        self.comboBox_speed_graph2.addItem("")
        self.comboBox_speed_graph2.addItem("")
        self.comboBox_speed_graph2.addItem("")
        self.horizontalLayout_4.addWidget(self.comboBox_speed_graph2)
        self.horizontalLayout_4.setStretch(5,1)
        self.save_photo_graph2 = QtWidgets.QPushButton(self.frame_6)
        self.save_photo_graph2.setObjectName("save_photo_graph2")
        self.horizontalLayout_4.addWidget(self.save_photo_graph2)
        self.horizontalLayout_4.setStretch(6,1)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_signal2 = QtWidgets.QLabel(self.frame_6)
        self.label_signal2.setObjectName("label_signal2")
        self.horizontalLayout_6.addWidget(self.label_signal2)
        self.horizontalLayout_6.setStretch(0,0)
        self.comboBox_signals_graph2 = QtWidgets.QComboBox(self.frame_6)
        self.comboBox_signals_graph2.setObjectName("comboBox_signals_graph2")
        self.horizontalLayout_6.addWidget(self.comboBox_signals_graph2)
        self.horizontalLayout_6.setStretch(1,1)
        self.label_change_color_graph2 = QtWidgets.QLabel(self.frame_6)
        self.label_change_color_graph2.setObjectName("label_change_color_graph2")
        self.horizontalLayout_6.addWidget(self.label_change_color_graph2)
        self.horizontalLayout_6.setStretch(2,0)
        self.comboBox_colors_graph2 = QtWidgets.QComboBox(self.frame_6)
        self.comboBox_colors_graph2.setObjectName("comboBox_colors_graph2")
        self.comboBox_colors_graph2.addItem("")
        self.comboBox_colors_graph2.addItem("")
        self.comboBox_colors_graph2.addItem("")
        self.comboBox_colors_graph2.addItem("")
        self.comboBox_colors_graph2.addItem("")
        self.comboBox_colors_graph2.addItem("")
        self.horizontalLayout_6.addWidget(self.comboBox_colors_graph2)
        self.horizontalLayout_6.setStretch(3,1)
        self.addlabel_button2 = QtWidgets.QPushButton(self.frame_6)
        self.addlabel_button2.setObjectName("addlabel_button2")
        self.horizontalLayout_6.addWidget(self.addlabel_button2)
        self.horizontalLayout_6.setStretch(4,1)
        self.pushButton_2 = QtWidgets.QPushButton(self.frame_6)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout_6.addWidget(self.pushButton_2)
        self.horizontalLayout_6.setStretch(5,1)
        self.checkBox_show_graph2 = QtWidgets.QCheckBox(self.frame_6)
        self.checkBox_show_graph2.setObjectName("checkBox_show_graph2")
        self.horizontalLayout_6.addWidget(self.checkBox_show_graph2)
        self.horizontalLayout_6.setStretch(6,0)
        self.verticalLayout_2.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_17 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_17.setObjectName("horizontalLayout_17")
        self.horizontalLayout_17.addStretch()
        self.make_report = QtWidgets.QPushButton(self.frame_6)
        self.make_report.setObjectName("make_report")
        self.horizontalLayout_17.addWidget(self.make_report)
        self.verticalLayout_2.addSpacing(15)
        self.verticalLayout_2.addLayout(self.horizontalLayout_17)   
        self.gridLayout_3.addWidget(self.frame_6, 0, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.actionNew = QtWidgets.QAction(MainWindow)
        self.actionNew.setObjectName("actionNew")
        self.action_upload_in_Graph_1 = QtWidgets.QAction(MainWindow)
        self.action_upload_in_Graph_1.setObjectName("action_upload_in_Graph_1")
        self.action_upload_in_Graph_2 = QtWidgets.QAction(MainWindow)
        self.action_upload_in_Graph_2.setObjectName("action_upload_in_Graph_2")
        self.actionMake_Report = QtWidgets.QAction(MainWindow)
        self.actionMake_Report.setObjectName("actionMake_Report")
        self.action_speed_graph1_0_5 = QtWidgets.QAction(MainWindow)
        self.action_speed_graph1_0_5.setObjectName("action_speed_graph1_0.5")
        self.action_speed_graph1_1 = QtWidgets.QAction(MainWindow)
        self.action_speed_graph1_1.setObjectName("action_speed_graph1_1")
        self.action_speed_graph1_1_5 = QtWidgets.QAction(MainWindow)
        self.action_speed_graph1_1_5.setObjectName("action_speed_graph1_1.5")
        self.action_speed_graph1_2 = QtWidgets.QAction(MainWindow)
        self.action_speed_graph1_2.setObjectName("action_speed_graph1_2")
        self.action_speed_graph2_0_5 = QtWidgets.QAction(MainWindow)
        self.action_speed_graph2_0_5.setObjectName("action_speed_graph2_0.5")
        self.action_speed_graph2_1 = QtWidgets.QAction(MainWindow)
        self.action_speed_graph2_1.setObjectName("action_speed_graph2_1")
        self.action_speed_graph2_1_5 = QtWidgets.QAction(MainWindow)
        self.action_speed_graph2_1_5.setObjectName("action_speed_graph2_1.5")
        self.action_speed_graph2_2 = QtWidgets.QAction(MainWindow)
        self.action_speed_graph2_2.setObjectName("action_speed_graph2_2")

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.comboBox_speed_graph1.setCurrentIndex(1)
        self.comboBox_speed_graph2.setCurrentIndex(1)
        self.comboBox_colors_graph1.setCurrentIndex(-1)
        self.comboBox_colors_graph2.setCurrentIndex(-1)
        self.comboBox_speed_graph1.activated.connect(lambda: self.control_plotting_speed(self.comboBox_speed_graph1.currentIndex(), True))
        self.comboBox_speed_graph2.activated.connect(lambda: self.control_plotting_speed(self.comboBox_speed_graph2.currentIndex(), False))
        self.comboBox_signals_graph1.activated.connect(lambda: self.control_single_plot(True))
        self.comboBox_signals_graph2.activated.connect(lambda: self.control_single_plot(False))
        self.comboBox_colors_graph1.activated.connect(lambda: self.change_plot_colour(True))
        self.comboBox_colors_graph2.activated.connect(lambda: self.change_plot_colour(False))
        self.widget_2_plot = self.widget_2.getPlotItem()
        self.widget_plot = self.widget.getPlotItem()
        self.widget_plot.addLegend()
        self.widget_2_plot.addLegend()
        self.magnitude_graph1=[]
        self.magnitude_graph2=[]
        self.plot_updater1 = PlotUpdater(0, 200)
        self.plot_updater1.update_signal.connect(self.get_and_plot_data_in_graph1)
        self.plot_updater2 = PlotUpdater(0, 200)
        self.plot_updater2.update_signal.connect(self.get_and_plot_data_in_graph2)
        self.overlay1 = Overlay('left', self.centralwidget)
        self.overlay2  = Overlay('right',self.centralwidget)
        self.widget.setLabel('left', 'Amplitude')
        self.widget.setLabel('bottom', 'Time (s)')
        self.widget_2.setLabel('left', 'Amplitude')
        self.widget_2.setLabel('bottom', 'Time (s)')
        self.widget.scene().sigMouseClicked.connect(lambda event, flag=True: self.Browse(event, flag))
        self.widget_2.scene().sigMouseClicked.connect(lambda event, flag=False: self.Browse(event, flag))
        self.scale_factor_graph1=1
        self.scale_factor_graph2=1
        self.panning_offset1=0
        self.panning_offset2=0
        self.mouse_click_pos= None
        self.max_pos1=0
        self.max_pos2=0
        self.zoom_in_graph1.clicked.connect(lambda: self.zoom_in(True))
        self.zoom_in_graph2.clicked.connect(lambda: self.zoom_in(False))
        self.zoom_out_graph1.clicked.connect(lambda: self.zoom_out(True))
        self.zoom_out_graph2.clicked.connect(lambda: self.zoom_out(False))
        self.pause_graph1.clicked.connect(lambda: self.pause(True))
        self.pause_graph2.clicked.connect(lambda: self.pause(False))
        self.rewind_graph1.clicked.connect(lambda: self.rewind(True))
        self.rewind_graph2.clicked.connect(lambda: self.rewind(False))
        self.checkBox_link.clicked.connect(self.link)
        self.pushButton.clicked.connect(lambda: self.Move_signals(True))
        self.pushButton_2.clicked.connect(lambda: self.Move_signals(False))
        self.visability1=[]
        self.visability2=[]
        self.checkBox_show_graph1.clicked.connect(lambda: self.change_visibility(True))
        self.checkBox_show_graph2.clicked.connect(lambda: self.change_visibility(False))
        self.checkBox_show_graph1.setCheckState(True)
        self.checkBox_show_graph2.setCheckState(True)
        self.plot_items_graph1=[]
        self.plot_items_graph2=[]
        self.colours1=[]
        self.labels1=[]
        self.colours2=[]
        self.labels2=[]
        self.current_directory = os.path.dirname(os.path.abspath(__file__))
        image_files = [file for file in os.listdir(self.current_directory) if file.lower().endswith(('.png', '.jpg', '.jpeg'))]
        # if there was a snapshots taken from thre previous run of the program left with the script in the same folder delete them (the copy in the folder previous snapshots wont be removed)
        for image_file in image_files:
            snapshot_path = os.path.join(self.current_directory, image_file)
            os.remove(snapshot_path)
        self.widget.mousePressEvent = lambda event:self.start_panning (event, True)
        self.widget.mouseMoveEvent = lambda event:self.trace_panning (event, True)
        self.widget_2.mousePressEvent = lambda event:self.start_panning (event, False)
        self.widget_2.mouseMoveEvent = lambda event:self.trace_panning (event, False)
        self.horizontalSlider.sliderReleased.connect(lambda: self.update_plotting_interval(True))
        self.horizontalSlider_2.sliderReleased.connect(lambda: self.update_plotting_interval(False))
        self.horizontalSlider.sliderPressed.connect(lambda: self.stop(True))
        self.horizontalSlider_2.sliderPressed.connect(lambda: self.stop(False))
        self.addlabel_button1.clicked.connect(lambda: self.Show_pop_up_window(True))
        self.addlabel_button2.clicked.connect(lambda: self.Show_pop_up_window(False))
        self.save_photo_graph1.clicked.connect(lambda: self.snapshot_graph1(self.widget))
        self.save_photo_graph2.clicked.connect(lambda: self.snapshot_graph2(self.widget_2))
        
        self.make_report.clicked.connect(self.make_the_report)
        # List to store snapshots
        self.snapshots1 = [] 

    def Browse(self,event, flag):
        """
        Description:
            - Browse the signal in any of the two graphs.
        Arg: 
            - flag: takes value zero in the desired graph is the second, and value 1 if the desired graph is the first
        """
        if event.double():
            self.filename=QFileDialog.getOpenFileName(filter="csv (*.csv)")[0]
            self.df=pd.read_csv(self.filename,encoding='utf-8').fillna(0)
            self.sampling_frequency= 125
            if flag:
                self.add_browsed_signal(self.magnitude_graph1, self.widget_plot, self.plot_items_graph1, self.colours1, self.labels1, self.visability1, self.comboBox_signals_graph1, self.pause_graph1, self.plot_updater1)
            else:
                self.add_browsed_signal(self.magnitude_graph2, self.widget_2_plot, self.plot_items_graph2, self.colours2, self.labels2, self.visability2, self.comboBox_signals_graph2, self.pause_graph2, self.plot_updater2)
    
    def add_browsed_signal(self, mag_array, plot_widget, plot_items, colours, labels, visability, combobox, pause_button, plot_updater):
        mag_array.append(self.df['Voltage'].values)
        widget_curve= plot_widget.plot(name="plot"+ str(len(self.labels1)) )
        plot_items.append(widget_curve)
        colours.append("red")
        labels.append("plot"+ str(len(labels)))
        visability.append(True)
        combobox.clear()
        for Combobox_it in range (len(labels)):
            combobox.addItem( labels[Combobox_it], userData=Combobox_it)
            combobox.setCurrentIndex(-1)
        if pause_button.text() == "Pause":
            plot_updater.start()

    def get_and_plot_data_in_graph1(self, position):
        if position> self.max_pos1:
            self.max_pos1= position
        self.max1=0
        self.min1= math.inf
        self.minimum1= np.array(self.magnitude_graph1).min()
        self.maximum1= np.array(self.magnitude_graph1).max()
        if position <= len(self.magnitude_graph1[0])- 200:
            for index, volt in enumerate(self.magnitude_graph1):
                y_values=volt[position: position +200]
                max= np.array(y_values).max()
                if max> self.max1:
                    self.max1= max
                min= np.array(y_values).min()
                if min< self.min1:
                    self.min1= min
                x_values=np.linspace(position/ self.sampling_frequency, (position + 200)/self.sampling_frequency, 200)
                self.plot_items_graph1[index].setData(x_values, y_values, name= self.labels1[index])
                self.plot_items_graph1[index].setPen(self.colours1[index])
                self.plot_items_graph1[index].setVisible(self.visability1[index])
                self.update_scrolling_slider_value(True)
            self.widget.setXRange(position/ self.sampling_frequency, (position + 200)/self.sampling_frequency)
            self.widget.setYRange(self.minimum1 *self.scale_factor_graph1 + self.panning_offset1, self.maximum1 *self.scale_factor_graph1 + self.panning_offset1)
        
    def get_and_plot_data_in_graph2(self, position):
        if position> self.max_pos2:
            self.max_pos2= position
        self.max2=0
        self.min2= math.inf
        self.minimum2= np.array(self.magnitude_graph2).min()
        self.maximum2= np.array(self.magnitude_graph2).max()
        if position <= len(self.magnitude_graph2[0])- 200:
            for index, volt in enumerate(self.magnitude_graph2):
                y_values=volt[position: position +200]
                max= np.array(y_values).max()
                if max> self.max2:
                    self.max2= max
                min= np.array(y_values).min()
                if min< self.min2:
                    self.min2= min
                x_values=np.linspace(position/ self.sampling_frequency, (position + 200)/self.sampling_frequency, 200)
                self.plot_items_graph2[index].setData(x_values, y_values, name= self.labels2[index])
                self.plot_items_graph2[index].setPen(self.colours2[index])
                self.plot_items_graph2[index].setVisible(self.visability2[index])
                self.update_scrolling_slider_value(False)
            self.widget_2.setXRange(position/ self.sampling_frequency, (position + 200)/self.sampling_frequency)
            self.widget_2.setYRange(self.minimum2 *self.scale_factor_graph2+ self.panning_offset2, self.maximum2 *self.scale_factor_graph2+ self.panning_offset2)
        
    
    def update_scrolling_slider_value(self, flag):
        if flag:
            self.horizontalSlider.setValue(int(self.plot_updater1.position * self.horizontalSlider.maximum()/ len(self.magnitude_graph1[0])))
        else:
            self.horizontalSlider_2.setValue(int(self.plot_updater2.position * self.horizontalSlider_2.maximum()/ len(self.magnitude_graph2[0])))

    #scroll the signal, forward and backward
    def update_plotting_interval(self, flag):
        if self.checkBox_link.isChecked():
            if flag:
                if int(self.horizontalSlider.value() * len(self.magnitude_graph1[0])/self.horizontalSlider.maximum()) < self.max_pos1:
                    self.plot_updater1.set_position(int(self.horizontalSlider.value() * len(self.magnitude_graph1[0])/self.horizontalSlider.maximum()))  
                    self.plot_updater2.set_position(int(self.horizontalSlider.value() * len(self.magnitude_graph2[0])/self.horizontalSlider.maximum()))  
            else:
                if int(self.horizontalSlider_2.value() * len(self.magnitude_graph2[0])/self.horizontalSlider_2.maximum()) < self.max_pos2:
                    self.plot_updater1.set_position(int(self.horizontalSlider_2.value() * len(self.magnitude_graph1[0])/self.horizontalSlider_2.maximum()))  
                    self.plot_updater2.set_position(int(self.horizontalSlider_2.value() * len(self.magnitude_graph2[0])/self.horizontalSlider_2.maximum()))  
            if self.pause_graph1.text() == "Resume":
                self.get_and_plot_data_in_graph1(int(self.horizontalSlider.value() * len(self.magnitude_graph1[0])/self.horizontalSlider.maximum()))
                self.get_and_plot_data_in_graph2(int(self.horizontalSlider_2.value() * len(self.magnitude_graph2[0])/self.horizontalSlider_2.maximum()))
            else:
                self.plot_updater1.start()
                self.plot_updater2.start()
        if flag:
            if int(self.horizontalSlider.value() * len(self.magnitude_graph1[0])/self.horizontalSlider.maximum()) < self.max_pos1:
                self.plot_updater1.set_position(int(self.horizontalSlider.value() * len(self.magnitude_graph1[0])/self.horizontalSlider.maximum()))  
                if self.pause_graph1.text() == "Resume":
                    self.get_and_plot_data_in_graph1(int(self.horizontalSlider.value() * len(self.magnitude_graph1[0])/self.horizontalSlider.maximum()))
            if self.pause_graph1.text() == "Pause":
                self.plot_updater1.start()
        else:
            if int(self.horizontalSlider_2.value() * len(self.magnitude_graph2[0])/self.horizontalSlider_2.maximum()) < self.max_pos2:
                self.plot_updater2.set_position(int(self.horizontalSlider_2.value() * len(self.magnitude_graph2[0])/self.horizontalSlider_2.maximum()))  
                if self.pause_graph2.text() == "Resume":
                    self.get_and_plot_data_in_graph2(int(self.horizontalSlider_2.value() * len(self.magnitude_graph2[0])/self.horizontalSlider_2.maximum()))
            if self.pause_graph2.text() == "Pause":
                self.plot_updater2.start()
            
    
    def stop(self, flag):
        if flag:
            self.plot_updater1.stop()
        else:
            self.plot_updater2.stop()

    def pause(self, flag):
        if self.checkBox_link.isChecked():

            if self.pause_graph1.text() == "Pause":
                self.pause_linked()
            else:
                self.resume_linked()
        else:
            if flag:
                if self.pause_graph1.text() == "Pause":
                    self.pause_method(self.pause_graph1, self.plot_updater1)
                else:
                    self.resume_method(self.pause_graph1, self.plot_updater1)
            else:
                if self.pause_graph2.text() == "Pause":
                    self.pause_method(self.pause_graph2, self.plot_updater2)
                else:
                     self.resume_method(self.pause_graph2, self.plot_updater2)

    def pause_linked(self):
        self.pause_method(self.pause_graph1, self.plot_updater1)
        self.pause_method(self.pause_graph2, self.plot_updater2)

    def pause_method(self, pause_button, plot_updater):
        pause_button.setText("Resume")
        plot_updater.stop()

    def resume_linked(self):
        self.resume_method(self.pause_graph1, self.plot_updater1)
        self.resume_method(self.pause_graph2, self.plot_updater2)


    def resume_method(self, pause_button, plot_updater):
        pause_button.setText("Pause")
        plot_updater.start()

  
    def rewind(self, flag):
        if self.checkBox_link.isChecked():
            self.plot_updater2.set_position(0)
            self.plot_updater1.set_position(0)
        if self.pause_graph1.text() == "Resume":
            self.get_and_plot_data_in_graph1(self.plot_updater1.position)
            self.get_and_plot_data_in_graph2(self.plot_updater2.position)
        else:
            if flag:
                self.plot_updater1.set_position(0)
                if self.pause_graph1.text() == "Resume":
                    self.get_and_plot_data_in_graph1(self.plot_updater1.position)
            else:
                self.plot_updater2.set_position(0)
                if self.pause_graph2.text() == "Resume":
                    self.get_and_plot_data_in_graph2(self.plot_updater2.position)

    def zoom_in(self, flag):
        if self.checkBox_link.isChecked():
            self.scale_factor_graph1 *=3/4
            self.scale_factor_graph2 *= 3/4
            if self.pause_graph1.text() == "Resume" or self.pause_graph2.text() == "Resume" :
                self.widget.setYRange(self.minimum1 *self.scale_factor_graph1 + self.panning_offset1, self.maximum1 *self.scale_factor_graph1 +self.panning_offset1 )
                self.widget_2.setYRange(self.minimum2 *self.scale_factor_graph2+ self.panning_offset2, self.maximum2 *self.scale_factor_graph2+ self.panning_offset2)
        else:
            if flag:
                self.scale_factor_graph1*= 3/4
                if self.pause_graph1.text() == "Resume":
                    self.widget.setYRange(self.minimum1 *self.scale_factor_graph1 + self.panning_offset1, self.maximum1 *self.scale_factor_graph1 +self.panning_offset1 )
            else:
                self.scale_factor_graph2 *= 3/4
                if self.pause_graph2.text() == "Resume":
                    self.widget_2.setYRange(self.minimum2 *self.scale_factor_graph2+ self.panning_offset2, self.maximum2 *self.scale_factor_graph2+ self.panning_offset2)


    def zoom_out(self, flag):
        if self.checkBox_link.isChecked():
            self.scale_factor_graph1 *=5/4
            self.scale_factor_graph2 *= 5/4
            if self.pause_graph1.text() == "Resume" or self.pause_graph2.text() == "Resume" :
                self.widget.setYRange(self.minimum1 *self.scale_factor_graph1 + self.panning_offset1, self.maximum1 *self.scale_factor_graph1 +self.panning_offset1 )
                self.widget_2.setYRange(self.minimum2 *self.scale_factor_graph2+ self.panning_offset2, self.maximum2 *self.scale_factor_graph2+ self.panning_offset2)
        else:
            if flag:
                self.scale_factor_graph1*= 5/4
                if self.pause_graph1.text() == "Resume":
                    self.widget.setYRange(self.minimum1 *self.scale_factor_graph1 + self.panning_offset1, self.maximum1 *self.scale_factor_graph1 + self.panning_offset1)
            else:
                self.scale_factor_graph2 *= 5/4
                if self.pause_graph2.text() == "Resume":
                    self.widget_2.setYRange(self.minimum2 *self.scale_factor_graph2+ self.panning_offset2, self.maximum2 *self.scale_factor_graph2+ self.panning_offset2)

            
    def control_plotting_speed(self, index, flag):
        if index == 0:   #0.5x
            if self.checkBox_link.isChecked():
                self.set_linked_speed(300, index)
            elif flag:
                self.set_speed_graph1(300)  
            else:
                self.set_speed_graph2(300)
        elif index == 1 :     #1x
            if self.checkBox_link.isChecked():
                self.set_linked_speed(200, index)
            elif flag:
                self.set_speed_graph1(200) 
            else:
                self.set_speed_graph2(200)
        elif index == 2 :   #1.5x
            if self.checkBox_link.isChecked():
                self.set_linked_speed(100, index)
            elif flag:
                self.set_speed_graph1(100) 
            else:
                self.set_speed_graph2(100)
        elif index == 3 :     #2x
            if self.checkBox_link.isChecked():
                self.set_linked_speed(50, index)
            elif flag:
                self.set_speed_graph1(50) 
            else:
                self.set_speed_graph2(50)

    def set_linked_speed(self, speed, index):
        self.comboBox_speed_graph2.setCurrentIndex(index)
        self.comboBox_speed_graph1.setCurrentIndex(index)
        self.set_speed_graph1(speed)
        self.set_speed_graph2(speed)
    
    def set_speed_graph1(self, speed):
        self.plot_updater1.set_update_interval(speed) 
        self.plot_updater1.start()
    
    def set_speed_graph2(self, speed):
        self.plot_updater2.set_update_interval(speed) 
        self.plot_updater2.start()

    def link(self):
        self.scale_factor_graph2= self.scale_factor_graph1
        if self.pause_graph2.text() == "Resume":
           self.widget_2.setYRange(self.minimum2 *self.scale_factor_graph2+ self.panning_offset2, self.maximum2 *self.scale_factor_graph2+ self.panning_offset2)
        self.comboBox_speed_graph2.setCurrentIndex(self.comboBox_speed_graph1.currentIndex())
        self.control_plotting_speed(self.comboBox_speed_graph2.currentIndex(),False)
        if self.pause_graph1.text() == "Pause":
            self.pause_graph2.setText("Pause")
            self.plot_updater2.start()
        else:
            self.pause_graph2.setText("Resume")
            self.plot_updater2.stop()
            self.plot_updater1.stop()

    def control_single_plot(self, flag):
        if flag:
            self.selected_plot_index1 = self.comboBox_signals_graph1.currentData()
        else:
            self.selected_plot_index2= self.comboBox_signals_graph2.currentData()

    def change_plot_colour(self, flag):
        if flag:
            self.colours1[self.selected_plot_index1]= self.comboBox_colors_graph1.currentText()
            if self.pause_graph1.text() == "Resume" :
                self.get_and_plot_data_in_graph1(self.plot_updater1.position)
        else:
            self.colours2[self.selected_plot_index2]= self.comboBox_colors_graph2.currentText()
            if self.pause_graph2.text() == "Resume" :
                self.get_and_plot_data_in_graph2(self.plot_updater2.position)
    
    def change_visibility(self, flag):
        if flag:
            self.visability1[self.selected_plot_index1]= self.checkBox_show_graph1.isChecked()
            if self.pause_graph1.text() == "Resume" :
                self.get_and_plot_data_in_graph1(self.plot_updater1.position)
        else:
            self.visability2[self.selected_plot_index2]= self.checkBox_show_graph2.isChecked()
            if self.pause_graph2.text() == "Resume" :
                self.get_and_plot_data_in_graph2(self.plot_updater2.position)
    
    def start_panning(self,event, flag):
        if event.button() == Qt.LeftButton:
            self.mouse_click_pos = event.pos().y()
        

    def trace_panning(self,event, flag):
        if event.buttons() & Qt.LeftButton:
            if self.mouse_click_pos is not None:
                current_y= event.pos().y()
                if current_y > self.mouse_click_pos:
                    self.panning(flag, "up")
                else:
                    self.panning(flag, "down")

    def panning(self, flag, text):
        if flag:
            if text == "up":
                if self.max1 *self.scale_factor_graph1 + self.panning_offset1 < self.max1:
                    self.panning_offset1+= 0.05 *self.max1
            else:
                if self.max1 *self.scale_factor_graph1 + self.panning_offset1 > self.min1 +0.4 :
                    self.panning_offset1-= 0.05 * abs(self.min1)
            if self.pause_graph1.text() == "Resume":
                self.widget.setYRange(self.minimum1 *self.scale_factor_graph1 + self.panning_offset1, self.maximum1 *self.scale_factor_graph1 +self.panning_offset1 )
                
        else:
            if text == "up":
                if self.max2 *self.scale_factor_graph2 + self.panning_offset2 < self.max2:
                    self.panning_offset2+= 0.05 *self.max2
            else:
                if self.max2 *self.scale_factor_graph2 + self.panning_offset2 > self.min2 +0.4:
                    self.panning_offset2-= 0.05 * abs(self.min2)
            if self.pause_graph2.text() == "Resume" :
                self.widget_2.setYRange(self.minimum2 *self.scale_factor_graph2+ self.panning_offset2, self.maximum2 *self.scale_factor_graph2+ self.panning_offset2)

    
    def Show_pop_up_window(self, flag):
        input_dialog=  QInputDialog()
        user_input, ok_pressed = input_dialog.getText( input_dialog, "Input Dialog", "Enter the label:")
        if ok_pressed:
            if flag:
                self.labels1[self.selected_plot_index1]= user_input
                self.widget_plot.legend.removeItem(self.plot_items_graph1[self.selected_plot_index1])
                self.widget_plot.legend.addItem(self.plot_items_graph1[self.selected_plot_index1], name= self.labels1[self.selected_plot_index1])
                self.comboBox_signals_graph1.clear()
                for Combobox_it in range (len(self.labels1)):
                    self.comboBox_signals_graph1.addItem( self.labels1[Combobox_it], userData=Combobox_it)
                    self.comboBox_signals_graph1.setCurrentText(self.labels1[self.selected_plot_index1])
            else:
                self.labels2[self.selected_plot_index2] = user_input
                self.widget_2_plot.legend.removeItem(self.plot_items_graph2[self.selected_plot_index2])
                self.widget_2_plot.legend.addItem(self.plot_items_graph2[self.selected_plot_index2], name= self.labels2[self.selected_plot_index2])
                self.comboBox_signals_graph2.clear()
                for Combobox_it in range (len(self.labels2)):
                    self.comboBox_signals_graph2.addItem( self.labels2[Combobox_it], userData=Combobox_it)
                    self.comboBox_signals_graph2.setCurrentText(self.labels2[self.selected_plot_index2])

    def Move_signals(self, flag):
        if flag:
            self.add_to_graph(self.magnitude_graph2, self.magnitude_graph1[self.selected_plot_index1], self.plot_items_graph2, self.colours2, self.labels2, self.visability2, self.widget_2_plot,self.labels1[self.selected_plot_index1], self.colours1[self.selected_plot_index1], self.labels1[self.selected_plot_index1], self.visability1[self.selected_plot_index1], self.comboBox_signals_graph2,self.pause_graph2,self.plot_updater2)
            self.remove_from_graph(self.magnitude_graph1,self.widget_plot, self.plot_items_graph1[self.selected_plot_index1],self.plot_items_graph1, self.labels1, self.colours1, self.visability1,self.comboBox_signals_graph1, self.selected_plot_index1, self.plot_updater1)
        else:
            self.add_to_graph(self.magnitude_graph1, self.magnitude_graph2[self.selected_plot_index2], self.plot_items_graph1, self.colours1, self.labels1, self.visability1, self.widget_plot,self.labels2[self.selected_plot_index2], self.colours2[self.selected_plot_index2], self.labels2[self.selected_plot_index2], self.visability2[self.selected_plot_index2], self.comboBox_signals_graph1,self.pause_graph1,self.plot_updater1)
            self.remove_from_graph(self.magnitude_graph2,self.widget_2_plot, self.plot_items_graph2[self.selected_plot_index2],self.plot_items_graph2, self.labels2, self.colours2, self.visability2,self.comboBox_signals_graph2, self.selected_plot_index2, self.plot_updater2)    

    def remove_from_graph( self, magnitude,plot_item, item,sig_array, label_array,color_array,visibility_array, combobox, index, updater):
        magnitude.pop(index)
        if len(magnitude) == 0:
            updater.stop()
            updater.set_position(0)
        plot_item.removeItem(item)
        plot_item.legend.removeItem(item)
        sig_array.pop(index)
        label_array.pop(index)
        color_array.pop(index)
        visibility_array.pop(index)
        combobox.clear()
        for Combobox_it in range (len(label_array)):
            combobox.addItem( label_array[Combobox_it], userData=Combobox_it)
            combobox.setCurrentIndex(-1)
        
    def add_to_graph(self, mag_array, mag, sig_array, color_array, label_array, visibility_array, item, name,  color, label, visibility, combobox, button, updater):
        mag_array.append(mag)
        widget_curve= item.plot(name= name)
        sig_array.append(widget_curve)
        color_array.append(color)
        label_array.append(label)
        visibility_array.append(visibility)
        combobox.clear()
        for Combobox_it in range (len(label_array)):
            combobox.addItem( label_array[Combobox_it], userData=Combobox_it)
            combobox.setCurrentIndex(-1)
        if button.text() == "Pause":
            updater.start()
                
    def snapshot_graph1(self, widget_1):
        pixmap = widget_1.grab()  # Capture the widget as a pixmap
        current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")  # Generate a timestamp
        image_path = os.path.join(self.current_directory, f"snapshot_{current_datetime}.png")  # Define the path to save the image
        pixmap.save(image_path, "PNG")  # Save the pixmap as PNG file
        previous_snapshots_directory= os.path.join(self.current_directory, r"previous_snapshots")
        pixmap.save(os.path.join(previous_snapshots_directory, f"snapshot_{current_datetime}.png"), "PNG")
        self.snapshots1.append(image_path)  # Store the image path in the snapshots list
        self.overlay1.resetOverlay()
        self.overlay1.showOverlay()
        

    def snapshot_graph2(self, widget_2):
        pixmap = widget_2.grab()  # Capture the widget as a pixmap
        current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")  # Generate a timestamp
        image_path = os.path.join(self.current_directory, f"snapshot_{current_datetime}.png") # Define the path to save the image
        pixmap.save(image_path, "PNG")  # Save the pixmap as PNG file
        previous_snapshots_directory= os.path.join(self.current_directory, r"previous_snapshots")
        pixmap.save(os.path.join(previous_snapshots_directory, f"snapshot_{current_datetime}.png"), "PNG")
        self.snapshots1.append(image_path)  # Store the image path in the snapshots list
        self.overlay2.resetOverlay()
        self.overlay2.showOverlay()
        

    def make_the_report(self):
        
        file_path, _ = QFileDialog.getSaveFileName(None, "Save Report", self.current_directory, "PDF Files (*.pdf)")
        
        # Check if the user selected a path
        if file_path:
            doc = SimpleDocTemplate(file_path, pagesize=letter)  # Create a PDF document

            # Define the content for the PDF report
            content = []

            # Get the current date and time
            # Add title and current date/time
            styles = getSampleStyleSheet()
            title_style = styles["Title"]
            normal_style = styles["Normal"]

            # Add title and current date/time
            title = Paragraph("Multi-Port, Multi-Channel Signal Viewer", title_style)
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Get the current date and time
            date = Paragraph(f"Date: {current_time.split()[0]}", normal_style)  # Extract the date
            time = Paragraph(f"Time: {current_time.split()[1]}", normal_style)  # Extract the time
            content.extend([title, Spacer(0, 50), Spacer(1, 12), date,Spacer(1,10) ,time, Spacer(1, 30)])
            # Add a table with data statistics
            data = [["Signal", "Mean", "Std", "Duration", "Min", "Max"]]
            for i in range(len(self.labels1)):
                signal_stats = [
                    self.labels1[i] + f"(Graph 1)",
                    np.mean(self.magnitude_graph1[i]),
                    np.std(self.magnitude_graph1[i]),
                    len(self.magnitude_graph1[i]) / self.sampling_frequency,
                    np.min(self.magnitude_graph1[i]),
                    np.max(self.magnitude_graph1[i]),
                ]
                data.append(signal_stats)

            for i in range(len(self.labels2)):
                signal_stats = [
                    self.labels2[i]  + f"(Graph 2)",
                    np.mean(self.magnitude_graph2[i]),
                    np.std(self.magnitude_graph2[i]),
                    len(self.magnitude_graph2[i]) / self.sampling_frequency,
                    np.min(self.magnitude_graph2[i]),
                    np.max(self.magnitude_graph2[i]),
                ]
                data.append(signal_stats)
            table = Table(data)
            table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.gray),
                                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                    ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
            content.append(table)
            content.append(Spacer(1, 30))  # Add some spacing between the table and the snapshots
            snapshot_folder= self.current_directory
            # Find all image files in the snapshot folder
            image_files = [file for file in os.listdir(snapshot_folder) if file.lower().endswith(('.png', '.jpg', '.jpeg'))]


            # Add the snapshots to the report
            for image_file in image_files:
                snapshot_path = os.path.join(snapshot_folder, image_file)
                if os.path.exists(snapshot_path):  # Check if the snapshot file exists
                    image = Image(snapshot_path, width=400, height=300)  # Adjust the width and height as per your requirements
                    content.append(KeepTogether([image]))
                    content.append(Spacer(1,20))
                else:
                    print(f"Warning: Snapshot file not found: {snapshot_path}")

            # Build the PDF report
            doc.build(content)
            image_files = [file for file in os.listdir(self.current_directory) if file.lower().endswith(('.png', '.jpg', '.jpeg'))]
            # delete the snapshots left with the script in the same folder(the copy in the folder previous snapshots wont be removed)
            for image_file in image_files:
                snapshot_path = os.path.join(self.current_directory, image_file)
                os.remove(snapshot_path)




    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pause_graph1.setText(_translate("MainWindow", "Pause"))
        self.zoom_in_graph1.setText(_translate("MainWindow", "Zoom In"))
        self.zoom_out_graph1.setText(_translate("MainWindow", "Zoom Out"))
        self.rewind_graph1.setText(_translate("MainWindow", "Rewind"))
        self.label_4.setText(_translate("MainWindow", "Speed"))
        self.label_signal.setText(_translate("MainWindow", "Signal"))
        self.label_signal2.setText(_translate("MainWindow", "Signal"))
        self.comboBox_speed_graph1.setItemText(0, _translate("MainWindow", "0.5x"))
        self.comboBox_speed_graph1.setItemText(1, _translate("MainWindow", "1x"))
        self.comboBox_speed_graph1.setItemText(2, _translate("MainWindow", "1.5x"))
        self.comboBox_speed_graph1.setItemText(3, _translate("MainWindow", "2x"))
        self.label_change_color_graph1.setText(_translate("MainWindow", "Color"))
        self.comboBox_colors_graph1.setItemText(0, _translate("MainWindow", "Red"))
        self.comboBox_colors_graph1.setItemText(1, _translate("MainWindow", "Green"))
        self.comboBox_colors_graph1.setItemText(2, _translate("MainWindow", "Blue"))
        self.comboBox_colors_graph1.setItemText(3, _translate("MainWindow", "Black"))
        self.comboBox_colors_graph1.setItemText(4, _translate("MainWindow", "Yellow"))
        self.comboBox_colors_graph1.setItemText(5, _translate("MainWindow", "Brown"))
        self.checkBox_show_graph1.setText(_translate("MainWindow", "Show"))
        self.addlabel_button1.setText(_translate("MainWindow", "Add a Label"))
        self.pushButton.setText(_translate("MainWindow", "Move to Graph2"))
        self.save_photo_graph1.setText(_translate("MainWindow", "Save Photo"))
        self.pause_graph2.setText(_translate("MainWindow", "Pause"))
        self.zoom_in_graph2.setText(_translate("MainWindow", "Zoom In"))
        self.zoom_out_graph2.setText(_translate("MainWindow", "Zoom Out"))
        self.rewind_graph2.setText(_translate("MainWindow", "Rewind"))
        self.label_3.setText(_translate("MainWindow", "Speed"))
        self.comboBox_speed_graph2.setItemText(0, _translate("MainWindow", "0.5x"))
        self.comboBox_speed_graph2.setItemText(1, _translate("MainWindow", "1x"))
        self.comboBox_speed_graph2.setItemText(2, _translate("MainWindow", "1.5x"))
        self.comboBox_speed_graph2.setItemText(3, _translate("MainWindow", "2x"))
        self.label_change_color_graph2.setText(_translate("MainWindow", "Color"))
        self.comboBox_colors_graph2.setItemText(0, _translate("MainWindow", "Red"))
        self.comboBox_colors_graph2.setItemText(1, _translate("MainWindow", "Green"))
        self.comboBox_colors_graph2.setItemText(2, _translate("MainWindow", "Blue"))
        self.comboBox_colors_graph2.setItemText(3, _translate("MainWindow", "Black"))
        self.comboBox_colors_graph2.setItemText(4, _translate("MainWindow", "Yellow"))
        self.comboBox_colors_graph2.setItemText(5, _translate("MainWindow", "Brown"))
        self.checkBox_show_graph2.setText(_translate("MainWindow", "Show"))
        self.addlabel_button2.setText(_translate("MainWindow", "Add a Label"))
        self.pushButton_2.setText(_translate("MainWindow", "Move to Graph1"))
        self.save_photo_graph2.setText(_translate("MainWindow", "Save Photo"))
        self.checkBox_link.setText(_translate("MainWindow", "Link the Two Graphs"))
        self.make_report.setText(_translate("MainWindow", "Make a Report"))
        self.actionNew.setText(_translate("MainWindow", "New"))
        self.action_upload_in_Graph_1.setText(_translate("MainWindow", "Graph 1"))
        self.action_upload_in_Graph_2.setText(_translate("MainWindow", "Graph 2"))
        self.actionMake_Report.setText(_translate("MainWindow", "Make Report"))
        self.action_speed_graph1_0_5.setText(_translate("MainWindow", "0.5"))
        self.action_speed_graph1_1.setText(_translate("MainWindow", "1"))
        self.action_speed_graph1_1_5.setText(_translate("MainWindow", "1.5"))
        self.action_speed_graph1_2.setText(_translate("MainWindow", "2"))
        self.action_speed_graph2_0_5.setText(_translate("MainWindow", "0.5"))
        self.action_speed_graph2_1.setText(_translate("MainWindow", "1"))
        self.action_speed_graph2_1_5.setText(_translate("MainWindow", "1.5"))
        self.action_speed_graph2_2.setText(_translate("MainWindow", "2"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
