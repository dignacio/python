# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DivisionFusion_dialog_base.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DivisionFusionDialogBase(object):
    def setupUi(self, DivisionFusionDialogBase):
        DivisionFusionDialogBase.setObjectName("DivisionFusionDialogBase")
        DivisionFusionDialogBase.resize(400, 300)
        self.button_box = QtWidgets.QDialogButtonBox(DivisionFusionDialogBase)
        self.button_box.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.button_box.setObjectName("button_box")

        self.retranslateUi(DivisionFusionDialogBase)
        self.button_box.accepted.connect(DivisionFusionDialogBase.accept)
        self.button_box.rejected.connect(DivisionFusionDialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(DivisionFusionDialogBase)

    def retranslateUi(self, DivisionFusionDialogBase):
        _translate = QtCore.QCoreApplication.translate
        DivisionFusionDialogBase.setWindowTitle(_translate("DivisionFusionDialogBase", "DivisionFusion"))

