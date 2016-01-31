#!/usr/bin/env python2.7
import telepot
import pprint
import time
import sys
import os
import json
import requests
import datetime
import ConfigParser

# "Domotibot" e' un bot di telegram che permette la gestione di alcune funzionalita' all'interno
# di una rete domestica. Viene usata la libreria "telepot" per le connessioni alle API di Telegram
#
# Programma di Francesco Tucci 
# Versione 1.02 del 31/01/2016
#
# Il programma e' rilasciato con licenza GPL v.3
#

# genero un timestamp per l'inserimento nel file di log all'inizio di ogni riga
# ritorna il timestamp nel formato dd-mm-aaaa hh:mm:ss
def adesso():
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    return st


# qualche nota sul file di log:
# - il timestamp nel formato dd-mm-aaaa hh:mm:ss messo all'inizio della riga e' generato dalla funzione adesso()
# - dopo il timestamp metto tre caratteri che riguardano il tipo si messaggio
#   0 = [INF] informazione
#   1 = [AVV] avviso
#   2 = [ERR] errore
# cosi' posso filtrare il log alla ricerca di errori senza vedere tutti i messaggi meno gravi
def logga(livello, messaggio):
    # apro il file di log in append
    log = open (ConfigSectionMap("Sistema")['log'], "a")
    
    # inizio mettendo il timestamp
    stringa = adesso()
    
    # aggiungo il livello di gravita'
    if livello == 0:
        stringa = stringa + " [INF]"
    elif livello == 1:
        stringa = stringa + " [AVV]"
    else:
        stringa = stringa + " [ERR]"
        
    # inserisco il messaggio
    stringa = stringa + " " + messaggio
    
    # lo scrivo nel file
    log.write(stringa + "\n")
    
    # chiudo il file di log
    log.close()

# funzione per la memorizzazione di tutti i parametri nel file di configrazione
# per poter accedere al parametro basta usare il comando
# x = ConfigSectionMap("nome_sezione)['nome_parametro']
# ritorna un array con tutti i valori della sezione richiesta
def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                print("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

# leggo il file di configurazione per recuparare tutti i parametri di funzionamento del sistema
# la cosa migliore sarebbe avere questo file in /etc/tvcc.conf per rispettare le convenzioni in linux
# io lo tengo nella cartella dove lavoro per questione di comodita'
Config = ConfigParser.ConfigParser()
Config.read("/home/pi/domotica_tucci/tvcc.conf")

bot = telepot.Bot(ConfigSectionMap("Sistema")['id_bot'])
logga(0, "Connesso a Telegram per invio foto di movimento")

# appena avviato motion genera un falso positivo
# ignoro quindi gli avvisi fatti prima di un minuto
# dall'avvio del sistema
data_avvio = time.ctime(os.path.getmtime(ConfigSectionMap("Sistema")['log_file_accensione']))
data_avvio = time.strptime(data_avvio, '%a %b %d %H:%M:%S %Y')
data_adesso = datetime.datetime.now()
data_adesso = time.strptime(str(data_adesso), '%Y-%m-%d %H:%M:%S.%f')

tempo_da_avvio = (time.mktime(data_adesso) - time.mktime(data_avvio)) / 60

if tempo_da_avvio > float(ConfigSectionMap("Sistema")['tempo_ingaggio']):
    # controllo l'esistenza di due argomenti nel lancio del file py
    if len(sys.argv) >=2:
        path_image = sys.argv[1]
        foto = open(path_image, 'rb')
        bot.sendPhoto(ConfigSectionMap("Sistema")['id_chat'], foto)
        logga(1, "Inviata la foto del moimento rilevato")
else:
    logga(1, "Foto generata, ma utenti non avvisati perche' nel periodo di grace")

    
