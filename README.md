# Un bot in grado di gestire dei sensori in casa
Telegram è un'ottima piattaforma per creare bot che possano interagire con i messaggi di domando inviati tramite il proprio dispositivo portatile.
Ho creato questo piccolo sistema per controllare l'impianto di videosorveglianza in casa (lo accendo, lo spengo, lo interrogo sullo stato e mi faccio mandare un avviso e le foto quando capita che viene rilevato un movimento.
L'applicazione è in Python, usa le librerie [telepot](https://github.com/nickoala/telepot) per interagire con le [API di Telegram](https://core.telegram.org/) e il programma [motion](http://www.lavrsen.dk/foswiki/bin/view/Motion/WebHome) per rilevare il movimento, usando la videocamera IR presente sul Raspberry Pi

Il programma _tvcc.py_ va avviato al boot del sistema, in modo che il bot sia pronto (per motivi di sicurezza, al riavvio del raspberry la videosorveglianza viene attivata in automatico)
Il programma _invia_foto.py_ va inserito nel file di configurazione di motion alla riga _on_picture_save_ (invia una foto ogni volta che questa viene salvata su disco, il problema è la lentezza dovuta al fatto che ogni volta deve aprire una connessione con Telegram)
Il programma _avvisa_movimento.py_ va inserito nel file di configurazione di motion alla riga _on_event_start_ (avvisa che un evento di rilevazione di movimento è iniziato)
E' necessario ricordarsi di mettere la calncellazione della cartelle delle foto alla riga _on_event_end_ altrimenti il disco si potrebbe riempire rapidamente

## Versione 1.0 del 24/01/2016
Funzionalità di base inserite, accensione, spegnimento, richiesta stato e invio messaggi di avviso quando viene rilevato un movimento.
Ripetto alla prima versione beta ho annullato la solita falsa rilevazione dell'errore che segnala il movimento appena il servizio di motion parte.
Resta da definire la procedura fatta bene che verifica gli utenti autorizzati.
