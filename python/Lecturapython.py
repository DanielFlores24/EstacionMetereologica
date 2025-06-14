#Librerias
import serial
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import time
import numpy as np

#Configuracion de InfluxDB
INFLUX_CONFIG = {
    "url": "http://localhost:8086",
    "token": "daniel-super-token",
    "org": "Daniel",
    "bucket": "DanielBucket"
}

#Filtro de Kalman
class KalmanFilter:
    def __init__(self, Q=1, R=1):
        self.Q = Q          
        self.R = R          
        self.x = None       
        self.P = 1         
    
    def update(self, z):
        if self.x is None:
            self.x = z
            return z
            
        self.P += self.Q
        K = self.P / (self.P + self.R)  
        self.x += K * (z - self.x)      
        self.P *= (1 - K)               
        return self.x

#Configuración de los filtros para cada variable del BME688
filtros = {
    'temperatura': KalmanFilter(Q=1, R=1),   
    'presion': KalmanFilter(Q=1, R=1),        
    'humedad': KalmanFilter(Q=4, R=9.0),        
    'gas_resistance': KalmanFilter(Q=0.1, R=1), 
    'altitud': KalmanFilter(Q=25, R=1)         
}

#Cliente InfluxDB
cliente = InfluxDBClient(
    url=INFLUX_CONFIG["url"],
    token=INFLUX_CONFIG["token"],
    org=INFLUX_CONFIG["org"]
)
#Uso de la API
P2I = cliente.write_api(write_options=SYNCHRONOUS)

#Funcion para procesar los datos del arduino en formato de InfluxDB
def procesar_linea(linea):
    if ';' not in linea: #Regresamos None si no hay un ;
        return None
    
    #Quitamos los ; y separamos por ,
    linea = linea.replace(';', '')
    partes = linea.split(',')
    
    #Guardamos los valores en una lista
    try:
        valores = [float(p) for p in partes]
    except ValueError:
        return None
    
    #Retornamos los valores de la lista en forma de diccionario
    return {
        'temperatura': valores[0],
        'presion': valores[1],
        'humedad': valores[2],
        'gas_resistance': valores[3],
        'altitud': valores[4],
        'timestamp': int(time.time()) 
    }

#Funcion para pasar los datos a influx en su formato (MODIFICADA para enviar ambos)
def enviar_a_influx(data, data_filtrado):
    #Creamos un punto de datos crudos, con los valores por cada campo y un tiempo
    point_crudo = Point("bme688") \
        .field("temperatura", data["temperatura"]) \
        .field("presion", data["presion"]) \
        .field("humedad", data["humedad"]) \
        .field("gas_resistance", data["gas_resistance"]) \
        .field("altitud", data["altitud"]) \
        .time(data["timestamp"], write_precision='s')
    
    #Creamos un punto de datos filtrados (usando Kalman)
    point_filtrado = Point("bme688_filtrado") \
        .field("temperaturaF", data_filtrado["temperatura"]) \
        .field("presionF", data_filtrado["presion"]) \
        .field("humedadF", data_filtrado["humedad"]) \
        .field("gas_resistanceF", data_filtrado["gas_resistance"]) \
        .field("altitudF", data_filtrado["altitud"]) \
        .time(data["timestamp"], write_precision='s')
    
    #Intentamos pasar los valores al bucket personalizado
    try:
        P2I.write(bucket=INFLUX_CONFIG["bucket"], record=point_crudo)
        P2I.write(bucket=INFLUX_CONFIG["bucket"], record=point_filtrado)
        print(f"Datos enviados a InfluxDB - Crudos: {data}")
        print(f"Datos enviados a InfluxDB - Filtrados: {data_filtrado}")
    except Exception as e:
        print(f"Error al enviar a InfluxDB: {e}")

#Aqui empieza la parte que se va a ir ejecutando 
try:
    #Conectamos con el arduino
    arduino = serial.Serial('COM9', 9600, timeout=1)
    print("Conectado al Arduino. Enviando datos a InfluxDB...")
    
    #Bucle principal de lectura
    while True: 
        if arduino.in_waiting > 0:
            #Vemos si se puede abrir el monitor serie
            try:
                #Procesamos los datos y los guardamos
                datos = procesar_linea(arduino.readline().decode('utf-8').strip())
                
                #Verificamos los datos
                if datos:
                    # Aplicamos el filtro
                    datos_filtrado = {
                        'temperatura': filtros['temperatura'].update(datos['temperatura']),
                        'presion': filtros['presion'].update(datos['presion']),
                        'humedad': filtros['humedad'].update(datos['humedad']),
                        'gas_resistance': filtros['gas_resistance'].update(datos['gas_resistance']),
                        'altitud': filtros['altitud'].update(datos['altitud']),
                        'timestamp': datos['timestamp']
                    }
                    enviar_a_influx(datos, datos_filtrado)
            except serial.SerialException:
                print("Error en la comunicación serial")
                break
            except Exception as e:
                print(f"Error inesperado: {e}")

#Excepciones del puerto o que sea interrumpido
except serial.SerialException:
    print(f"No se pudo abrir el puerto")
except KeyboardInterrupt:
    print("Programa terminado manualmente")
#Parte final por si se termina el loop
finally:
    if 'arduino' in locals() and arduino.is_open:
        arduino.close()
    cliente.close()