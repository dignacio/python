# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Master
                                 A QGIS plugin
 Master
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2018-04-27
        copyright            : (C) 2018 by Master
        email                : Master
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
    """Load Master class from file Master.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .Master import Master
    return Master(iface)