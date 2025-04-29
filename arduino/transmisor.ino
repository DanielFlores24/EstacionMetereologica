///ara este proyecto use un ESP32-C3 mini
#include <Wire.h>
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
#include <Adafruit_Sensor.h>
#include "Adafruit_BME680.h"

#define SEALEVELPRESSURE_HPA (1013.25)

//Pines del NRF24L01
#define CE_PIN 3
#define CSN_PIN 10
#define SCK_PIN 6
#define MOSI_PIN 7
#define MISO_PIN 2

RF24 radio(CE_PIN, CSN_PIN); 

//Canal de comunicacion
const byte address[6] = "00001";

//Instanciamos el sensor
Adafruit_BME680 bme;

//La estructura de datos que vamos a mandar
struct SensorData {
  float temperature;
  float pressure;
  float humidity;
  float gas_resistance;
  float altitude;
};

void setup() {
  Serial.begin(115200);
  SPI.begin(SCK_PIN, MISO_PIN, MOSI_PIN);
  //Condiciones de inicializacion
  if (!bme.begin()) {
    Serial.println("No se encontró el sensor BME680!");
    while (1);
  }
  if (!radio.begin()) {
    Serial.println(" NRF24L01 no conectado");
    while (1);
  }
  
  //Datos de inicializaacion del bme688
  bme.setTemperatureOversampling(BME680_OS_8X);
  bme.setHumidityOversampling(BME680_OS_2X);
  bme.setPressureOversampling(BME680_OS_4X);
  bme.setIIRFilterSize(BME680_FILTER_SIZE_3);
  bme.setGasHeater(320, 150);
  //Datos de inicializaacion del NRF24L01
  radio.begin();
  radio.setPALevel(RF24_PA_LOW);
  radio.setDataRate(RF24_250KBPS);
  radio.openWritingPipe(address);
  radio.stopListening(); 

 
}

void loop() {
  //Condicion por si no se puede abrir el bme688
  if (!bme.performReading()) {
    Serial.println("Fallo al leer sensor.");
    delay(1000);
    return;
  }
  //Guardamos y mandamos los datos
  SensorData data;
  data.temperature = bme.temperature;  //°C
  data.pressure = bme.pressure / 100.0; //hPa
  data.humidity = bme.humidity;//%
  data.gas_resistance = bme.gas_resistance / 1000.0;//Kohms
  data.altitude = bme.readAltitude(SEALEVELPRESSURE_HPA);//m
  radio.write(&data, sizeof(data));


  //Imprimimos los datos serialmente
  Serial.println(data.temperature);  //°C
  Serial.println(data.pressure);  //hPa
  Serial.println(data.humidity); //%
  Serial.println(data.gas_resistance); //Kohms
  Serial.println(data.altitude);//m
  Serial.println("Datos enviados");
  delay(2000);
}