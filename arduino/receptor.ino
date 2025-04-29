
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

//Pines CE y CSN
RF24 radio(9, 10);

//Canal de comunicacion coincidente con la del transmisor
const byte address[6] = "00001";

// Estructura que coincide con la del transmisor
struct SensorData {
  float temperature;
  float pressure;
  float humidity;
  float gas_resistance;
  float altitude;
};

void setup() {
  Serial.begin(9600);
  delay(500);

  //Detener el programa si no detecta la antena
  if (!radio.begin()) {while (1);}a
  radio.setPALevel(RF24_PA_LOW);      
  radio.setDataRate(RF24_250KBPS);    
  radio.openReadingPipe(0, address);   
  radio.startListening();                   
}

void loop() {
  //Condición para cuando detecte mensaje
  if (radio.available()) {
    //Recibimos los datos
    SensorData receivedData;
    radio.read(&receivedData, sizeof(receivedData));
    //Mandamos los datos al puerto serie
    Serial.print(receivedData.temperature); //°C
    Serial.print(",");
    Serial.print(receivedData.pressure); //hPa
    Serial.print(",");
    Serial.print(receivedData.humidity); //%
    Serial.print(",");
    Serial.print(receivedData.gas_resistance); //Kohms
    Serial.print(",");
    Serial.print(receivedData.altitude); //m
    Serial.println(";");
  }
  delay(200); 
}

