#!/usr/bin/python
import telepot
import pprint
import time
import sys
import os
import json
import requests
import ConfigParser
import datetime
import traceback


# "Domotibot" e' un bot di telegram che permette la gestione di alcune funzionalita' all'interno
# di una rete domestica. Viene usata la libreria "telepot" per le connessioni alle API di Telegram
#
# Programma di Francesco Tucci 
# Versione 1.01 del 27/01/2016
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

# scrivo un file di semaforo con data e ora di accensione, per evitare la falsa rilevazione
# tutte le volte che il sistema si accende
def scrivi_semaforo():
    quando_acceso = open (ConfigSectionMap("Sistema")['log_file_accensione'], "w")
    quando_acceso.write("adesso")
    quando_acceso.close

# per verificare se il processo di motion e' attivo
# ritorna il numero di occorrenze del processo "motion" attive nel sistema
# (attenzione, se si sta lavorando con il file di configurazione di motion aperto il conteggio e' falsato)
def verifica_motion():
    processname = 'motion'
    tmp = os.popen("ps -Af").read()
    proccount = tmp.count(processname)
    return proccount


# cosa fare quando si riceve un messaggio
def handle(msg):
    # questi sono i dati del messaggio in arrivo
    id_utente = msg['from']['id'] # id utente per rispondere male a chi non e' ablitato
    nome_utente = msg['from']['first_name'] # nome utente per rispondere con gentilezza ai comandi
    cognome_utente = msg['from']['last_name'] # cognome dell'utente che ha inviato il messaggio
    id_chat = msg['chat']['id'] # id della chat a cui rispondere
    testo = msg['text'].lower() # testo dei messaggi ricevuti, convertito tutto in minuscole per facilitare il lavoro con il parse
    
    # debug, per verificare cosa e' effettivamente arrivato al bot
    logga(0, "L'utente " + nome_utente + " (" +str(id_utente) + ") ha scritto <<" + testo + ">> nella chat " + str(id_chat))
    
    # comando per reimpostare la tastiera standard e quello per creare la tastiera personalizzata
    hide_keyboard = {'hide_keyboard': True}
    show_keyboard = {'keyboard': [['TVcc ON','TVcc OFF', 'TVcc?', 'Now'],['DLNA agg', 'DLNA HD', 'DLNA dwn']]}
    
    # controllo che i comandi arrivino dagli utenti abilitati
    if id_utente != int(ConfigSectionMap("Sistema")['utente_1']) and id_utente != int(ConfigSectionMap("Sistema")['utente_2']):
        bot.sendMessage(id_utente, "Spiacente, bot non attivo")
        
        #mando un messaggio all'amministratore del sistema per informare che un altro utete ha provato a scrivere
        messaggio = "Attenzione l'utente " + nome_utente + " " + cognome_utente + " (id " + str(id_utente) + ") ha scritto questo: <<" + testo + ">>"
        bot.sendMessage(ConfigSectionMap("Sistema")['utente_1'], messaggio)
        logga(1, "Messaggio da utente non autorizzato!")
    else:
        # questo e' il comando per iniziare ad interagire
        if testo == "/ciao" or testo == "/ciao@domotuccibot":
            messaggio = "Ciao " + nome_utente + ", cosa posso fare per te?"
            # alla risposta aggiunge la tastiera personalizzata
            bot.sendMessage(id_chat, messaggio, reply_markup=show_keyboard)

        # *******
        # voglio accendere il sistema di videosorveglianza
        # *******
        elif testo == "tvcc on":
            logga(0, "Accendo motion come da richiesta")
            # controllo se il processo 'motion' e' attivo o no
            motion_on = verifica_motion()        
            
            # se il processo 'motion' non e' attivo lo avvio e avviso che e' attivato
            if motion_on == 0:
                # attivo il processo
                os.system("/home/pi/motion-mmal/motion")
                
                scrivi_semaforo()  
                
                # gli lascio il tempo di attivarsi
                time.sleep(5)
                
                # controllo se e' in esecuzione
                motion_on = verifica_motion()   
                if motion_on == 0:
                    messaggio = "Sistema TVcc NON attivato, potrebbe esserci un problema"
                    bot.sendMessage(id_chat, messaggio, reply_markup=hide_keyboard)
                    logga(2, "Motion non si e' avviato")
                else:           
                    messaggio = "Sistema TVcc attivato con successo!"
                    bot.sendMessage(id_chat, messaggio, reply_markup=hide_keyboard)
                    logga(0, "Motion regolarmente attivo")
            
            # se il processo era gia' attivo, avviso che non ho fatto nulla
            else:
                messaggio = "Il Sistema TVcc era gia' attivo, non ho fatto nulla."
                bot.sendMessage(id_chat, messaggio, reply_markup=hide_keyboard)
                logga(1, "Motion non attivato, era gia' attivo")
            

        
        # *******
        # voglio spegnere il sistema di videosorveglianza
        # *******
        elif testo == 'tvcc off':
            logga(0, "Spengo motion come richiesto")
            
            # controllo se il processo 'motion' e' attivo o no
            motion_on = verifica_motion() 

            # se il processo 'motion' e' attivo lo uccido e avviso che e' disattivato
            if motion_on != 0:
                os.system("pkill motion")
                time.sleep(5)
                motion_on = verifica_motion() 
                # se il processo 'motion' non e' attivo va bene, e' ammazzato davvero
                if motion_on == 0:
                    messaggio = "Confermo che il sistema TVcc e' stato disattivato"
                    bot.sendMessage(id_chat, messaggio, reply_markup=hide_keyboard)
                    logga(0, "Motion disattivato")
                else:
                    messaggio = "Non sono riuscito a spegnere il sistema TVcc!"
                    bot.sendMessage(id_chat, messaggio, reply_markup=hide_keyboard)
                    logga(3, "Motion ancora attivo, ci sono " + str(motion_on) + " processi attivi")
            else:
                messaggio = "Il sistema TVcc era gia' disattivato, non ho fatto niente."
                bot.sendMessage(id_chat, messaggio, reply_markup=hide_keyboard)
                logga (0, "Motion gia' spento, nessun intervento")

        # *******
        # voglio sapere lo stato del sisterma di videosorveglianza
        # *******
        elif testo == 'tvcc?':
            # controllo se il processo 'motion' e' attivo o no
            motion_on = verifica_motion()
            logga(0, "Verifica dello stato di motion")
            
            if motion_on == 0:
                messaggio = "Il sistema TVcc e' DISATTIVATO"
                bot.sendMessage(id_chat, messaggio, reply_markup=hide_keyboard)
                logga(0, "motion spento")
            else:
                messaggio = "Il sistema TVcc e' ATTIVO"
                bot.sendMessage(id_chat, messaggio, reply_markup=hide_keyboard)
                logga(0, "motion acceso")

        # *******
        # voglio fare un foto dell'area (solo se il sistema non e' attivo)
        # *******
        elif testo == 'now':
            # controllo se il processo 'motion' e' attivo o no
            motion_on = verifica_motion()

            # se il processo 'motion' e' attivo non posso fare la foto
            if motion_on != 0:
                messaggio = "Posso fare la foto solo con il sistema TVcc non attivo, se ti serve farla adesso devi prima disattivarlo"
                bot.sendMessage(id_chat, messaggio, reply_markup=hide_keyboard)
                logga(1, "Richiesta foto istantanea non ammissibile con motion attivo")
            else:
                os.system("raspistill -w 1600 -h 1200 -ex verylong -t 1 -o /home/pi/Pictures/SingoloClick.jpg")
                path_image = '/home/pi/Pictures/SingoloClick.jpg'
                foto = open(path_image, 'rb')
                messaggio = "Ecco la foto che mi hai chiesto"
                bot.sendMessage(id_chat, messaggio, reply_markup=hide_keyboard)                
                bot.sendPhoto(id_chat, foto)
                os.system("rm /home/pi/Pictures/SingoloClick.jpg")
                logga(0, "Scattata la foto istantanea")
            
        else:
            messaggio = "Ciao " + nome_utente + ", per interagire con me scrivi '/ciao' e segui le istruzioni"
            bot.sendMessage(id_chat, messaggio, reply_markup=hide_keyboard)
            loggo(1, "Messaggio non riconosciuto")


# qui inizia il codice principale (non c'e' il 'main' in python)
# che viene eseguto solo all'avvio del sistema

# leggo il file di configurazione per recuparare tutti i parametri di funzionamento del sistema
# la cosa migliore sarebbe avere questo file in /etc/tvcc.conf per rispettare le convenzioni in linux
# io lo tengo nella cartella dove lavoro per questione di comodita'
Config = ConfigParser.ConfigParser()
Config.read("/home/pi/domotica_tucci/tvcc.conf")

# registro l'avvio del sistema
logga(0, "Sistema avviato")

# all'avvio del sistema notifico la cosa al gruppo, ma prima devo verificare
# che la connessione ad Internet sia operativa

# cerco di ottenere l'IP pubblico
# aggiunta la gestione delle eccezioni per l'avvio se la rete manca (27-01-2016)
connesso = False
while connesso == False:
    try:
        req = requests.get("http://httpbin.org/ip")
        connesso = True
        logga(0, "Internet c'e")
    except Exception, err:
        logga(3, "Manca Internet " + str(traceback.format_exc()))
        time.sleep(30)

# ci provo fino a che la richiesta non mi da' messaggio http200
while req.status_code != 200:
    time.sleep(30)
    req = requests.get("http://httpbin.org/ip")
    logga(2, "http status code: " + str(req.status_code))

# se la richiesta e' http 200, vuol dire che e' buona, quindi procedo
if req.status_code == 200:
	# change the HTTP response body into a JSON type
        text = json.loads(req.text)
        # retreive value by key using dict
        ip = text['origin']
        logga(0, "IP pubblico: " + ip)

# ottengo l'IP della lan e della wlan
indirizzo_eth0 = os.popen("/sbin/ifconfig eth0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}'").read()
indirizzo_eth0 = indirizzo_eth0.replace('\n', '')
#indirizzo_wlan0 = os.popen("/sbin/ifconfig wlan00 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}'").read()
logga (0, "IP di LAN: " + indirizzo_eth0)

# creo il bot e mi collego a Telegram usando la mia chiave univoca
# che mi e' stata comunicata da The Botfather (si deve rispettare la famiglia)
# aggiunta la gestione delle eccezioni per capire che fare quando manca connessione o i server Telegram sono giu' (27/01/2016)
connessione_telegram = False
while connessione_telegram == False:
    try:
        bot = telepot.Bot(ConfigSectionMap("Sistema")['id_bot'])
        utente =  bot.getMe()
        logga(0, "Connessione a Telegram avvenuta! ID utente del bot: " + str(utente['id']))
        connessione_telegram = True
    except Exception, err:
        logga(3, "Connessione a Telegram fallita o caduta")
        logga(3, traceback.format_exc())
        time.sleep(30)

# mando i messaggi informativi alla chat
messaggio = "Ciao, sono stato appena riavviato, per sicurezza adesso avvio la videosorveglianza e ti mostro alcune informazioni\n"
messaggio = messaggio + "IP pubblico del tuo sistema: " + ip + "\n"
messaggio = messaggio + "IP di LAN: " + indirizzo_eth0
bot.sendMessage(ConfigSectionMap("Sistema")['id_chat'], messaggio)

# a questo punto avvio Motion solo se non e' indicato il parametro 'off' nella riga di comando
if len(sys.argv) >=2:
    if sys.argv[1] == 'off':
        messaggio = "Mi hai chiesto di non avviare la TVcc, quindi non l'ho fatto"
        bot.sendMessage(ConfigSectionMap("Sistema")['id_chat'], messaggio)
        logga(0, "motion non attivato per switch OFF a riga di comando")
else:          
    os.system("/home/pi/motion-mmal/motion")
    logga(0, "Comando avvio motion al boot del sistema")
    
    scrivi_semaforo()

    # gli do il tempo di avviarsi
    time.sleep(5)

    # controllo se il processo 'motion' si e' attivato
    motion_on = verifica_motion()
    # se non si e' attivato lo segnalo
    if motion_on == 0:
        messaggio = "ATTENZIONE, il sistema TVcc non ha risposto al comando di attivazione!"
        bot.sendMessage(ConfigSectionMap("Sistema")['id_chat'], messaggio)
        logga(2, "Motion non e' partito")
    # se invece si e' attivato lo notifico
    else:
        messaggio = "Confermo che il sistema TVcc e' adesso attivo"
        bot.sendMessage(ConfigSectionMap("Sistema")['id_chat'], messaggio)
        logga(0, "Motion e' partito al boot del sistema")

# controllo comandi in arrivo
bot.notifyOnMessage(handle)

while 1:
    time.sleep(10)
