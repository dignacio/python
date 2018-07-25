

from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt, QSettings, QSize
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWidgets import QAction, QMessageBox
from PyQt5 import QtWidgets
# Initialize Qt resources from file resources.py
from .resources import *
from qgis.core import *
from qgis.utils import iface
from qgis.gui import QgsLayerTreeView

import os.path
import os, json, requests
from osgeo import ogr, osr

class Referencias:

    def consultar(self, egName):

        url='http://192.168.0.40:8080/busquedasimplewkn/api/busqueda/simple'
        token = self.obtenerToken()

        pagina = None
        itemsPagina = None

        if egName == 'e_predio':
            pagina = 0
            itemsPagina = 6000

        payload = {"nombre": egName, "epsg": 32614,"bbox": False,"pin": False,"geomWKT": None, "epsgGeomWKT": 32614,"incluirGeom": True,"pagina": pagina,"itemsPagina": itemsPagina}
        payload = json.dumps(payload)
        headers = {'Content-Type': 'application/json', 'Authorization' : token}

        response = requests.post(url, headers = headers, data = payload)
        if response.status_code == 200:
            data = response.content
            data = json.loads(data)

            return data

        else:
            self.createAlert('Error de servidor', QMessageBox.Critical, 'Cargar capas de referencia para topologia')

#######################################################################################################################

    def cargar(self, nameCapa, tipoConsulta):
        #Nombre de la capa de acuerdo al valor del ComboBox de capas a cargar
        
        self.valorInteresado = -1

        #print(QSettings().value('capaEnEdicion'))
        if tipoConsulta == 'objeto' and QSettings().value('capaRefEdicion') == self.obtenerIdCapa( nameCapa):
            return QgsProject.instance().mapLayer(self.obtenerIdCapa( nameCapa)).getFeatures()

        self.manzanaPrincipal = QgsProject.instance().mapLayer(self.obtenerIdCapa( 'manzana'))

        if self.manzanaPrincipal == None:
            self.createAlert("Debes cargar una manzana primero", QMessageBox().Critical, "Pintar capas de referencia")
            return
        
        self.tablasReferencias = {
        'Estado' : 'e_estado',
        'Region Catastral' : 'e_region_carto',
        'Municipios' : 'e_municipio',
        'Secciones' : 'e_seccion',		
        'Localidades' : 'e_localidad',
        'Sectores' : 'e_sector',
        'Manzanas' : 'e_manzana',
        'Predios' : 'e_predio',
        'Calles' : 'e_calle',
        'Colonias' : 'e_colonia',
        'Codigo Postal' : 'e_cp',
        'Zona Uno' : 'e_zona_uno',
        'Zona Dos' : 'e_zona_dos',
        'Area de Valor' : 'e_area_valor'
        }

        data = self.consultar(self.tablasReferencias[nameCapa])
        
        type(data)
        srid = 32614
        inSpatialRef = osr.SpatialReference()
        inSpatialRef.ImportFromEPSG(int(srid))
        outSpatialRef = osr.SpatialReference()
        outSpatialRef.ImportFromEPSG(int(srid))
        coordTrans = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)
        if not bool(data):
            raise Exception('Error')

        if data['features'] == []:
            return

        varKeys = data['features'][0]['properties']

        keys = list(varKeys.keys())
        
        stringInteresado = 'cve_cat'

        if nameCapa == 'Estado':
            stringInteresado = 'clave'

        if tipoConsulta == 'contenedor':
            self.valorInteresado = keys.index(stringInteresado)
            

        properties = []
        geoms = []
        for feature in data['features']:
            geom = feature['geometry']
            
            property = feature['properties']
            geom = json.dumps(geom)
            geometry = ogr.CreateGeometryFromJson(geom)
            geometry.Transform(coordTrans)
            geoms.append(geometry.ExportToWkt())

            l = []
            for i in range(0, len(keys)):
                
                l.append(property[keys[i]])
            properties.append(l)

        feats = [ QgsFeature() for i in range(len(geoms)) ]
        for i, feat in enumerate(feats):
            feat.setGeometry(QgsGeometry.fromWkt(geoms[i]))
            feat.setAttributes(properties[i])


        return feats


#####################################################################################################################

    def obtenerToken(self):
        url= 'http://192.168.0.40:8080/auth/login'
        payload = {"username" : "user", "password" : "user"}
        payload = json.dumps(payload)
        headers = {'Content-Type': 'application/json'}

        response = requests.post(url, headers = headers, data = payload)
        if response.status_code == 200:
            #print('habemus token')
            data = response.content
        else:
            self.createAlert('Error de autenticacion', QMessageBox().Critical, 'Autenticacion')
            return
            ##print('no se arma el token')

        #print(json.loads(data)['access_token'])
        return 'bearer ' + json.loads(data)['access_token']


####################################################################################################################


    def obtenerIdCapa(self, nombreCapa):

        if nombreCapa == "manzana":
            return QSettings().value('xManzana')
        elif nombreCapa == "predios.geom":
            return QSettings().value('xPredGeom')
        elif nombreCapa == "predios.num":
            return QSettings().value('xPredNum')
        elif nombreCapa == "construcciones":
            return QSettings().value('xConst')
        elif nombreCapa == "horizontales.geom":
            return QSettings().value('xHoriGeom')
        elif nombreCapa == "horizontales.num":
            return QSettings().value('xHoriNum')
        elif nombreCapa == "verticales":
            return QSettings().value('xVert')
        elif nombreCapa == "Area de Valor":
            return QSettings().value('xAreaValor')
        elif nombreCapa == "Zona Uno":
            return QSettings().value('xZonaUno')
        elif nombreCapa == "Zona Dos":
            return QSettings().value('xZonaDos')
        elif nombreCapa == "Codigo Postal":
            return QSettings().value('xCP')
        elif nombreCapa == "Colonias":
            return QSettings().value('xColonia')
        elif nombreCapa == "Calles":
            return QSettings().value('xCalle')
        elif nombreCapa == "Sectores":
            return QSettings().value('xSector')
        elif nombreCapa == "Localidades":
            return QSettings().value('xLocal')
        elif nombreCapa == "Secciones":
            return QSettings().value('xSeccion')
        elif nombreCapa == "Municipios":
            return QSettings().value('xMunicipio')
        elif nombreCapa == "Region Catastral":
            return QSettings().value('xRegion')
        elif nombreCapa == "Estado":
            return QSettings().value('xEstado')
        
        return 'None'
    