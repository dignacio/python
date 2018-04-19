
import qgis
from qgis.utils import iface
from qgis.core import *
from PyQt5.QtCore import QFileInfo, QSettings, QCoreApplication
from PyQt5.QtWidgets import QAction, QMessageBox
from PyQt5.QtGui import *
import json, requests, os


class Startup():

    def __init__(self):
        menuVector = iface.vectorMenu().actions()
        menuOpciones = iface.settingsMenu().actions()
        menuPlug = iface.pluginMenu().actions()
        helpBar = iface.helpToolBar()

        QSettings().setValue('listaEliminada', [])
        QSettings().setValue('listaEliminadaRef', [])
        QSettings().setValue('capaRefEdicion', 'None')

        self.tablas = {'manzana': 'e_manzana', 'predios.geom': 'e_predio', 'construcciones': 'e_construccion',  'horizontales.geom':'e_condominio_horizontal', 'verticales':'e_condominio_vertical', 'cves_verticales':'e_condominio_vert_clave'}

        self.modoDesarrollo = True

        clickFuga = QAction(QIcon("C:/AplicacionQGIS/reload.png"), QCoreApplication.translate("Groundwater Modeling", "Cerrar Sesion"), iface.mainWindow())
        clickCerrar = QAction(QIcon("C:/AplicacionQGIS/cerrar.png"), QCoreApplication.translate("Groundwater Modeling", "Cerrar Sesion"), iface.mainWindow())
        clickBorrarTodoAlv = QAction(QIcon("C:/AplicacionQGIS/borrartodoalv.png"), QCoreApplication.translate("Groundwater Modeling", "Cerrar Sesion"), iface.mainWindow())
        clickGuardar = QAction(QIcon("C:/AplicacionQGIS/guardar.png"), QCoreApplication.translate("Groundwater Modeling", "Guardar Cambios"), iface.mainWindow())

        clickFuga.triggered.connect(self.cerrarSinPreguntar)
        clickCerrar.triggered.connect(self.preguntarCerrarSesion)
        clickBorrarTodoAlv.triggered.connect(self.borrarTodoAlv)
        clickGuardar.triggered.connect(self.guardarCambios)

        helpBar.addAction(clickFuga)
        helpBar.addAction(clickGuardar)
        helpBar.addAction(clickBorrarTodoAlv)
        
        self.var = QSettings()
        self.var.setValue("reglasTopologicas", [])
        self.var.setValue("posibleGuardar", "False")

    def borrarTodoAlv(self):
        grupoLayers =  QgsProject.instance().layerTreeRoot().findGroup('consulta')
        layers = grupoLayers.findLayers()
        for layer in layers:
            layer.layer().startEditing()
            for f in layer.layer().getFeatures():
                layer.layer().dataProvider().deleteFeatures([f.id()])
            layer.layer().triggerRepaint()
            layer.layer().commitChanges()

    def cerrarSinPreguntar(self):
        os.kill(os.getpid(), 9)


    def mostrarConsola(self):

        iface.actionShowPythonDialog().trigger()
        print ('CONSOLA INICIADA')

    def checarLogin(self):
        
        archivo = open('C:/AplicacionQGIS/start.det', 'r') #Abrimos el archivo generado por C#
        
        self.var.setValue("usoLogin", archivo.readline().replace('\n', ''))

        if(self.var.value("usoLogin") == "True"):
            self.var.setValue("token", archivo.readline().replace('\n', ''))
            self.var.setValue("logeado", archivo.readline().replace('\n', ''))
            
        else:
            self.var.setValue("token", "None")
            self.var.setValue("logeado", "Flase")

        log = self.var.value("logeado")
        sal = self.var.value("salida")

        archivo.close()

        #DESCOMENTAR LO SIGUIENTE
        if(self.var.value("usoLogin") == "True"):
            archivo = open('C:/AplicacionQGIS/start.det', 'r+')
            archivo.truncate()
            archivo.close()
        

        if log == "True" or self.modoDesarrollo:  
            cargarCapas()
            #cargarWebService()
            agregarBotones()


    def preguntarCerrarSesion(self):
        
        mensaje = "Se perderan las capas de los grupos de consulta y referencia, ademas de las reglas de topologia\nDeseas continuar?"
        respuesta = QMessageBox.question(iface.mainWindow(), "Nota de cierre de sesion", mensaje, QMessageBox.Yes, QMessageBox.No)

        if respuesta == QMessageBox.Yes:
            cerrarSesion()


    def preguntarGuardar(self):
        
        if QSettings().value("token") != "None" or self.modoDesarrollo:

            if QSettings().value("posibleGuardar") == "True" or self.modoDesarrollo:
            
                mensaje = "Deseas guardar los cambios?"
                respuesta = QMessageBox.question(iface.mainWindow(), "Guardar Cambios", mensaje, QMessageBox.Yes, QMessageBox.No)

                if respuesta == QMessageBox.Yes:
                    guardarCambios()
            
            else:
                createAlert('No es posible guardar los cambios debido a \n que no se ha validado la topologia', QMessageBox.Critical, 'Error al guardar cambios')

        else:
            createAlert('Inicia Sesion', QMessageBox.Critical, 'Guardar Cambios')
            ocultarIconos()

######################################################################################################################

    def cerrarSesion(self):

        if QSettings().value("token") != "None":
                #Creamos instancia del proyecto
            proyecto = QgsProject.instance()

            #Creamos la raiz
            root = QgsProject.instance().layerTreeRoot()

            #Borramos el grupo consulta y sus capas
            group = root.findGroup('consulta')
            if not group is None:
                for child in group.children():
                    dump = child.dump()
                    id = dump.split("=")[-1].strip()
                    QgsProject.instance().removeMapLayer(id)
                root.removeChildNode(group)

            #Borramos el grupo referencia y sus capas
            group = root.findGroup('referencia')
            if not group is None:
                for child in group.children():
                    dump = child.dump()
                    id = dump.split("=")[-1].strip()
                    QgsProject.instance().removeMapLayer(id)
                root.removeChildNode(group)

            #Devolver token
            QSettings().setValue("token", "None")
            QSettings().setValue("logeado", "False")
            #QSettings().setValue("salida", "True")
            ocultarIconos()

        else:
            createAlert('La sesion ya ha sido cerrada', QMessageBox.Critical, 'Cerrar Sesion')
            ocultarIconos()

######################################################################################################################
        
    def ocultarIconos(self):
        contadorHelp = 0
        for item in helpBar.actions():
            if(contadorHelp > 0):
                item.setVisible(False)
            contadorHelp = contadorHelp + 1

########################################################################################################################

    def guardarCambios(self):

        print('entro al guardar')

        
        root = QgsProject.instance().layerTreeRoot()

        group = root.findGroup('ERRORES DE TOPOLOGIA')
        if not group is None:
            for child in group.children():
                dump = child.dump()
                id = dump.split("=")[-1].strip()
                QgsProject.instance().removeMapLayer(id)
            root.removeChildNode(group)

        for layer in iface.mapCanvas().layers():
            layer.triggerRepaint()

        if self.var.value('posibleGuardar') == 'True':
            print('fue posible guardar')
            self.listaAGuardar = []

            self.agregarALista('manzana')
            self.agregarALista('predios.geom')
            self.agregarALista('construcciones')
            self.agregarALista('horizontales.geom')
            self.agregarALista('verticales')
            self.agregarALista('cves_verticales')
            self.agregarAListaEliminados()

            
            #Formato para solicitar la peticion
            jsonParaGuardarAtributos = json.dumps(self.listaAGuardar)

            print (jsonParaGuardarAtributos)
            
            #try:
            
            url='http://192.168.0.40:8080/featureswkn/api/manzana/'
            payload = jsonParaGuardarAtributos
            headers = {'Content-Type': 'application/json', 'Authorization' : self.obtenerToken()}
            try:
                response = requests.post(url, headers = headers, data = payload)
            
            except requests.exceptions.RequestException:
                self.createAlert("No se ha podido conectar al servidor v1", QMessageBox.Critical, "Guardar Cambios v1")#Error en la peticion de consulta
            
            print(response.json())
            print(response.status_code)
            if response.status_code == 200:
                self.createAlert("Cambios guardados con exito", QMessageBox.Information, "Guardar Cambios")
                QSettings().setValue('listaEliminada', [])
                #Guardado de datos correcto
            elif response.status_code == 202:

                root.insertGroup(0, 'ERRORES DE TOPOLOGIA')

                capa = QgsVectorLayer('Point?crs=epsg:32614&field=mensaje:string(80)', 'ERRORES PUNTO', 'memory')

                QgsProject.instance().addMapLayers([capa], False)

                props = capa.renderer().symbol().symbolLayer(0).properties()
                props['color'] = '#FF0000'
                capa.renderer().setSymbol(QgsMarkerSymbol.createSimple(props))

                self.etiquetarCapa(capa.name())

                QgsProject.instance().addMapLayer(capa, False)
                grupoErrores = root.findGroup('ERRORES DE TOPOLOGIA')
                capaError = QgsLayerTreeLayer(capa)
                capa.startEditing()

                puntosMalos = response.json()
                #print (type(puntosMalos))

                for malo in puntosMalos:
                    
                    #print(malo)
                    #print(type(malo))
                    geom = QgsGeometry.fromWkt(malo["wkt"])
                    feat = QgsFeature()
                    feat.setGeometry(geom)
                    feat.setAttributes([malo['mensaje']])
                    capa.dataProvider().addFeatures([feat])
                    capa.updateFeature(feat)

                capa.triggerRepaint()
                capa.commitChanges()
                grupoErrores.insertChildNode(0, capaError)

            else:
                self.createAlert("No se ha podido conectar al servidor v2\n" + str(response.json()[0]['mensaje']), QMessageBox.Critical, "Guardar Cambios v2")
                #Error al guardar datos

            #except ValueError:
                #self.createAlert("No se ha podido conectar al servidor v3", QMessageBox.Critical, "Guardar Cambios v3")
            
        else:
            self.createAlert("Se debe validar la topologia antes de guardar", QMessageBox.Critical, "Guardar Cambios v4")
        

        QSettings().setValue('posibleGuardar', 'False')

#######################################################################################################################

    def agregarALista(self, nombreCapa):

        capa = QgsProject.instance().mapLayersByName(nombreCapa)[0]
        listaTemp = []

        for feat in capa.getFeatures():
            campos = {}
            campos['wkt'] = feat.geometry().asWkt()
            campos['srid'] = 32614
            campos['tabla'] = self.tablas[capa.name()]
            atributos = {}
            nombresAtrbutos = capa.fields()   

            nombres = [campo.name() for campo in nombresAtrbutos]

            for x in range(0, len(nombres)):
                atributo = feat.attributes()[x]
                if str(feat.attributes()[x]) == "NULL":
                    atributo = None
                atributos[str(nombres[x])] = atributo
                
                if capa.name() == ('predios.geom'):
                    punto = self.exteriorPredio(feat.geometry())
                    if punto != None:
                        atributos['num_ext'] = punto['num_ext']
                        atributos['geom_num'] = punto.geometry().asWkt()

                elif capa.name() == ('horizontales.geom'):
                    punto = self.exteriorCondom(feat.geometry())
                    if punto != None:
                        atributos['num_ofi'] = punto['num_ofi']
                        atributos['geom_num'] = punto.geometry().asWkt()
                    
            campos['attr'] = atributos
            if campos['attr']['id'] == None:
                campos['nuevo'] = True
                campos['eliminado'] = False
            else:
                campos['nuevo'] = False
                campos['eliminado'] = False
            self.listaAGuardar.append(campos)

############################################################################################

    def agregarAListaEliminados(self):

        listaTemp = QSettings().value('listaEliminada')

        for elemento in listaTemp:
            self.listaAGuardar.append(elemento)

#############################################################################################

    def obtenerCapa(self, feat):
        if feat.fields() == self.capaManzana.fields():
            capa = self.capaManzana
        elif feat.fields() == self.capaPrediosGeom.fields():
            capa = self.capaPrediosGeom
        elif feat.fields() == self.capaPrediosNum.fields():
            capa = self.capaPrediosNum
        elif feat.fields() == self.capaConstrucciones.fields():
            capa = self.capaConstrucciones
        elif feat.fields() == self.capaHorizontalesGeom.fields():
            capa = self.capaHorizontalesGeom
        elif feat.fields() == self.capaHorizontalesNum.fields():
            capa = self.capaHorizontalesNum
        elif feat.fields() == self.capaVerticales.fields():
            capa = self.capaVerticales
        elif feat.fields() == self.capaCvesVert.fields():
            capa = self.capaCvesVert

        return capa

#####################################################################################################################

    def exteriorPredio(self, predio):

        puntos = QgsProject.instance().mapLayersByName('predios.num')[0].getFeatures()

        for punto in puntos:
            if punto.geometry().intersects(predio):
                return punto

    def exteriorCondom(self, condominio):

        puntos = QgsProject.instance().mapLayersByName('horizontales.num')[0].getFeatures()

        for punto in puntos:
            if punto.geometry().intersects(condominio):
                return punto

###########################################################################################

    #Metodo que crea un elemento QMessageBox
    def createAlert(self, mensaje, icono, titulo):
        #Create QMessageBox
        msg = QMessageBox()
        #Add message
        msg.setText(mensaje)
        #Add icon of critical error
        msg.setIcon(icono)
        #Add tittle
        msg.setWindowTitle(titulo)
        #Show of message dialog
        msg.show()
        # Run the dialog event loop
        result = msg.exec_()


    def cargarCapas(self):
        
        url = 'http://192.168.0.30:1093/api/cat/municipio/'

        headers = {'Content-Type': 'application/json'}

        #respuesta = requests.get(url, headers = headers)



        if (self.modoDesarrollo):

            srid = 32614
            #srid = respuesta.json()[0]['srid']
            self.var.setValue("srid", srid)

            root = QgsProject.instance().layerTreeRoot()
            root.addGroup('consulta')

            root.addGroup('referencia')
            #root.addGroup('edicion')

            #Creamos las capas
            capaManzana = QgsVectorLayer('Polygon?crs=epsg:' + str(srid) +'&field=id:string(50)&field=cve_cat:string(50)&field=clave:string(50)&index=yes', 'manzana', 'memory')
            capaPredioGeom = QgsVectorLayer('Polygon?crs=epsg:' + str(srid) +'&field=id:string(50)&field=cve_cat:string(50)&field=clave:string(50)&field=cve_cat_ant:string(50)&field=cve_usuario:string(50)&field=id_manzana:string(50)&field=cve_tipo_pred:string(50)&field=num_ext:string(50)&field=num_predio:string(50)&field=fecha_act:string(50)&field=fondo:string(50)&field=frente:string(50)&field=perimetro:string(50)&field=sup_terr:string(50)&field=cve_vus:string(50)&field=cve_uso_suelo:string(50)&field=id_area_valor:string(50)&field=id_facilidad_comunicacion:string(50)&field=nivel:string(50)&field=id_predio_forma:string(50)&field=id_predio_ubicacion_manzana:string(50)&field=id_regimen_propiedad:string(50)&field=id_tipo_relieve:string(50)&field=id_uso_predio:string(50)&field=nombre:string(50)&field=num_exterior_alf:string(50)&field=num_exterior_ant:string(50)&field=observaciones:string(50)&field=valor_catastral:string(50)&field=valor_construccion:string(50)&field=valor_terreno:string(50)&field=geom_num:string(50)', 'predios.geom', 'memory')
            capaPredioNum = QgsVectorLayer('Point?crs=epsg:' + str(srid) + '&field=num_ext:string(50)', 'predios.num', 'memory')
            capaConst = QgsVectorLayer('Polygon?crs=epsg:' + str(srid) +'&field=id:string(50)&field=id_predio:string(50)&field=cve_catastral:string(50)&field=fecha_act:string(50)&field=nom_volumen:string(50)&field=sup_const:string(50)&field=num_niveles:string(50)&field=volumen:string(50)&field=guardado:string(50)&field=id_cat_estado_construccion:string(50)&field=id_tipo_construccion:string(50)&field=cve_const_esp:string(50)&field=id_condominio_vertical:string(50)&field=horizontal:string(50)&field=geom_vol:string(50)&field=anio_construccion:string(50)&field=codigo_construccion:string(50)&field=id_factor:string(50)&field=id_categoria:string(50)&field=nombre:string(50)&field=tipo_calculo:string(50)&field=valor_const:string(50)&field=id_cat_destino:string(50)', 'construcciones', 'memory')
            capaHorizontalGeom = QgsVectorLayer('Polygon?crs=epsg:' + str(srid) + '&field=id:string(50)&field=cve_cat:string(50)&field=clave:string(50)&field=cve_cat_ant:string(50)&field=cve_usuario:string(50)&field=id_manzana:string(50)&field=id_predio:string(50)&field=fecha_act:string(50)&field=num_ofi:string(50)&field=perimetro:string(50)&field=indiviso:string(50)&field=valor_construccion_priv:string(50)&field=valor_construccion_comun:string(50)&field=valor_terreno_priv:string(50)&field=valor_terreno_comun:string(50)&field=pct_ind_rest:string(50)&field=sup_terr_rest:string(50)&field=sup_const_rest:string(50)&field=tipo_calc_ind:string(50)&field=valor_const_exc:string(50)&field=valor_terr_exc:string(50)&field=sup_const_comun_ex:string(50)&field=sup_terr_comun_ex:string(50)&field=sup_ind_mixto:string(50)&field=sup_construccion_comun:string(50)&field=sup_construccion_privada:string(50)&field=sup_ter_comun:string(50)&field=sup_ter_privada:string(50)&field=geom_num:string(50)', 'horizontales.geom', 'memory')
            capaHorizontalNum = QgsVectorLayer('Point?crs=epsg:' + str(srid) + '&field=num_ofi:string(50)', 'horizontales.num', 'memory')
            capaVertical = QgsVectorLayer('Polygon?crs=epsg:' + str(srid) + '&field=id:string(50)&field=cve_cat:string(50)&field=clave:string(50)&field=edificio_nombre:string(50)', 'verticales', 'memory')
            capaCveVertical = QgsVectorLayer('Point?crs=epsg:' + str(srid) + '&field=id:string(50)&field=cve_cat:string(50)&field=clave:string(50)&field=cve_cat_ant:string(50)&field=cve_usuario:string(50)&field=id_manzana:string(50)&field=id_predio:string(50)&field=fecha_act:string(50)&field=num_ofi:string(50)&field=indiviso:string(50)&field=valor_construccion_priv:string(50)&field=valor_construccion_comun:string(50)&field=valor_terreno_priv:string(50)&field=valor_terreno_comun:string(50)&field=valor_terreno_priv:string(50)&field=valor_terreno_comun:string(50)&field=pct_ind:string(50)&field=pct_ind_rest:string(50)&field=sup_terr_rest:string(50)&field=sup_const_rest:string(50)&field=tipo_calc_ind:string(50)&field=valor_const_exc:string(50)&field=valor_terr_exc:string(50)&field=sup_const_comun_ex:string(50)&field=sup_terr_comun_ex:string(50)&field=sup_ind_mixto:string(50)&field=sup_construccion_comun:string(50)&field=sup_construccion_privada:string(50)&field=sup_ter_comun:string(50)&field=sup_ter_privada:string(50)', 'cves_verticales', 'memory')
            
            print(capaManzana.id())

            #Renderizado de manzanas
            renderManzana = capaManzana.renderer()
            symbolManzana = QgsFillSymbol.createSimple({'color':'255,0,0,0', 'color_border':'#F5A9F2', 'width_border':'0.5'})
            renderManzana.setSymbol(symbolManzana)

            #Renderizado de predios
            renderPredio = capaPredioGeom.renderer()
            symbolPredio = QgsFillSymbol.createSimple({'color':'255,0,0,0', 'color_border':'#00ff00', 'width_border':'0.5'})
            renderPredio.setSymbol(symbolPredio)

                    #REnderizado predios num
            propsPred = capaPredioNum.renderer().symbol().symbolLayer(0).properties()
            propsPred['color'] = '#00FF00'
            capaPredioNum.renderer().setSymbol(QgsMarkerSymbol.createSimple(propsPred))


            #Renderizado de construcciones mediante reglas
            road_rules = (
                ('Construccion', ' "id_tipo_construccion" = 1 OR "id_tipo_construccion" is NULL'),
                ('Const_Esp',  'NOT "id_tipo_construccion" = 1 '),
            )

            symbolConst = QgsSymbol.defaultSymbol(capaConst.geometryType())
            rendererConst = QgsRuleBasedRenderer(symbolConst)

            fillConst = QgsFillSymbol.createSimple({'color':'255,0,0,0', 'color_border':'#000000', 'width_border':'0.5'})
            fillEsp = QgsFillSymbol.createSimple({'color':'255,0,0,0', 'color_border':'#00FFFF', 'width_border':'0.5'})

            # get the "root" rule
            root_rule = rendererConst.rootRule()

            for label, expression in road_rules:
                # create a clone (i.e. a copy) of the default rule
                rule = root_rule.children()[0].clone()
                # set the label, expression and color
                rule.setLabel(label)
                rule.setFilterExpression(expression)

                if label == "Construccion":
                    rule.setSymbol(fillConst)
                else:
                    rule.setSymbol(fillEsp)

                root_rule.appendChild(rule)

            root_rule.removeChildAt(0)

            # apply the renderer to the layer
            capaConst.setRenderer(rendererConst)

            #Renderizado horizontal
            renderHorizontal = capaHorizontalGeom.renderer()
            symbolHorizontal = QgsFillSymbol.createSimple({'color':'255,0,0,0', 'color_border':'#C68C21', 'width_border':'0.5'})
            renderHorizontal.setSymbol(symbolHorizontal)
            
            #Renderizado horizontales num
            propsHor = capaHorizontalNum.renderer().symbol().symbolLayer(0).properties()
            propsHor['color'] = '#C68C21'
            capaHorizontalNum.renderer().setSymbol(QgsMarkerSymbol.createSimple(propsHor))

            #Renderizado vertical
            renderVertical = capaVertical.renderer()
            symbolVertical = QgsFillSymbol.createSimple({'color':'255,0,0,0', 'color_border':'#ff9900', 'width_border':'0.5'})
            renderVertical.setSymbol(symbolVertical)
            
            props = capaCveVertical.renderer().symbol().symbolLayer(0).properties()
            props['color'] = '#ff9900'
            capaCveVertical.renderer().setSymbol(QgsMarkerSymbol.createSimple(props))

            #Tipo BOLD para letras
            capaManzana.setCustomProperty("labeling/namedStyle", "Bold")
            capaPredioGeom.setCustomProperty("labeling/namedStyle", "Bold")
            capaPredioNum.setCustomProperty("labeling/namedStyle", "Bold")
            capaConst.setCustomProperty("labeling/namedStyle", "Bold")
            capaHorizontalGeom.setCustomProperty("labeling/namedStyle", "Bold")
            capaHorizontalNum.setCustomProperty("labeling/namedStyle", "Bold")
            capaVertical.setCustomProperty("labeling/namedStyle", "Bold")
            capaCveVertical.setCustomProperty("labeling/namedStyle", "Bold")

            #Agregamos las capas
            QgsProject.instance().addMapLayers([capaManzana,capaPredioGeom, capaPredioNum, capaConst, capaHorizontalGeom, capaHorizontalNum, capaVertical, capaCveVertical], False)

            arbolManzana = QgsLayerTreeLayer(capaManzana)
            arbolPredioGeom = QgsLayerTreeLayer(capaPredioGeom)
            arbolPredioNum = QgsLayerTreeLayer(capaPredioNum)
            arbolConst = QgsLayerTreeLayer(capaConst)
            arbolHorizontalGeom = QgsLayerTreeLayer(capaHorizontalGeom)
            arbolHorizontalNum = QgsLayerTreeLayer(capaHorizontalNum)
            arbolVertical = QgsLayerTreeLayer(capaVertical)
            arbolCveVertical = QgsLayerTreeLayer(capaCveVertical)

            consulta = root.findGroup('consulta')

            consulta.insertChildNode(0, arbolCveVertical)
            consulta.insertChildNode(0, arbolVertical)
            consulta.insertChildNode(0, arbolHorizontalNum)
            consulta.insertChildNode(0, arbolHorizontalGeom)
            consulta.insertChildNode(0, arbolConst)
            consulta.insertChildNode(0, arbolPredioNum)
            consulta.insertChildNode(0, arbolPredioGeom)
            consulta.insertChildNode(0, arbolManzana)
            
            
            self.ineditarCapa('manzana')
            self.ineditarCapa('predios.geom')
            self.ineditarCapa('predios.num')
            self.ineditarCapa('construcciones')
            self.ineditarCapa('horizontales.geom')
            self.ineditarCapa('horizontales.num')
            self.ineditarCapa('verticales')
            self.ineditarCapa('cves_verticales')

            self.etiquetarCapa('manzana')
            self.etiquetarCapa('predios.geom')
            self.etiquetarCapa('predios.num')
            self.etiquetarCapa('construcciones')
            self.etiquetarCapa('horizontales.geom')
            self.etiquetarCapa('horizontales.num')
            self.etiquetarCapa('verticales')
            self.etiquetarCapa('cves_verticales')

            

    def etiquetarCapa(self, nombreCapa):

        capa = QgsProject.instance().mapLayersByName(nombreCapa)[0]
        etiquetaField = ""
        colorCapa = ""
        esExpresion = False
        if nombreCapa == "manzana":
            etiquetaField = "clave"
            colorCapa = QColor(255,0,0)
        elif nombreCapa == "predios.geom":
            etiquetaField = "clave"
            colorCapa = QColor(0,255,0)
        elif nombreCapa == "predios.num":
            etiquetaField = "num_ext"
            colorCapa = QColor(0,255,0)
        elif nombreCapa == "construcciones":
            etiquetaField = " if( id_tipo_construccion = 1, concat(nom_volumen, '\\n', num_niveles), concat(nom_volumen, '\\n', cve_const_esp))"
            esExpresion = True
            colorCapa = QColor(0,0,255)
        elif nombreCapa == "horizontales.geom":
            etiquetaField = "clave"
            colorCapa = QColor(198,140,33)
        elif nombreCapa == "horizontales.num":
            etiquetaField = "num_ofi"
            colorCapa = QColor(198,140,33)
        elif nombreCapa == "verticales":
            etiquetaField = "clave"
            colorCapa = QColor(255,153,0)
        elif nombreCapa == "cves_verticales":
            etiquetaField = "clave"
            colorCapa = QColor(255,153,0)
        else:
            etiquetaField = "mensaje"
            colorCapa = QColor(255,153,0)
        
        settings = QgsPalLayerSettings()
        settings.fieldName = etiquetaField
        settings.enabled = True
        settings.isExpression = esExpresion
        
        settings.centroidWhole = True

        textFormat = QgsTextFormat()
        textFormat.setColor(colorCapa)
        textFormat.setSize(8)
        textFormat.setNamedStyle('Bold')

        settings.setFormat(textFormat)

        #settings.placement= QgsPalLayerSettings.OverPoint
        labeling = QgsVectorLayerSimpleLabeling(settings)

        capa.setLabeling(labeling)
        capa.setLabelsEnabled(True)
        capa.triggerRepaint()


    def ineditarCapa(self, nombreCapa):
        #Predios ineditables

        capa = QgsProject.instance().mapLayersByName(nombreCapa)[0]

        campos = capa.fields()   
        nombres = [field.name() for field in campos]

        for i in range (0, len(nombres)):
            config = capa.editFormConfig()
            config.setReadOnly(i, True)
            capa.setEditFormConfig(config)

    def cargarWebService(self):

        #token = "bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX25hbWUiOiJhZG1pbiIsInNjb3BlIjpbIm9wZW5pZCJdLCJleHAiOjE1MTk2ODcwMzgsImlhdCI6MTUxOTY4NjczOCwiYXV0aG9yaXRpZXMiOlsiUk9MRV9BRE1JTiIsIlJPTEVfVVNFUiJdLCJqdGkiOiJkMzI1ZWQ4Ni1iNmVlLTQ3ZDktYWI4YS1lYzE3YjgwMDNjNzEiLCJjbGllbnRfaWQiOiJ3ZWJfYXBwIn0.TMXvDbwtfMJLK_1UnnoTySt0TZ4o_4H1tp-A1CHBDlnU0aCQWnfcj3ja6jD5RAsNKmlc-5HD1gvRlFdKt5D9BBbLxykswD161N2690iurCV0NkjhmMia7yt8-X0EOI1vQoEyf7GdnzFo6Bi5fpmFE6YSS9LMZaxCy4NVhLRfqgNgq9ExKd4igedRSMmSVpQ5oV0u-5__7-sB07n3KCwGZjXeRJgVZQuKUiNI8pPljsY8X56vqYPlJlBNLzIjGjjxR_bkiYaXTdytd9LckbwSnm0914KHkIEhr66PS548V58nZfSAovLofaqV7-VCWViPo3SgvmuLDVxwdFem4b4ipQ"
        token = "bearer " + QSettings().value("token")

        cabecera = {'Content-type': 'application/json', 'Authorization' : token}

            #url del service
        url = 'http://192.168.0.50:8080/configuracion/api/adm-capas/getAllCapasConfiguration'

        respuesta = requests.get(url, headers = cabecera)

        if respuesta.status_code == 200:

            datos = respuesta.json()


            #Leemos los objetos capa del json
            for objeto in datos:

                stringDatos = "" #Los datos de la capa los guardamemos en un string

                #obtenemos el srid
                srid = objeto["catDependencia"]["municipio"]["srid"]

                #cargamos el srid en el string de los datos
                #stringDatos += objeto["layerType"]
                stringDatos += "Polygon"
                stringDatos += '?crs=epsg:'
                stringDatos += str(srid)

                #Obtenemos la dependencia de del objeto capa
                dependencia = objeto["catDependencia"]["nombre"]

                #Obtenemos los atributos de la capa y los pasamos al string
                for atributo in objeto["atributos"]:
                    stringDatos += '&field='
                    stringDatos += atributo["internalName"]
                    tipo = atributo["attrType"]
                    if tipo == 'STRING':
                        stringDatos += ':string(15)'
                    
                stringDatos += '&index=yes'    
                stringNombre = objeto["name"] #Obtenemos el nombre la capa

                #Creamos la capa con el string
                capa = QgsVectorLayer(stringDatos, stringNombre, "memory")

                capa.startEditing() #Iniciamos edicion de la capa

                root = QgsProject.instance().layerTreeRoot() #Obtenemos la raiz para agregar grupos

                QgsProject.instance().addMapLayer(capa, False) #Agregamos la capa en falso para que no se refleje hasta agregarla al grupo

                group = root.findGroup(dependencia) #Buscamos el grupo de la dependencia

                capaReinst = QgsLayerTreeLayer(capa) #La necesitamos para agregar al grupo

                renderer = capa.renderer() #Obtenemos el rendered
                colorRelleno = "#" + objeto["fillColor"] #Obtenemos el color de relleno de la capa
                colorBorde = "#" + objeto["strokeColor"] #Obtenemos el color del borde de la capa
                anchoBorde = str(objeto["strokeWidth"]) #Obtenemos el ancho del bode de la capa

                if capa.wkbType() == 3: #Si la capa es poligono aplicamos el estilo
                    symbol = QgsFillSymbol.createSimple({'color': colorRelleno, 'color_border': colorBorde, 'width_border': anchoBorde})
                    renderer.setSymbol(symbol)
                    capa.triggerRepaint()
                    capa.commitChanges() #Aceptamos los cambios

                if not group is None: #Si el grupo dependencia existe agregamos la capa
                    group.insertChildNode(0, capaReinst)
                else: #Si el grupo dependencia no existe lo creamos y luego agregamos la capa
                    root.insertGroup(0, dependencia)
                    group = root.findGroup(dependencia)
                    group.insertChildNode(0, capaReinst)

                #print QSettings().value("reglasTopologicas", [])
                reglas = QSettings().value("reglasTopologicas") #obtenemos las reglas ya almacenadas en qgis

                #print reglas
                reglasObjeto = objeto["topologias"]
                
                for regla in reglasObjeto:
                    descRegla = regla["reglaTopolia"]
                    capa1 = stringNombre
                    capa2 = regla["capa"]
                    tupla = (descRegla, capa1, capa2)
                    reglas.append(tupla)
                
                QSettings().setValue("reglasTopologicas", reglas)

##########################################################################################################################

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




#################################################################################################################

    def cargarJSON(self):


        stringJson = """ [
    {
    "name": "PRUEBA1",
    "layerType": "WMS",
    "strokeColor": "ABCDEF",
    "strokeWidth": 0.5,
    "fillColor": "FFBF00",
    "atributos": [
        {
        "internalName": "clv",
        "attrType": "STRING"
        }
    ],
    "catDependencia": {
        "nombre": "catastro",
        "municipio": {
        "srid": 32614
        },
        "topologias": [
        {
            "reglaTopolia": "interseccion",
            "capa": "PRUEBA1"
        },
        {
            "reglaTopolia": "inclusion",
            "capa": "PRUEBA2"
        }
        ]
    }
    },
    {
    "name": "PRUEBA2",
    "layerType": "WMS",
    "strokeColor": "A9F5A9",
    "strokeWidth": 0.3,
    "fillColor": "A9F5A9",
    "atributos": [
        {
        "internalName": "clv",
        "attrType": "STRING"
        }
    ],
    "catDependencia": {
        "nombre": "catastro",
        "municipio": {
        "srid": 32614
        },
        "topologias": [
        {
            "reglaTopolia": "interseccion",
            "capa": "PRUEBA2"
        }
        ]
    }
    }

    ] """

        datos = json.loads(stringJson)


        #Leemos los objetos capa del json
        for objeto in datos:

            stringDatos = "" #Los datos de la capa los guardamemos en un string

            #obtenemos el srid
            srid = objeto["catDependencia"]["municipio"]["srid"]

            #cargamos el srid en el string de los datos
            #stringDatos += objeto["layerType"]
            stringDatos += "Polygon"
            stringDatos += '?crs=epsg:'
            stringDatos += str(srid)

            #Obtenemos la dependencia de del objeto capa
            dependencia = objeto["catDependencia"]["nombre"]

            #Obtenemos los atributos de la capa y los pasamos al string
            for atributo in objeto["atributos"]:
                stringDatos += '&field='
                stringDatos += atributo["internalName"]
                tipo = atributo["attrType"]
                if tipo == 'STRING':
                    stringDatos += ':string(15)'
                
            stringDatos += '&index=yes'    
            stringNombre = objeto["name"] #Obtenemos el nombre la capa

            #Creamos la capa con el string
            capa = QgsVectorLayer(stringDatos, stringNombre, "memory")

            capa.startEditing() #Iniciamos edicion de la capa

            root = QgsProject.instance().layerTreeRoot() #Obtenemos la raiz para agregar grupos

            QgsProject.instance().addMapLayer(capa, False) #Agregamos la capa en falso para que no se refleje hasta agregarla al grupo

            group = root.findGroup(dependencia) #Buscamos el grupo de la dependencia

            capaReinst = QgsLayerTreeLayer(capa) #La necesitamos para agregar al grupo

            renderer = capa.renderer() #Obtenemos el rendered
            colorRelleno = "#" + objeto["fillColor"] #Obtenemos el color de relleno de la capa
            colorBorde = "#" + objeto["strokeColor"] #Obtenemos el color del borde de la capa
            anchoBorde = str(objeto["strokeWidth"]) #Obtenemos el ancho del bode de la capa

            if capa.wkbType() == 3: #Si la capa es poligono aplicamos el estilo
                symbol = QgsFillSymbol.createSimple({'color': colorRelleno, 'color_border': colorBorde, 'width_border': anchoBorde})
                renderer.setSymbol(symbol)
                capa.triggerRepaint()
                capa.commitChanges() #Aceptamos los cambios

            if not group is None: #Si el grupo dependencia existe agregamos la capa
                group.insertChildNode(0, capaReinst)
            else: #Si el grupo dependencia no existe lo creamos y luego agregamos la capa
                root.insertGroup(0, dependencia)
                group = root.findGroup(dependencia)
                group.insertChildNode(0, capaReinst)

            #print QSettings().value("reglasTopologicas", [])
            reglas = QSettings().value("reglasTopologicas") #obtenemos las reglas ya almacenadas en qgis

            #print reglas
            reglasObjeto = objeto["catDependencia"]["topologias"]
            
            for regla in reglasObjeto:
                descRegla = regla["reglaTopolia"]
                capa1 = stringNombre
                capa2 = regla["capa"]
                tupla = (descRegla, capa1, capa2)
                reglas.append(tupla)
            
            QSettings().setValue("reglasTopologicas", reglas)








startup = Startup()
startup.mostrarConsola()
startup.cargarCapas()



