/*
  Controllore di consumo elettrico istantaneo
  By Francesco Tucci
  
  Tratto del progetto di Mirco Piccin aka pitusso
  http://playground.arduino.cc/italiano/emoncms
  tratto a sua volta da
  http://arduino.cc/en/Tutorial/WebClientRepeating
  
  Il sistema visualizza su un display TFT il consumo istantaneo della corrente che passa attraverso un filo 
  della 220V, con la scheda YUN (o WiFi) registra le letture sulla centralina di controllo
  
  Materiale:
  - Arduino YUN
  - Display TFT
  - Pinza Amperometrica CT013
  
*/

// Include la libreria per la lettura dell pinza amoerometrica
#include "EmonLib.h"

// include le librerie per la gestione del display TFT
#include <SPI.h>
#include <TFT.h>

// Libreria per creare richieste http e memorizzare i dati sul server
#include <HttpClient.h>

// Libreria per comunicare con la parte Linux dello YUN (indispensabile per accedere al WiFi)
#include <Bridge.h>


// imposta i pin di collegamente del display ad Arduino
// Il display TFT va collegato ad Arduino Yun come nella pagina
// relativa alle informazioni sul display, ma i pin 0 e 1 vanno
// sostituiti con 2 e 3
// Attenzione che se si usa Arduino Uno i pin sono diversi e anche 
// i collehamento devono essere modificati
#define cs   7
#define dc   2
#define rst  3

// inizializza l'oggetto del display TFT
TFT screen = TFT(cs, dc, rst);

// parametri di calibrazione per la pinza amperometrica
// la calibrazione va fatta a mano con l'aiuto di qualche strumento
// più preciso. Per me il '29' va bene.
const int volt = 220;
const float ct_calibration = 29;

// Pin analogico per la lttura del valore dalla pinza amperometrica
const int currentSensorPin = A2;

// variabili necessarie per il sistema
float Irms = 0;
float lettura; // contatore per le letture del sensore
char suSchermo[8]; // stringa del consumo da scrivere a display
String stringaGet; // stringa della chiamata GET http per memorizzare i valori
int cicliGet = 0; // contatore delle letture prima di scrivere sul DB
long sommaPerMedia = 0; // la lettura scritta sul DB è la media di 50 letture

// Oggetto per la lttura della corrente
EnergyMonitor emon1;                   

void setup() {
  // queste prime righe servono per far avviare correttamente il sistema Linux
  // se non si fa così, tre volte su 4 il boot non avviene
  delay(2500);
  do {
     while (Serial1.available() > 0) {
        Serial1.read();
        }
    delay(1000);
  } while (Serial1.available()>0);
  
  // adesso Linux dovrebbe essere avviato
  
  // avvia la porta seriale (per debug)
  Serial.begin(9600);

  // inizializza il lettore di corrente
  emon1.current(currentSensorPin, ct_calibration);

  // inizializza lo schermo
  screen.begin();

  screen.background(0,0,0); // sfondo nero
  screen.stroke(255,255,255); //testo bianco
  screen.setTextSize(2); // dimensione carattere
  screen.text("Inizializzo...\n ",0,0);
  screen.text("Bridge... ",0,20); 
  screen.text("...attendi...",0,40);
  
  // il bridge è lento ad avviarsi, quindi quando è avviato
  // accendo il LED 13 (già presente sulla scheda) per notificarlo
  // senza bridge non c'è la possibilità di accedere alla WiFi dallo sketch
  pinMode(13, OUTPUT);
  digitalWrite(13, LOW);
  Bridge.begin();
  digitalWrite(13, HIGH);

  screen.text("Bridge Pronto!\n ",0,60); //
  delay(3000);

  // sfondo nero (cancello quello che c'è scritto sul display)
  screen.background(0,0,0);
}

void loop() {
  
    // fa 10 letture consecutive della corrente e poi ne fa la media
    lettura = 0;
    for (int c = 0; c<10; c++)
      { 
        lettura = lettura + (emon1.calcIrms(1480));
      }
    Irms = lettura / 10;
    
    // debug, visualizza vie seriale i dati letti
    Serial.print("W : ");
    Serial.print(Irms*volt);
    Serial.print(" - A : ");
    Serial.println(Irms);
    
    // imposta il colore con cui colorare lo sfondo
    // sfondo neto e testo bianco se inferiore a 2000
    // sfondo giallo e testo nero 2000 e 3000
    // sfondo rosso e testo nero se superiore a 3000
    if (int(Irms*volt) <= 2000) {
      screen.background(0,0,0);
      screen.stroke(255,255,255);
    }
    else if ((int(Irms*volt) > 2000) and (int(Irms*volt) <= 3000)) {
      screen.background(255,255,0);
      screen.stroke(0,0,0);
    }
    else {
      screen.background(255,0,0);
      screen.stroke(0,0,0);
    }
    
    // scrive su schermo il valore intero della lettura
    String(int(Irms*volt)).toCharArray(suSchermo, 8);
    screen.setTextSize(2);
    screen.text("Consumo (W)\n ",10,5);
    screen.setTextSize(6);
    screen.text(suSchermo, 10, 45);

    // incrementa la somma delle letture per poi ferne la media
    sommaPerMedia = sommaPerMedia + int(Irms*volt);

    // se ho fatto 50 aggiornamenti è ora di scrivere il dato sul DB
    if (cicliGet == 50)
    { 
      // inizializzo la sessione http
      HttpClient client;
      
      // genero la stringa get da passare al server web
      // IP e porta sono da inserire a seconda delle configurazioni di rete attuali
      // è l'indirizzo del server web, non della scheda Arduino Yun
      stringaGet = "http://192.168.1.1:8888/?tab=corr&a=1&w="; 
      stringaGet += int(sommaPerMedia/50);
      stringaGet += " HTTP/1.1\r\n";
      
      Serial.print(stringaGet); // print seriale per debug
      
      client.get(stringaGet); // faccio la chiamata http
      
      cicliGet = 0;
      sommaPerMedia = 0;
    }
    else
    {
      cicliGet = cicliGet + 1;
    }
}
