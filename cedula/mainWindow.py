# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
       
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

    def hasAlgo(self):
        self.msg = QMessageBox()
        self.msg.setText("mensaje")
        self.msg.setIcon(QMessageBox().Critical)
        self.msg.setWindowTitle("titulo")
        self.msg.show()
        result = self.msg.exec_()

        QgsMessageLog.logMessage("message", "name")
        print('entro')
        #self.lineEdit.clear

