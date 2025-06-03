Este proyecto mide variables como temperatura, humedad, presión atmosférica, resistencia de gas y altitud usando el sensor BME688.
Los datos son enviados mediante comunicación entre dos microcontroladores Arduino, luego procesados con un script en Python y almacenados en InfluxDB. 
Finalmente, son visualizados en Grafana.

InfluxDB UI: http://localhost:8086
-  Usuario: daniel
-  Contraseña: danielpassword

Grafana: http://localhost:3000
-  Usuario: admin
-  Contraseña: admin

Flujo de los datos
```mermaid
graph LR
    A[Sensor en ESPP32-C3 mini] -->|Transmite vía RF/NRF24L01| B[Arduino nano Receptor]
    B -->|Envía datos por Serial| C[Python: Lectura Serial]
    C -->|Procesa y envía| D[InfluxDB vía API HTTP]
    D -->|Almacenamiento| E[Grafana: Visualización]
```

Diagrama en grafana
![Diagrama de flujo de Grafana](diagrama_grafana.png)

Este proyecto cuenta tambien con un filtro de kalman, si bien los datos no siguien distribuciones normales decidimos meterlo.
En total hicimos 1050 mediciones estaticas con el sensor para ver el comportamiento de los datos:
Distribucion de la temperatura
![Distribucion temperatura](Temperatura.png)
Distribucion de la presión
![Distribucion presión](Presion.png)
Distribucion de la humedad
![Distribucion humedad](Humedad.png)
Distribucion de la resistencia de los gases
![Distribucion gas resistance](Gas_Resistance.png)
Distribucion de la altitud
![Distribucion altitud](Altitud.png)