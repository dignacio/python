# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'CedulaPadron_dialog_base.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_CedulaPadronDialogBase(object):
    def setupUi(self, CedulaPadronDialogBase):
        CedulaPadronDialogBase.setObjectName("CedulaPadronDialogBase")
        CedulaPadronDialogBase.resize(931, 746)
        self.tabWidget = TabWidget(CedulaPadronDialogBase)
        self.tabWidget.setGeometry(QtCore.QRect(20, 20, 891, 711))
        self.tabWidget.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.West)
        self.tabWidget.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tabWidget.setElideMode(QtCore.Qt.ElideRight)
        self.tabWidget.setTabsClosable(False)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tabWidget.addTab(self.tab_2, "")

        self.retranslateUi(CedulaPadronDialogBase)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(CedulaPadronDialogBase)

    def retranslateUi(self, CedulaPadronDialogBase):
        _translate = QtCore.QCoreApplication.translate
        CedulaPadronDialogBase.setWindowTitle(_translate("CedulaPadronDialogBase", "CedulaPadron"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("CedulaPadronDialogBase", "UBICACION"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("CedulaPadronDialogBase", "Tab 2"))

from tabwidget import TabWidget
