# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Cedula
                                 A QGIS plugin
 Cedula Catastral
                             -------------------
        begin                : 2018-03-20
        copyright            : (C) 2018 by Worknest
        email                : dignacio.lopezo@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load Cedula class from file Cedula.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .Cedula import Cedula
    return Cedula(iface)
