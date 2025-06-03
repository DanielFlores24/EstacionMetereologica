import serial
import numpy as np

n = 1050
mediciones = np.zeros((n, 5))
indice = 0  

# Funcion para procesar los datos del Arduino
def procesar_linea(linea):
    if ';' not in linea:
        return None
    linea = linea.replace(';', '')
    partes = linea.split(',')

    try:
        valores = [float(p) for p in partes]
    except ValueError:
        return None

    return valores 

#Conexion con Arduino
try:
    arduino = serial.Serial('COM9', 9600, timeout=1)
    print("Conectado al Arduino. Guardando datos en matriz...")

    while indice < n:
        if arduino.in_waiting > 0:
            try:
                linea = arduino.readline().decode('utf-8').strip()
                valores = procesar_linea(linea)
                if valores and len(valores) == 5:
                    #Insertamos los datos como columna en la matriz
                    mediciones[indice, :] = valores
                    print(f"Datos guardados en fila {indice}: {valores}")
                    indice += 1
            except Exception as e:
                print(f"Error al leer o guardar datos: {e}")

except serial.SerialException:
    print("No se pudo abrir el puerto serial")
except KeyboardInterrupt:
    print("Lectura interrumpida por el usuario")
finally:
    if 'arduino' in locals() and arduino.is_open:
        arduino.close()
    print("Conexión cerrada")

#Guardamos los datos
np.savetxt("datos_bme688.csv", mediciones, delimiter=",", comments='', fmt="%.3f")
print("Archivo guardado")