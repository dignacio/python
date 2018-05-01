import pytz
from datetime import datetime
# la libreria JWT no se encuentra cargada
# se ejecuta el siguiente comando en la consola (cmd) para instalarla
# python -m pip install PyJWT
import jwt
from PyQt5.QtCore import QSettings


class Autenticacion:
    
    def autentication(self):
       
        try:
            encoded = QSettings().value("token")
        except: 
            raise ValueError("No existe el token") 

        if encoded == "None":
            raise ValueError('No existe el token')
            return 
        

        try:
            utc=pytz.UTC
            decoded = jwt.decode(encoded, verify=False)
            timestamp = decoded['exp']
            date = datetime.fromtimestamp(timestamp, utc)
            present = datetime.now()
            present = utc.localize(present)
        except:
            raise ValueError('Problemas al validar el token')

        if present < date:
           
            return True
        else:
          
            return False
    


