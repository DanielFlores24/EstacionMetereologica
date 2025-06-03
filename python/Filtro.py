import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

class FiltroKalmanExtendido:
    def __init__(self, estado_inicial, covarianza_inicial, ruido_proceso, ruido_medicion):
        self.estado = estado_inicial
        self.covarianza = covarianza_inicial
        self.Q = ruido_proceso
        self.R = ruido_medicion
        self.historial_estados = []
    
    def predecir(self):
        self.covarianza += self.Q
        return self.estado
    
    def actualizar(self, medicion):
        y = medicion - self.estado
        S = self.covarianza + self.R
        K = self.covarianza / S
        self.estado += K * y
        self.covarianza = (1 - K) * self.covarianza
        self.historial_estados.append(self.estado)
        return self.estado

def graficar_resultados(original, filtrado, titulo, unidad):
    plt.figure(figsize=(12, 6))
    plt.plot(original, 'b-', alpha=0.3, label='Original')
    plt.plot(filtrado, 'r-', linewidth=1.5, label='Filtrado')
    plt.title(titulo)
    plt.xlabel('Muestras')
    plt.ylabel(unidad)
    plt.legend()
    plt.grid(True)
    plt.show()

#Leemos el archivo CSV
datos = pd.read_csv("datos_bme688.csv")
datos.columns = ['temperatura', 'presión', 'humedad', 'gas resistance', 'altitud']

#Unidades para la grafica
unidades = {
    'temperatura': '°C',
    'presion': 'hPa',
    'humedad': '%',
    'gas_resistance': 'KOhm',
    'altitud': 'm'
}

#Parametros del filtro
parametros = {
    'temperatura': {'Q': 1, 'R': 1},
    'presion': {'Q': 1, 'R': 1},
    'humedad': {'Q': 4, 'R': 9},
    'gas_resistance': {'Q': 100, 'R': 1000},
    'altitud': {'Q': 25, 'R': 1}
}

#Procesamiento de las variables
resultados = {}
for columna in datos.columns:
    print(f"\nProcesando: {columna}")
    
    # Inicialización
    ekf = FiltroKalmanExtendido(
        estado_inicial=datos[columna].iloc[0],
        covarianza_inicial=1,
        ruido_proceso=parametros[columna]['Q'],
        ruido_medicion=parametros[columna]['R']
    )
    
    #Aplicacion del filtro
    datos_filtrados = [datos[columna].iloc[0]]
    for valor in tqdm(datos[columna].iloc[1:], desc=f"Filtrando {columna}"):
        ekf.predecir()
        datos_filtrados.append(ekf.actualizar(valor))
    
    resultados[columna] = {
        'original': datos[columna].values,
        'filtrado': np.array(datos_filtrados),
        'unidad': unidades[columna]
    }

#Graficas
plt.figure(figsize=(15, 10))
for i, columna in enumerate(resultados.keys(), 1):
    plt.subplot(3, 2, i)
    plt.plot(resultados[columna]['original'], 'b-', alpha=0.3)
    plt.plot(resultados[columna]['filtrado'], 'r-', linewidth=1)
    plt.title(columna)
    plt.ylabel(unidades[columna])
    plt.grid(True)
plt.tight_layout()
plt.show()