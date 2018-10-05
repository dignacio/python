# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'EliminacionV3_dialog_base.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_EliminacionV3DialogBase(object):
    def setupUi(self, EliminacionV3DialogBase):
        EliminacionV3DialogBase.setObjectName("EliminacionV3DialogBase")
        EliminacionV3DialogBase.resize(400, 300)
        self.button_box = QtWidgets.QDialogButtonBox(EliminacionV3DialogBase)
        self.button_box.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.button_box.setObjectName("button_box")

        self.retranslateUi(EliminacionV3DialogBase)
        self.button_box.accepted.connect(EliminacionV3DialogBase.accept)
        self.button_box.rejected.connect(EliminacionV3DialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(EliminacionV3DialogBase)

    def retranslateUi(self, EliminacionV3DialogBase):
        _translate = QtCore.QCoreApplication.translate
        EliminacionV3DialogBase.setWindowTitle(_translate("EliminacionV3DialogBase", "EliminacionV3"))

