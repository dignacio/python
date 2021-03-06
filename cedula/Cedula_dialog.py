# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CedulaDialog
                                 A QGIS plugin
 Cedula Catastral
                             -------------------
        begin                : 2018-03-20
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Worknest
        email                : dignacio.lopezo@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from PyQt5 import uic
from PyQt5 import QtWidgets

from PyQt5.QtCore import *
from PyQt5.QtGui import *

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'Cedula_dialog_base.ui'))


class CedulaDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(CedulaDialog, self).__init__(parent, \
            flags=Qt.WindowMinimizeButtonHint|Qt.WindowMaximizeButtonHint|Qt.WindowCloseButtonHint)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

    def closeEvent(self,event):
        print("salio")
        if self.predio != None:
            self.predio.selectionChanged.disconnect()
        
    def event(self, event):
        #print(event.type())

        if event.type() == QEvent.WindowActivate:
            print('esta activa', str(event.type()))

            print(self.lista)
            listElim = []

            for key, value in self.lista.items():
                #print(key, value)

                if self.lista[key].isVisible() == False:
                    listElim.append(key)

                # print(str(self.lista[key].isVisible()),str(self.lista[key].windowTitle()))

            for key in listElim:
                del self.lista[key]

        return super(CedulaDialog, self).event(event)
