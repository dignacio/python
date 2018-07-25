

from qgis.utils import iface
from qgis.core import *
from PyQt5.QtCore import QFileInfo, QSettings, QPoint
from PyQt5.QtWidgets import QToolBar, QDockWidget, QMenuBar, QMenu, QAction, QMessageBox
from PyQt5.QtGui import QIcon, QColor
from qgis import *
import os.path
import os, json, requests
from osgeo import ogr, osr
import math

class Reglas:

    def __init__(self, ACA):
        self.ACA = ACA
        self.idManzanas = self.ACA.obtenerIdCapa('manzana')
        self.idPredios = self.ACA.obtenerIdCapa('predios.geom')
        self.idConst = self.ACA.obtenerIdCapa('construcciones')

        self.manzanasMalas = []
        self.prediosMalos = []
        self.constMalas = []

############################################################################

    def obtenerSoloFeaturesRef(self, nameCapa, tipoConsulta):
        #Nombre de la capa de acuerdo al valor del ComboBox de capas a cargar
        
        self.valorInteresado = -1

        #print(QSettings().value('capaEnEdicion'))
        if tipoConsulta == 'objeto' and QSettings().value('capaRefEdicion') == self.ACA.obtenerIdCapa( nameCapa):
            print('namecapa', nameCapa)
            return QgsProject.instance().mapLayer(self.ACA.obtenerIdCapa( nameCapa)).getFeatures()

        self.manzanaPrincipal = QgsProject.instance().mapLayer(self.ACA.obtenerIdCapa('manzana'))

        if self.manzanaPrincipal == None:
            self.createAlert("Debes cargar una manzana primero", QMessageBox().Critical, "Pintar capas de referencia")
            return

        data = self.ACA.obtenerCapasDeReferencia(self.ACA.tablasReferencias[nameCapa], None)
        
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


###########################################################

    def validarIntersecciones(self, capa1, capa2):

        if capa1 == None or capa2 == None:
            return
        
        #Lista de errores
        listaErrores = []

        #Obtenemos los featores
        listaCapa1 = list(capa1.getFeatures())
        listaCapa2 = list(capa2.getFeatures())

        #Variables para el error
        self.cuentaError = 0
        self.stringError = ""

        tolerancia = 0.0000001

        nombreCapa1 = capa1.name()
        nombreCapa2 = capa2.name()
        print("Validando intersecciones: " + nombreCapa1 + " - " + nombreCapa2)

        #Operaciones realizadas cuando las capas son distintas
        if (capa1.id() != capa2.id()):
            rango1 = len(listaCapa1)
            rango2 = len(listaCapa2)
            for i in range(0, rango1):
                feat1 = listaCapa1[i]
                for j in range(0, rango2):
                    feat2 = listaCapa2[j] 
                    #Comparamos las intersecciones
                    if (feat1.geometry().intersects(feat2.geometry())):
                        interseccion = feat1.geometry().buffer(-0.0000001,1).intersection(feat2.geometry().buffer(-0.0000001,1))
                        if (interseccion.area() > tolerancia):
                            listaErrores.append(interseccion.asWkt())
                            self.checarMalos(capa1, feat1)
                            self.checarMalos(capa2, feat2)
        #Cuandolas capas a comparar son la misma
        else:
            rango1 = len(listaCapa1)
            for i in range(0, rango1-1):
                feat1 = listaCapa1[i]
                for j in range(i+1, rango1):
                    feat2 = listaCapa2[j]
                    if (feat1.geometry().intersects(feat2.geometry())):
                        interseccion = feat1.geometry().buffer(-0.0000001,1).intersection(feat2.geometry().buffer(-0.0000001,1))
                        if(interseccion.area() > tolerancia):
                            listaErrores.append(interseccion.asWkt()) 
                            self.checarMalos(capa1, feat1)
                            self.checarMalos(capa1, feat2)
        self.cuentaError = len(listaErrores)

        if (self.cuentaError == 0):
            return

        

        self.stringError = "Interseccion: " + nombreCapa1 + " - " + nombreCapa2 + " " + str(self.cuentaError) + " elementos"   
        temp = QgsVectorLayer("Polygon?crs=epsg:32614", "Intersecciones: "  + nombreCapa1 + "-" + nombreCapa2, "memory")

        self.pintarErrores(temp, listaErrores)
        

###################################################################################################

    def validarCobertura(self, capaBase, capaCobertura):

        #Creamos las capas involucradas
        if capaBase == None or capaCobertura == None:
            return

        listaBase = list(capaBase.getFeatures()) #Obtenemos la lista de las features
        listaCobertura = list(capaCobertura.getFeatures())
        
        #OBtenemos las variables para los errores
        self.cuentaError = 0
        self.stringError = "None"
        #tolerancia = 0.0000001

        listDiferencias = [] #Lista con los errores

        #Longitud de las listas para checar todas las featuers
        rangoBase = len(listaBase)
        rangoCober = len(listaCobertura)

        nombreBase = capaBase.name()
        nombreCobertura = capaCobertura.name()
        print("Validando cobertura: " + nombreBase + " - " + nombreCobertura)
        
        #Checamos ls errores
        for i in range(0, rangoBase):
            objBase = listaBase[i].geometry()
            diferencia = QgsGeometry()
            diferencia = objBase
            for j in range(0, rangoCober):
                objCober = listaCobertura[j].geometry().buffer(0.0000001,1)
                diferencia = diferencia.difference(objCober)

            if(diferencia.area() > 0.0000001): #Agregamos los errores a la lista

                listDiferencias.append(diferencia.asWkt())
                self.checarMalos(capaBase, listaBase[i])
        self.cuentaError = len(listDiferencias)

        if (self.cuentaError == 0):
            return
        
        

        #Dibujamos los errores
        self.stringError = nombreBase + " no cubiertos por " + nombreCobertura + " " + str(self.cuentaError) + " elementos"
        temp = QgsVectorLayer("Polygon?crs=epsg:32614", nombreBase + " no cubiertos por " + nombreCobertura, "memory")
        
        
        self.pintarErrores(temp, listDiferencias)
        
############################################################################################

    def validarInclusion(self, capaObjeto, capaContenedor):

        if capaObjeto == None or capaContenedor == None:
            return

        listaObjeto = list(capaObjeto.getFeatures()) #Lista los objetos
        listaContenedor = list(capaContenedor.getFeatures())

        self.cuentaError = 0
        self.stringError = "None"
        tolerancia = 0.00000001 #Si se pasa de la tolerancia es un error
        listaSalidas = [] #Objetos salidos

        nombreObjetos = capaObjeto.name()
        nombreContenedor = capaContenedor.name()
        print("Validando inclusion: " + nombreObjetos + " - " + nombreContenedor)

        for featObj in listaObjeto: #Para cada contenedor...
            objeto = featObj.geometry()
            bandera = False
            for featCont in listaContenedor:   
                contenedor = featCont.geometry()
                if objeto.intersects(contenedor): #El area del objeto debe ser igual a su interseccion con algo de tolerancia
                    bandera = True
                    inter = objeto.intersection(contenedor)
                    areaContenida = inter.area()
                    areaObjeto = objeto.area()
                    diferencia = areaObjeto - areaContenida
                    if (diferencia > tolerancia):
                        salida = objeto.difference(contenedor)
                        listaSalidas.append(salida.asWkt())
                        self.checarMalos(capaObjeto, featObj)
            if not bandera:

                listaSalidas.append(objeto.asWkt())
                self.checarMalos(capaObjeto, featObj)

        self.cuentaError = len(listaSalidas)

        if (self.cuentaError == 0): #Si hay errores...
            return
        #Los dibujamos
        

        self.stringError = nombreObjetos + " no cubiertos totalmente por " + nombreContenedor + " " + str(self.cuentaError) + " elementos"
        temp = QgsVectorLayer("Polygon?crs=epsg:32614", nombreObjetos + " no cubiertos totalmente por " + nombreContenedor, "memory")

        self.pintarErrores(temp, listaSalidas)

#######################################################################################

    def validarPoligonosInvalidos(self, capa):

        if capa == None:
            return

        features = capa.getFeatures()
        
        self.cuentaError = 0
        self.stringError = "None"
        self.poligonosValidos = True

        geoms = []

        nombreCapa = capa.name()
        print("Validando poligonos invalidos: " + nombreCapa)

        for s in features:
            geom = s.geometry()

            if not geom.isGeosValid():
                geoms.append(geom.asWkt())
                self.checarMalos(capa, s)

        self.cuentaError = len(geoms)

        if (self.cuentaError == 0):
            return

        self.poligonosValidos = False

        
        self.stringError = "Capa: " + nombreCapa + " " + str(self.cuentaError) + " geometrias invalidas"
        temp = QgsVectorLayer('Polygon?crs=epsg:32614', 'Poligonos Invalidos ' + nombreCapa, 'memory')

        self.pintarErrores(temp, geoms)


########################################################################################

    #DUPLICADOS - PUNTOS Y LINESTRING
    def validarDuplicados(self, capa):

        if capa == None:
            return
        
        features = capa.getFeatures()
        geoms = []

        self.cuentaError = 0
        self.stringError = "None"

        listaFeatures = list(features)
        rango = len(listaFeatures)

        nombreCapa = capa.name()
        print("Validando duplicados: " + nombreCapa)

        for i in range(0, rango-1):
            geometria1 = listaFeatures[i].geometry()
            for j in range(i+1, rango):
                
                geometria2 = listaFeatures[j].geometry()
                if(geometria1.equals(geometria2)):
                    geoms.append(geometria1.asWkt())
                    self.checarMalos(capa, listaFeatures[i])
                    self.checarMalos(capa, listaFeatures[j])
        self.cuentaError = len(geoms)

        if (self.cuentaError == 0):
            return

        

        self.stringError = "Capa: " + nombreCapa + " " + str(self.cuentaError) + " geometrias duplicadas"
        root = QgsProject.instance().layerTreeRoot()
        grupoErrores = root.findGroup('ERRORES DE TOPOLOGIA')
        l1 = QgsVectorLayer()

        if capa.wkbType() == 5 or capa.wkbType() == 2:
            l1 = QgsVectorLayer('LineString?crs=epsg:32614&field=cve_cat:string(15)&index=yes', 'duplicado_' + nombreCapa, 'memory')

        if capa.wkbType() == 1:
            l1 = QgsVectorLayer('Point?crs=epsg:32614&field=cve_cat:string(15)&index=yes', 'duplicado_' + nombreCapa, 'memory')

        self.pintarErrores(l1, geoms)

########################################################################################################

    def validarOverlapLineas(self, capa):

        if capa == None:
            return
        
        features = capa.getFeatures()
        geoms = []

        self.cuentaError = 0
        self.stringError = "None"

        listaFeatures = list(features)
        rango = len(listaFeatures)

        nombreCapa = capa.name()
        print("Validando lineas solapadas: " + nombreCapa)

        for i in range(0, rango-1):
            geometria1 = listaFeatures[i].geometry()
            for j in range(i+1, rango):
                geometria2 = listaFeatures[j].geometry()
                if(geometria1.intersects(geometria2)):
                    gb = geometria1.buffer(0.05, 1)
                    gb1 = geometria2.buffer(0.05, 1)
                    
                    area = gb.intersection(gb1).area()
                    if area > 0.01:
                        geoms.append(geometria1.asWkt())
                        self.checarMalos(capa, listaFeatures[i])
        self.cuentaError = len(geoms)

        if (self.cuentaError == 0):
            return

        

        self.stringError = "Capa: " + nombreCapa  + " se solapan "  + str(self.cuentaError) + " lineas"
        l1 = QgsVectorLayer('LineString?crs=epsg:32614&field=cve_cat:string(15)&index=yes', 'Lineas solapadas ' + nombreCapa, 'memory')

        self.pintarErrores(l1, geoms)

#################################################################################
    
    def validarMultipartes(self, capa):

        if capa == None:
            return

        features = list(capa.getFeatures())

        self.cuentaError = 0
        self.stringError = ""

        nombreCapa = capa.name()
        print("Validando multipartes: " + nombreCapa)

        geoms = []
        for f in features:
            geom = f.geometry()
            
            if geom.wkbType() == 6: # multipoligono
                lista = geom.asMultiPolygon()
                if len(lista) > 1:
                    geoms.append(geom.asWkt())
                    self.checarMalos(capa, f)
        if len(geoms) == 0:
            return

        self.cuentaError = len(geoms)

        

        self.stringError = "Multipartes: "  + nombreCapa + " " + str(self.cuentaError) + " elementos"   
        l1 = QgsVectorLayer('Polygon?crs=epsg:32614&index=yes', 'Geometrias Multiparte ' + nombreCapa, 'memory')
        
        self.pintarErrores(l1, geoms) 

###################################################################################

    def validarAnillos(self, capa):

        if capa == None:
            return

        features = list(capa.getFeatures())

        self.cuentaError = 0
        self.stringError = ""

        nombreCapa = capa.name()
        print("Validando anillos: " + nombreCapa)
        geoms = []
        for f in features:
            geom = f.geometry()
            
            if geom.isGeosValid():
                
                if geom.wkbType() == 3: # poligono
                    lista = geom.asPolygon()
                    if len(lista) > 1:
                        geoms.append(geom.asWkt())
                        self.checarMalos(capa, f)
                if geom.wkbType() == 6: # multipoligono
                    lista = geom.asMultiPolygon()[0]
                    if len(lista) > 1:
                        geoms.append(geom.asWkt())
                        self.checarMalos(capa, f)
        if len(geoms) == 0:
            return

        
        self.cuentaError = len(geoms)
        self.stringError = "Anillos: "  + nombreCapa + " " + str(self.cuentaError) + " elementos"   
        l1 = QgsVectorLayer('Polygon?crs=epsg:32614&index=yes', 'Anillos ' + nombreCapa, 'memory')

        self.pintarErrores(l1, geoms)

###########################################################################################################

    def validarPuntoEnPoligono(self, capaPunto, capaPoligono):

        if capaPunto == None or capaPoligono == None:
            return
        
        featuresPunto = list(capaPunto.getFeatures())
        featuresPoligono = list(capaPoligono.getFeatures())

        self.cuentaError = 0
        self.stringError = ""

        geoms = []

        nombrePunto = capaPunto.name()
        nombrePoligono = capaPoligono.name()
        print("Validando puntos incluidos: " + nombrePunto + " - " + nombrePoligono)

        for punto in featuresPunto:
            cuentaPunto = 0
            for poli in featuresPoligono:
                if punto.geometry().intersects(poli.geometry()):
                    cuentaPunto += 1
            if cuentaPunto != 1:
                geoms.append(punto.geometry().asWkt())
                self.checarMalos(capaPunto, punto)
        self.cuentaError = len(geoms)

        if self.cuentaError == 0:
            return

        
        self.stringError = "Puntos de la capa: " + nombrePunto + " no incluidos en poligonos de la capa " + nombrePoligono + " " + str(self.cuentaError) + " elementos"
        capa = QgsVectorLayer('Point?crs=epsg:32614&field=cve_cat:string(15)&index=yes',  "Puntos de la capa: " + nombrePunto + " no incluidos en poligonos de la capa " + nombrePoligono, 'memory')

        self.pintarErrores(capa, geoms)

############################################################################################################

    def validarToqueCompartido(self, capaObjeto, capaBase):

        if capaObjeto == None or capaBase == None:
            return

        listObj = list(capaObjeto.getFeatures())
        listBase = list(capaBase.getFeatures())

        self.cuentaError = 0
        self.stringError = "None"

        listaError = []

        listaToque = [] 
        nombreObj = capaObjeto.name()
        nombreBase = capaBase.name()   
        print("Validando toque compartido: " + nombreObj + " - " + nombreBase)

        listaSemi = []

        for const in listObj: #Las construcciones que esten totalmente dentro ya la libraron y no son errores
            obj = const.geometry()
            bandera = False
            for predio in listBase:
            
                pre = predio.geometry()

                if obj.buffer(-0.0000002, 1).area() - obj.intersection(pre).area() < 0.0000001: #Cehcamos que el area de la consturccion y su interseccion con el predio sean iguales
                    bandera = True

            if not bandera:

                listaSemi.append(const) #TOdas las construcciones que no estan totalmente dentro de un predio

        listaRayada = [] #Posibles aleros

        for featObj in listaSemi: #Para cada cosntruccion que no esta totalmente dentro del predio
            objeto = featObj.geometry()
            bandera = True
            for featCont in listBase:  #Checamos todos los predios
                contenedor = featCont.geometry()
                if objeto.intersects(contenedor): 
                    inter = objeto.intersection(contenedor)

                    if inter.area() > 0.000001:  #Si la cosntruccion intersecta el predio, no debe exceder una tolerancia, si no pues es solape y eror

                        bandera = False
                        listaError.append(objeto.asWkt())
                        self.checarMalos(capaObjeto, featObj)
                
            if bandera:
                listaRayada.append(featObj)


        for feat1 in listaRayada: #Aleros
            listaCompartida = []
            objeto = feat1.geometry()
            contenido = False

            for feat2 in listBase: #Recorremos todos los predios
                base = feat2.geometry()

                if(objeto.buffer(0.0000001, 1).intersects(base)): #Checamos predios compartidos
                    self.deb(feat1, 10, 'tenemos un compartido ' + str(feat2.id()))
                    listaCompartida.append(feat2)

            if len(listaCompartida) > 1: #Cuando se comparte mas de 1
                
                pasa = False

                cuentaExcede = 0
                for choque in listaCompartida:

                    if objeto.touches(choque.geometry()):
                        pasa = True

                    if objeto.buffer(0.0000001, 1).intersection(choque.geometry()).area() > 0.0000000000001:
                        cuentaExcede += 1

                if cuentaExcede > 1:
                    listaError.append(objeto.asWkt())
                    self.checarMalos(capaObjeto, feat1)
            #De aqui para abajo esta bien
            if len(listaCompartida) == 0:
                #print("Le falto - "  "id: " + str(feat1.id()) + " - Lista compartida: " + str(len(listaCompartida)))
                listaError.append(objeto.asWkt())
                self.checarMalos(capaObjeto, feat1)
        self.cuentaError = len(listaError)

        if self.cuentaError == 0:
            return
        
        
        self.stringError = nombreObj + " sin tocar un solo elemento de " + nombreBase + " " + str(self.cuentaError) + " elementos"
        temp = QgsVectorLayer("Polygon?crs=epsg:32614", nombreObj + " sin tocar un solo elemento de " + nombreBase, "memory")

        self.pintarErrores(temp, listaError)

##########################################################################################################################

    def pintarErrores(self, capa, listaErrores):
        
        
        QgsProject.instance().addMapLayer(capa, False)
        root = QgsProject.instance().layerTreeRoot()
        grupoErrores = root.findGroup('ERRORES DE TOPOLOGIA')
        capaError = QgsLayerTreeLayer(capa)
        capa.startEditing()
        
        for inter in listaErrores:
            
            geom = QgsGeometry()
            geom = QgsGeometry.fromWkt(inter)

            if geom.wkbType() < 7:
                feat = QgsFeature()
                feat.setGeometry(geom)
                capa.dataProvider().addFeatures([feat])
            elif geom.wkbType() == 7 :
                if len(geom.asGeometryCollection()) > 0:
                    for gc in geom.asGeometryCollection():
                        if gc.wkbType() == 3 or gc.wkbType() == 2:
                            feat = QgsFeature()
                            feat.setGeometry(gc)
                            capa.dataProvider().addFeatures([feat])
                else:
                    feat = QgsFeature()
                    feat.setGeometry(geom)
                    capa.dataProvider().addFeatures([feat])

        #Cambiamos el color de la capa a rojo
        renderer  = capa.renderer()

        

        if capa.wkbType() == 3 or capa.wkbType() == 6:
            symbol = QgsFillSymbol.createSimple({'color':'#F5A9A9', 'color_border':'#FF0000', 'width_border':'0.5'})
            renderer.setSymbol(symbol)
        
        elif capa.wkbType() == 2 or capa.wkbType() == 4:
            symbols = capa.renderer().symbols(QgsRenderContext())
            symbol = symbols[0]
            symbol.setColor(QColor.fromRgb(255,0,0))


        #if capa.wkbType() == 5 or capa.wkbType() == 2 or capa.wkbType() == 1 :
        else:
            props = capa.renderer().symbol().symbolLayer(0).properties()
            props['color'] = '#FF0000'
            capa.renderer().setSymbol(QgsMarkerSymbol.createSimple(props))
        
        #Renderizamos la capa con los cambios
        capa.triggerRepaint()
        capa.commitChanges()
        grupoErrores.insertChildNode(0, capaError)


#######################################################################################################################

    def validarPoligonosDuplicados(self, capa):

        if capa == None:
            return

        features = capa.getFeatures()
        geoms = []

        self.cuentaError = 0
        self.stringError = "None"

        listaFeatures = list(features)
        rango = len(listaFeatures)

        nombreCapa = capa.name()
        print("Validando duplicados: " + nombreCapa)

        for i in range(0, rango-1):
            geometria1 = listaFeatures[i].geometry()
            for j in range(i+1, rango):
                geometria2 = listaFeatures[j].geometry()

                if geometria1.equals(geometria2):
                    geoms.append(geometria1.asWkt())
                    self.checarMalos(capa, listaFeatures[i])
                else:
                    area = geometria1.intersection(geometria2).area() - geometria1.area()

                    if (geometria1.area() == geometria2.area() and area < 0.0000001 and area > -0.0000001) or listaFeatures[i] == listaFeatures[j]:
                        geoms.append(geometria1.asWkt())
                        self.checarMalos(capa, listaFeatures[i])

        self.cuentaError = len(geoms)

        if (self.cuentaError == 0):
            return

        
        self.stringError = "Capa: " + nombreCapa + " " + str(self.cuentaError) + " poligonos duplicados"
        root = QgsProject.instance().layerTreeRoot()
        grupoErrores = root.findGroup('ERRORES DE TOPOLOGIA')

        l1 = QgsVectorLayer('Polygon?crs=epsg:32614&field=cve_cat:string(15)&index=yes', 'poligono_duplicado_' + nombreCapa, 'memory')

        self.pintarErrores(l1, geoms)

#############################################################################################################################################

    def validarSoloUnPunto(self, capaPunto, capaPoligono):

        if capaPunto == None or capaPoligono == None:
            return

        featuresPunto = list(capaPunto.getFeatures())
        featuresPoligono = list(capaPoligono.getFeatures())

        self.cuentaError = 0
        self.stringError = ""

        geoms = []

        nombrePunto = capaPunto.name()
        nombrePoligono = capaPoligono.name()
        print("Validando sol un punto: " + nombrePunto + " - " + nombrePoligono)

        for poli in featuresPoligono:
            cuentaPunto = 0
            for punto in featuresPunto:
                if punto.geometry().intersects(poli.geometry()):
                    cuentaPunto += 1
            if cuentaPunto != 1:
                geoms.append(poli.geometry().asWkt())
                self.checarMalos(capaPoligono, poli)

        self.cuentaError = len(geoms)

        if self.cuentaError == 0:
            return

        
        self.stringError = "Debe existir exactamente un punto de la capa " + nombrePunto + " en poligonos de la capa " + nombrePoligono + " " + str(self.cuentaError) + " elementos"
        capa = QgsVectorLayer('Polygon?crs=epsg:32614&field=cve_cat:string(15)&index=yes',  "Puntos de la capa: " + nombrePunto + " no incluidos en poligonos de la capa " + nombrePoligono, 'memory')

        self.pintarErrores(capa, geoms)

####################################################################################################################

    def validarInscritasEnPrediosIrregulares(self):
        capaAreasInscritas = QgsProject.instance().mapLayer(QSettings().value('xAreasInscritas'))
        capaPredios = QgsProject.instance().mapLayer(QSettings().value('xPredGeom'))

        if capaAreasInscritas == None or capaPredios == None:
            return

        self.cuentaError = 0
        self.stringError = ""

        listaError = []

        for insc in capaAreasInscritas.getFeatures():

            geomInsc = insc.geometry()
            bandera = True
            
            for predio in capaPredios.getFeatures():
                geomPredio = predio.geometry()

                if geomInsc.buffer(-0.0000001,1).intersects(geomPredio):
                    if self.estaEscuadradito(geomPredio):
                        bandera = False
                        break

            if not bandera:
                listaError.append(geomInsc.asWkt())
            
        self.cuentaError = len(listaError)

        if self.cuentaError == 0:
            return

        self.stringError = str(self.cuentaError) + " areas inscritas en predios regulares"
        capa = QgsVectorLayer('Polygon?crs=epsg:32614&field=cve_cat:string(15)&index=yes',  "Areas inscritas en predios regulares", 'memory')

        self.pintarErrores(capa, listaError)

###################################################################################################################

    def validarAreasInscritasCuadraditas(self):
        capaAreasInscritas = QgsProject.instance().mapLayer(QSettings().value('xAreasInscritas'))
        capaPredios = QgsProject.instance().mapLayer(QSettings().value('xPredGeom'))

        if capaAreasInscritas == None or capaPredios == None:
            return

        self.cuentaError = 0
        self.stringError = ""

        listaError = []

        for insc in capaAreasInscritas.getFeatures():

            geomInsc = insc.geometry()
            if not self.estaEscuadradito(geomInsc):
                listaError.append(geomInsc.asWkt())

            
        self.cuentaError = len(listaError)

        if self.cuentaError == 0:
            return

        self.stringError = str(self.cuentaError) + " Areas inscritas no cuadradas o rectangulares y con angulos rectos"
        capa = QgsVectorLayer('Polygon?crs=epsg:32614&field=cve_cat:string(15)&index=yes',  "Areas inscritas no cuadradas o rectangulares y con angulos rectos", 'memory')

        self.pintarErrores(capa, listaError)

######################################################################################################################

    def validarCantidadAreasInscritas(self):
        capaAreasInscritas = QgsProject.instance().mapLayer(QSettings().value('xAreasInscritas'))
        capaPredios = QgsProject.instance().mapLayer(QSettings().value('xPredGeom'))

        if capaAreasInscritas == None or capaPredios == None:
            return

        self.cuentaError = 0
        self.stringError = ""

        listaError = []

        for predio in capaPredios.getFeatures():
            geomPredio = predio.geometry()
            #if self.estaEscuadradito(geomPredio):
            #    continue
            bandera = True
            cuentaInter = 0
            for area in capaAreasInscritas.getFeatures():
                if geomPredio.buffer(-0.0000001,1).intersects(area.geometry()):
                    cuentaInter += 1
    
            if cuentaInter > 2:
                bandera = False

            if not bandera:          
                listaError.append(geomPredio.asWkt())
                self.checarMalos(capaPredios, predio)

            
        self.cuentaError = len(listaError)

        if self.cuentaError == 0:
            return

        self.stringError = str(self.cuentaError) + " predios irregulares con mas de dos areas inscritas"
        capa = QgsVectorLayer('Polygon?crs=epsg:32614&field=cve_cat:string(15)&index=yes',  "predios irregulares con mas de dos areas inscritas", 'memory')

        self.pintarErrores(capa, listaError)


###################################################################################################################

    def validarAlMenosUnPunto(self, capaPunto, capaPoligono):

        if capaPoligono == None or capaPunto == None:
            return

        featuresPunto = list(capaPunto.getFeatures())
        featuresPoligono = list(capaPoligono.getFeatures())

        self.cuentaError = 0
        self.stringError = ""

        geoms = []

        nombrePunto = capaPunto.name()
        nombrePoligono = capaPoligono.name()
        print("Validando sol un punto: " + nombrePunto + " - " + nombrePoligono)

        for poli in featuresPoligono:
            cuentaPunto = 0
            for punto in featuresPunto:
                if punto.geometry().intersects(poli.geometry()):
                    cuentaPunto += 1
            if cuentaPunto < 1:
                geoms.append(poli.geometry().asWkt())
                self.checarMalos(capaPoligono, poli)

        self.cuentaError = len(geoms)

        if self.cuentaError == 0:
            return

        
        self.stringError = "Debe existir al menos un punto de la capa " + nombrePunto + " en poligonos de la capa " + nombrePoligono + " " + str(self.cuentaError) + " elementos"
        capa = QgsVectorLayer('Polygon?crs=epsg:32614&field=cve_cat:string(15)&index=yes',  "Puntos de la capa: " + nombrePunto + " no incluidos en poligonos de la capa " + nombrePoligono, 'memory')

        self.pintarErrores(capa, geoms)

#################################################################################################

    def validarInclusionRef(self, nombreObjeto, nombreContenedor):


        listaObjeto = self.obtenerSoloFeaturesRef(nombreObjeto, 'objeto')
        listaContenedor = self.obtenerSoloFeaturesRef(nombreContenedor, 'contenedor')

        #print(len(listaContenedor))
        capaObjeto = QgsProject.instance().mapLayer(self.ACA.obtenerIdCapa( nombreObjeto))
        capaContenedor = QgsProject.instance().mapLayer(self.ACA.obtenerIdCapa( nombreContenedor))

        self.cuentaError = 0
        self.stringError = "None"

        tolerancia = 0.00000001 #Si se pasa de la tolerancia es un error
        listaSalidas = [] #Objetos salidos
        listaSinClave = []

        for featObj in listaObjeto: #Para cada contenedor...
            objeto = featObj.geometry().buffer(-0.5,1)
            bandera = False
            for featCont in listaContenedor:   

                contenedor = featCont.geometry()
                if objeto.intersects(contenedor): #El area del objeto debe ser igual a su interseccion con algo de tolerancia
                    bandera = True
                    inter = objeto.intersection(contenedor)
                    areaContenida = inter.area()
                    areaObjeto = objeto.area()
                    diferencia = areaObjeto - areaContenida
                    if (diferencia > tolerancia):
                        salida = objeto.difference(contenedor)
                        listaSalidas.append(salida.asWkt())
                    else:
                        claveObjeto = featObj['clave']
                        claveCont = featCont.attributes()[self.valorInteresado]
                        
                        #if claveCont != None:
                        claveTotal = claveCont + claveObjeto
                        capaObjeto.startEditing()
                        featObj['cve_cat'] = claveTotal
                        capaObjeto.updateFeature(featObj)
                        capaObjeto.commitChanges()

            if not bandera:
                listaSalidas.append(objeto.asWkt())
            
        self.cuentaError = len(listaSalidas)

        if (self.cuentaError == 0): #Si hay errores...
            return
        #Los dibujamos
        self.stringError = nombreObjeto + " no cubiertos totalmente por " + nombreContenedor + " " + str(self.cuentaError) + " elementos"
        temp = QgsVectorLayer("Polygon?crs=epsg:32614", nombreObjeto + " no cubiertos totalmente por " + nombreContenedor, "memory")

        self.pintarErrores(temp, listaSalidas)

####################################################################################################

    def validarPoligonosInvalidosRef(self, nombreCapa):

        features = self.obtenerSoloFeaturesRef(nombreCapa, 'objeto')

        if features == None:
            return

        #features = capa.getFeatures()
        
        self.cuentaError = 0
        self.stringError = "None"
        self.poligonosValidos = True

        geoms = []

        print("Validando poligonos invalidos: " + nombreCapa)

        for s in features:
            geom = s.geometry()

            if not geom.isGeosValid():
                print('tenemos un error mano')
                geoms.append(geom.asWkt())

        self.cuentaError = len(geoms)

        if (self.cuentaError == 0):
            return

        self.poligonosValidos = False

        self.stringError = "Capa: " + nombreCapa + " " + str(self.cuentaError) + " geometrias invalidas"
        temp = QgsVectorLayer('Polygon?crs=epsg:32614', 'Poligonos Invalidos ' + nombreCapa, 'memory')

        self.pintarErrores(temp, geoms)
    
################################################################################################

    
#################################################################################################


    def validarCamposRef(self, nombreCapa):

        features = self.obtenerSoloFeaturesRef(nombreCapa, 'objeto')

        if features == None:
            return

       
        diccCampos = {}
        diccCampos['Estado'] = ['clave']
        diccCampos['Region Catastral'] = ['clave']
        diccCampos['Municipios'] = ['clave']
        diccCampos['Secciones'] = ['clave']
        diccCampos['Localidades'] = ['clave']
        diccCampos['Sectores'] = ['clave']

        diccCampos['Calles'] = ['calle', 'id_cve_vialidad', 'valor']
        diccCampos['Colonias'] = ['id_tipo_asentamiento', 'descripcion']
        diccCampos['Codigo Postal'] = ['cve_cp']
        diccCampos['Zona Uno'] = ['descripcion']
        diccCampos['Zona Dos'] = ['descripcion']
        diccCampos['Area de Valor'] = ['valor', 'descripcion', 'cve_vus']


        self.cuentaError = 0
        self.stringError = "None"

        geoms = []

        print("Validando campos: " + nombreCapa)

        listaCampos = diccCampos[nombreCapa]

        for feat in features:
            for campo in listaCampos:
                if feat[campo] == None or feat[campo] == '':
                    geom = feat.geometry()
                    geoms.append(geom.asWkt())

        self.cuentaError = len(geoms)

        if (self.cuentaError == 0):
            return


        self.stringError = "Capa: " + nombreCapa + " " + str(self.cuentaError) + " geometrias invalidas"


        if nombreCapa == 'Calles':
            temp = QgsVectorLayer('LineString?crs=epsg:32614', 'Campos Incompletos ' + nombreCapa, 'memory')
        else:
            temp = QgsVectorLayer('Polygon?crs=epsg:32614', 'Campos Incompletos ' + nombreCapa, 'memory')



        self.pintarErrores(temp, geoms)

#############################################################################################

    def validarInterseccionesRef(self, nombreCapa1, nombreCapa2):

        if nombreCapa1 == 'Calles':
            return

        featuresCapa1 = self.obtenerSoloFeaturesRef(nombreCapa1, 'objeto')

        if nombreCapa1 != nombreCapa2:
            featuresCapa2 = self.obtenerSoloFeaturesRef(nombreCapa2, 'objeto')
        else:
            featuresCapa2 = featuresCapa1

        if featuresCapa1 == None or featuresCapa2 == None: 
            return

        
        #Lista de errores
        listaErrores = []

        #Variables para el error
        self.cuentaError = 0
        self.stringError = ""

        tolerancia = 0.0000001
        tamanoBuffer1 = -0.0000001
        tamanoBuffer2 = 0


        if nombreCapa1 == 'Calles':
            tolerancia = 0.05
            tamanoBuffer1 = 0.1
            tamanoBuffer2 = 0.1

        print("Validando intersecciones: " + nombreCapa1 + " - " + nombreCapa2)
        featuresCapa1 = list(featuresCapa1)
        featuresCapa2 = list(featuresCapa2)

        #Operaciones realizadas cuando las capas son distintas
        if (nombreCapa1 != nombreCapa2):
            rango1 = len(featuresCapa1)
            rango2 = len(featuresCapa2)
            for i in range(0, rango1):
                feat1 = featuresCapa1[i]
                for j in range(0, rango2):
                    feat2 = featuresCapa2[j] 
                    #Comparamos las intersecciones
                    if (feat1.geometry().intersects(feat2.geometry())):
                        interseccion = feat1.geometry().buffer(tamanoBuffer1,1).intersection(feat2.geometry().buffer(tamanoBuffer,1))
                        
                        if (interseccion.area() > tolerancia):
                            listaErrores.append(interseccion.asWkt())
        
        #Cuandolas capas a comparar son la misma
        else:
            rango1 = len(featuresCapa1)
            for i in range(0, rango1-1):
                feat1 = featuresCapa1[i]
                for j in range(i+1, rango1):
                    feat2 = featuresCapa1[j]
                    if (feat1.geometry().intersects(feat2.geometry())):
                        interseccion = feat1.geometry().buffer(tamanoBuffer1,1).intersection(feat2.geometry().buffer(tamanoBuffer2,1))
                        #print(feat1.id(), feat2.id())
                        #print(interseccion.area())
                        if(interseccion.area() > tolerancia):
                            #print( str(feat1['id']) + ' - ' + str(feat2['id']) + ' = ' + str(interseccion.area()) )
                            listaErrores.append(interseccion.asWkt()) 

        self.cuentaError = len(listaErrores)

        if (self.cuentaError == 0):
            return

        self.stringError = "Interseccion: " + nombreCapa1 + " - " + nombreCapa2 + " " + str(self.cuentaError) + " elementos"   

        #if nombreCapa1 != 'Calles':
            
        temp = QgsVectorLayer('Polygon?crs=epsg:32614', "Intersecciones: " + nombreCapa1 + " - " + nombreCapa2, 'memory')
        #else:
        #    temp = QgsVectorLayer('LineString?crs=epsg:32614', "Intersecciones: " + nombreCapa1 + " - " + nombreCapa2, 'memory')

        self.pintarErrores(temp, listaErrores)
        

#############################################################################################

    def validarLongitudCampo(self, capa, campo, longitud):
        
        if capa == None:
            return

        self.cuentaError = 0
        self.stringError = "None"

        listaError = []

        capa.startEditing()
        for feat in capa.getFeatures():
            campoV = str(feat[campo])
            if len(campoV) != longitud:
                listaError.append(feat.geometry().asWkt())
                self.checarMalos(capa, feat)
        capa.commitChanges()

        self.cuentaError = len(listaError)

        if (self.cuentaError == 0):
            return

        self.stringError = "Capa: " + capa.name() + " " + str(self.cuentaError) + " longitud de " + str(campo) + " invalida"

        if capa.wkbType() == 3 or capa.wkbType() == 6:
            temp = QgsVectorLayer('Polygon?crs=epsg:32614','('+ capa.name() +')'  +  ' Longitud invalida de ' + campo, 'memory')
        else:
            temp = QgsVectorLayer('Point?crs=epsg:32614','('+ capa.name() +')'  +  ' Longitud invalida de ' + campo, 'memory')
        self.pintarErrores(temp, listaError)

######################################################################################################################################

    def validarCampoNoNulo(self, capa, campo):
        
        if capa == None:
            return

        self.cuentaError = 0
        self.stringError = "None"

        listaError = []

        capa.startEditing()
        for feat in capa.getFeatures():
            campoV = str(feat[campo])
            if campoV == '' or campoV == None or campoV == 'NULL':
                listaError.append(feat.geometry().asWkt())
                self.checarMalos(capa, feat)
        capa.commitChanges()

        self.cuentaError = len(listaError)

        if (self.cuentaError == 0):
            return

        self.stringError = "Capa: " + capa.name() + " " + str(self.cuentaError) + str(campo) + " vacio"

        if capa.wkbType() == 3 or capa.wkbType() == 6:
            temp = QgsVectorLayer('Polygon?crs=epsg:32614','('+ capa.name() +')'  +  ' Campo vacio: ' + campo, 'memory')
        else:
            temp = QgsVectorLayer('Point?crs=epsg:32614','('+ capa.name() +')'  +  ' Campo vacio: ' + campo, 'memory')
        self.pintarErrores(temp, listaError)

##################################################################################################

    def validarCampoNoNuloDoble(self, capa, campo1, campo2):
        
        if capa == None:
            return

        self.cuentaError = 0
        self.stringError = "None"

        listaError = []

        capa.startEditing()
        for feat in capa.getFeatures():
            campoV1 = str(feat[campo1])
            campoV2 = str(feat[campo2])
            if (campoV1 == '' or campoV1 == None or campoV1 == 'NULL') and (campoV2 == '' or campoV2 == None or campoV2 == 'NULL'):
                listaError.append(feat.geometry().asWkt())
                self.checarMalos(capa, feat)
        capa.commitChanges()

        self.cuentaError = len(listaError)

        if (self.cuentaError == 0):
            return

        self.stringError = "Capa: " + capa.name() + " " + str(self.cuentaError) + str(campo1) + ' y ' + str(campo2) + " vacios"

        if capa.wkbType() == 3 or capa.wkbType() == 6:
            temp = QgsVectorLayer('Polygon?crs=epsg:32614','('+ capa.name() +')'  +  str(campo1) + ' y ' + str(campo2) + " vacios", 'memory')
        else:
            temp = QgsVectorLayer('Point?crs=epsg:32614','('+ capa.name() +')'  +  str(campo1) + ' y ' + str(campo2) + " vacios", 'memory')
        self.pintarErrores(temp, listaError)

################################################################################################

    def validarCamposDuplicados(self, capaContenedor, capaObjeto, campo):

        if capaContenedor == None or capaObjeto == None:
            return

        self.cuentaError = 0
        self.stringError = "None"

        listaError = []

        capaObjeto.startEditing()
        #listaDatos = [feat[campo] for feat in capaObjeto.getFeatures()]
        for cont in capaContenedor.getFeatures():
            geomCont = cont.geometry()
            listaDentro = []
            for obj in capaObjeto.getFeatures():
                geomObj = obj.geometry()
                if geomCont.intersects(geomObj.buffer(-0.0000001,1)) or geomCont.intersection(geomObj.buffer(0.0000001,1)).area() >0.0000000001 and self.contarIntegraciones(geomObj.buffer(-0.0000001,1), 'predios.geom') == 0:
                    listaDentro.append(obj)
            
            listaDatos = [feat[campo] for feat in listaDentro]
            
            for dentro in listaDentro:
                campoV = dentro[campo]
                if campoV == '' or campoV == 'NULL' or campoV == None:
                    continue
                if listaDatos.count(campoV) > 1:
                    listaError.append(dentro.geometry().asWkt())
                    self.checarMalos(capaObjeto, dentro)
        capaObjeto.commitChanges()

        self.cuentaError = len(listaError)

        if (self.cuentaError == 0):
            return

        self.stringError = "Capa: " + capaObjeto.name() + " " + str(self.cuentaError) + str(campo) + " repetido"

        if capaObjeto.wkbType() == 3 or capaObjeto.wkbType() == 6:
            temp = QgsVectorLayer('Polygon?crs=epsg:32614','('+ capaObjeto.name() +')'  +  ' Campo repetido: ' + campo, 'memory')
        else:
            temp = QgsVectorLayer('Point?crs=epsg:32614','('+ capaObjeto.name() +')'  +  ' Campo repetido: ' + campo, 'memory')
        self.pintarErrores(temp, listaError)





#########################################################################################
    def deb(self, feat, id, mensaje):
        if feat.id() == id:
            print(mensaje)

    def deb2(self, feat1, feat2, id1, id2, mensaje):
        if feat1.id() == id1 and feat2.id() == id2:
            print(mensaje)

#########################################################################################

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

##################################################################################################################

    def estaEscuadradito(self, geometria):
        vertices = self.obtenerVertices(geometria)
            
        rango = len(vertices)
        total = 0
        listaGrados = []
        for x in range(0, rango-1):
            p1 = vertices[x]
            p2 = vertices[x+1]

            dx = p2.x() - p1.x()
            dy = p2.y() - p1.y()
            #rads = math.atan2 (dy, dx) #wrong for finding angle/declination?
            grados = math.degrees(math.atan2(dy, dx))
            if grados < 0:
                grados += 180

            grados = int(grados)
            listaGrados.append(grados)

        for x in range(0, len(listaGrados)):
            
            if listaGrados.count(listaGrados[x]) != 2:
                return False
                
        return True

##########################################################################################################

    def obtenerVertices(self, geom):
        n  = 0
        ver = geom.vertexAt(0)
        vertices=[]

        while(ver != QgsPoint(0,0)):
            n +=1
            vertices.append(ver)
            ver=geom.vertexAt(n)

        return vertices

#############################################################################################################################

    def contarIntegraciones(self, geometria, nombreCapa):
        capa = QgsProject.instance().mapLayer(self.ACA.obtenerIdCapa(nombreCapa))
        cuenta = 0
        for feat in capa.getFeatures():
            if geometria.intersects(feat.geometry()):
                cuenta += 1

        return cuenta

##########################################################################################################################

    def checarMalos(self, capa, feat):

        if capa.id() == self.idManzanas:
            if not feat.id() in self.manzanasMalas:
                self.manzanasMalas.append(feat.id())
        elif capa.id() == self.idPredios:
            if not feat.id() in self.prediosMalos:
                self.prediosMalos.append(feat.id())
        elif capa.id() == self.idConst:
            if not feat.id() in self.constMalas:
                self.constMalas.append(feat.id())