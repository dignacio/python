# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AsignacionCampoDialog
                                 A QGIS plugin
 AsignacionCampo
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2018-06-21
        git sha              : $Format:%H$
        copyright            : (C) 2018 by AsignacionCampo
        email                : AsignacionCampo
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
from qgis.utils import iface
from PyQt5.QtCore import Qt

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'AsignacionCampo_dialog_base.ui'))


class AsignacionCampoDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=iface.mainWindow()):
        """Constructor."""
        super(AsignacionCampoDialog, self).__init__(parent, \
            flags=Qt.WindowMinimizeButtonHint|Qt.WindowCloseButtonHint)
        #self.close()
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
