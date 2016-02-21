# Un bot in grado di gestire dei sensori in casa
Telegram è un'ottima piattaforma per creare bot che possano interagire con i messaggi di domando inviati tramite il proprio dispositivo portatile.
Ho creato questo piccolo sistema per controllare l'impianto di videosorveglianza in casa (lo accendo, lo spengo, lo interrogo sullo stato e mi faccio mandare un avviso e le foto quando capita che viene rilevato un movimento.
L'applicazione è in Python, usa le librerie [telepot](https://github.com/nickoala/telepot) per interagire con le [API di Telegram](https://core.telegram.org/) e il programma [motion](http://www.lavrsen.dk/foswiki/bin/view/Motion/WebHome) per rilevare il movimento, usando la videocamera IR presente sul Raspberry Pi

Il programma _tvcc.py_ va avviato al boot del sistema, in modo che il bot sia pronto (per motivi di sicurezza, al riavvio del raspberry la videosorveglianza viene attivata in automatico)
Il programma _invia_foto.py_ va inserito nel file di configurazione di motion alla riga _on_picture_save_ (invia una foto ogni volta che questa viene salvata su disco, il problema è la lentezza dovuta al fatto che ogni volta deve aprire una connessione con Telegram)
Il programma _avvisa_movimento.py_ va inserito nel file di configurazione di motion alla riga _on_event_start_ (avvisa che un evento di rilevazione di movimento è iniziato)
E' necessario ricordarsi di mettere la calncellazione della cartelle delle foto alla riga _on_event_end_ altrimenti il disco si potrebbe riempire rapidamente

## Changelog

### Versione 1.03 del 21/02/2016
Il sistema non rispondeva quando ho tolto il cognome dela mio account su telefram, ho aggiunto il controllo che se il cognome non c'è il sistema non si blocca.

### Versione 1.02 del 31/01/2016
Aggiunto il controllo del server multimedale linux con miniDLNA
Aggiunte alcune try per tracciare problemi in giro per il programma
Aggiunto un log per l'output del programma, far partire il sistema al boot con il comando nel crontab
```@reboot /bin/sleep 60 ; python /cartella_del_programa/tvcc.py >>/cartella_del_log/tvcc_std.log 2>&1```
Aggiunto lo script per controllare se il programma cade, da inserire nel crontab ogni 5 o 10 minuti
Affinata la gestione degli utenti autorizzati, ora sono gestiti tutti e 5

### Versione 1.01 del 27/01/2016
Ho aggiunto il controllo delle eccezioni in caso di avvio del sistema con Internet assente e sulla mancata connessione ai server di Telegram per problemi loro o mancanza di Internet

### Versione 1.0 del 24/01/2016
Funzionalità di base inserite, accensione, spegnimento, richiesta stato e invio messaggi di avviso quando viene rilevato un movimento.
Ripetto alla prima versione beta ho annullato la solita falsa rilevazione dell'errore che segnala il movimento appena il servizio di motion parte.
Resta da definire la procedura fatta bene che verifica gli utenti autorizzati.
