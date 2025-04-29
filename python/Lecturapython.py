#Librerias
import serial
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import time

#Configuracion de InfluxDB
INFLUX_CONFIG = {
    "url": "http://localhost:8086",
    "token": "daniel-super-token",
    "org": "Daniel",
    "bucket": "DanielBucket"
}


#Cliente InfluxDB
cliente = InfluxDBClient(
    url=INFLUX_CONFIG["url"],
    token=INFLUX_CONFIG["token"],
    org=INFLUX_CONFIG["org"]
)
#Uso de la API
P2I = cliente.write_api(write_options=SYNCHRONOUS)

#Funcion ara rocesar los datos del arduino en formato de InfluxDB
def procesar_linea(linea):
    if ';' not in linea: #Reegresamos None si no hay un ;
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


#Funcion para pasar los datos a influx en su formato
def enviar_a_influx(data):
    #Creamos un punto de datos, con los valores ppor cada campo y un tiempo
    point = Point("bme688") \
        .field("temperatura", data["temperatura"]) \
        .field("presion", data["presion"]) \
        .field("humedad", data["humedad"]) \
        .field("gas_resistance", data["gas_resistance"]) \
        .field("altitud", data["altitud"]) \
        .time(data["timestamp"], write_precision='s')
    
    #Intentamos pasar los valores all bucket personalizado
    try:
        P2I.write(bucket=INFLUX_CONFIG["bucket"], record=point)
        print(f"Datos enviados a InfluxDB: {data}")
    except Exception as e:
        print(f"Error al enviar a InfluxDB: {e}")


#Aqui empieza la parte que se va a ir ejecutando 
try:
    #Conectamos con el arduino
    arduino = serial.Serial('COM9', 9600, timeout=1)
    print("Conectado al Arduino. Enviando datos a InfluxDB...")
    
    #Bucle
    while True:
        if arduino.in_waiting > 0:
            #Vemos si se puede abrir ell monitor serie
            try:
                #Procesamos los datos y los guardamos
                datos = procesar_linea(arduino.readline().decode('utf-8').strip())
                #Verificamos que los datos fueran "correctos"
                if datos:
                    enviar_a_influx(datos)
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