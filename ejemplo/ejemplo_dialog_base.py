# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ejemplo_dialog_base.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ejemploDialogBase(object):
    def setupUi(self, ejemploDialogBase):
        ejemploDialogBase.setObjectName("ejemploDialogBase")
        ejemploDialogBase.resize(389, 82)
        self.pushButton = QtWidgets.QPushButton(ejemploDialogBase)
        self.pushButton.setGeometry(QtCore.QRect(290, 30, 75, 23))
        self.pushButton.setObjectName("pushButton")
        self.comboBox = QtWidgets.QComboBox(ejemploDialogBase)
        self.comboBox.setGeometry(QtCore.QRect(60, 30, 211, 22))
        self.comboBox.setObjectName("comboBox")
        self.label = QtWidgets.QLabel(ejemploDialogBase)
        self.label.setGeometry(QtCore.QRect(20, 30, 47, 13))
        self.label.setObjectName("label")

        self.retranslateUi(ejemploDialogBase)
        QtCore.QMetaObject.connectSlotsByName(ejemploDialogBase)

    def retranslateUi(self, ejemploDialogBase):
        _translate = QtCore.QCoreApplication.translate
        ejemploDialogBase.setWindowTitle(_translate("ejemploDialogBase", "ejemplo"))
        self.pushButton.setText(_translate("ejemploDialogBase", "PushButton"))
        self.label.setText(_translate("ejemploDialogBase", "Capa"))

