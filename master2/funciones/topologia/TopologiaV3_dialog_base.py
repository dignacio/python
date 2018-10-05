# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'TopologiaV3_dialog_base.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QSettings
QSettings().setValue('autor', 'Charro')

class Ui_TopologiaV3DialogBase(object):
    def setupUi(self, TopologiaV3DialogBase):
        TopologiaV3DialogBase.setObjectName("TopologiaV3DialogBase")
        TopologiaV3DialogBase.resize(400, 300)
        self.button_box = QtWidgets.QDialogButtonBox(TopologiaV3DialogBase)
        self.button_box.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.button_box.setObjectName("button_box")

        self.retranslateUi(TopologiaV3DialogBase)
        self.button_box.accepted.connect(TopologiaV3DialogBase.accept)
        self.button_box.rejected.connect(TopologiaV3DialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(TopologiaV3DialogBase)

    def retranslateUi(self, TopologiaV3DialogBase):
        _translate = QtCore.QCoreApplication.translate
        TopologiaV3DialogBase.setWindowTitle(_translate("TopologiaV3DialogBase", "TopologiaV3"))

