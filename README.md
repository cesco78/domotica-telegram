# Un bot in grado di gestire dei sensori in casa
Telegram è un'ottima piattaforma per creare bot che possano interagire con i messaggi di domando inviati tramite il proprio dispositivo portatile.
Ho creato questo piccolo sistema per controllare l'impianto di videosorveglianza in casa (lo accendo, lo spengo, lo interrogo sullo stato e mi faccio mandare un avviso e le foto quando capita che viene rilevato un movimento.
L'applicazione è in Python, usa le librerie "telepot" per interagire con Telegram e il programma "motion" per rilevare il movimento, usando la videocamera IR presente sul Raspberry Pi

## Versione 1.0 del 21/01/2016
Funzionalità di base inserite, accensione, spegnimento, richiesta stato e invio messaggi di avviso quando viene rilevato un movimento.
Ripetto alla prima versione beta ho annullato la solita falsa rilevazione dell'errore che segnala il movimento appena il servizio di motion parte.
