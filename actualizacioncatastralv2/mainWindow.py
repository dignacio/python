# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(457, 241)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(180, 70, 75, 23))
        self.pushButton.setObjectName("pushButton")
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(70, 120, 113, 20))
        self.lineEdit.setObjectName("lineEdit")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 457, 21))
        self.menubar.setObjectName("menubar")
        self.menuhola = QtWidgets.QMenu(self.menubar)
        self.menuhola.setObjectName("menuhola")
        self.menuhoa_dos = QtWidgets.QMenu(self.menubar)
        self.menuhoa_dos.setObjectName("menuhoa_dos")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionuno = QtWidgets.QAction(MainWindow)
        self.actionuno.setObjectName("actionuno")
        self.actiondos = QtWidgets.QAction(MainWindow)
        self.actiondos.setObjectName("actiondos")
        self.actionuno_2 = QtWidgets.QAction(MainWindow)
        self.actionuno_2.setObjectName("actionuno_2")
        self.actiondos_2 = QtWidgets.QAction(MainWindow)
        self.actiondos_2.setObjectName("actiondos_2")
        self.menuhola.addAction(self.actionuno)
        self.menuhola.addAction(self.actiondos)
        self.menuhoa_dos.addAction(self.actionuno_2)
        self.menuhoa_dos.addAction(self.actiondos_2)
        self.menubar.addAction(self.menuhola.menuAction())
        self.menubar.addAction(self.menuhoa_dos.menuAction())

        self.retranslateUi(MainWindow)
        #self.pushButton.clicked.connect(hasAlgo)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "PushButton"))
        self.menuhola.setTitle(_translate("MainWindow", "hola"))
        self.menuhoa_dos.setTitle(_translate("MainWindow", "hoa dos"))
        self.actionuno.setText(_translate("MainWindow", "uno"))
        self.actiondos.setText(_translate("MainWindow", "dos"))
        self.actionuno_2.setText(_translate("MainWindow", "uno"))
        self.actiondos_2.setText(_translate("MainWindow", "dos"))


