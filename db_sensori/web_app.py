#!/usr/bin/env python2.7

# applicazione web per ricevere i dati dei sensori e degli allarmi del sistema
# il DB e' in SQlite ed e' creato con la seguente struttura
# nome del DB: domotica.db
# comando --> $ sqlite3 domodica.db
#
# Fare il backup del DB (non dimenticarsi di farlo!!)
# comando --> echo '.dump' | sqlite3 /home/pi/domotica.db > exportdb
import web
import sqlite3

        
urls = (
    '/(.*)', 'hello'
)
app = web.application(urls, globals())

class hello:        
    def GET(self, data):
        data = web.input()
        tabella = data.tab #temp => Temperature - corr => Corrente - all => Allarmi
        
        # Arriva un dato di temperatura => http://[IP]:8000/?tab=temp&a=1&t=20&h=45
        if (tabella =="temp"):
            zona = data.a
            temp = data.t
            humi = data.h
            
            connessione = None
        
            try:
                connessione = sqlite3.connect('/home/pi/domotica.db')
                
                cursore = connessione.cursor()
                # inserisco la lettura della temeratura
                cursore.execute("INSERT INTO Temperature (Luogo, Temp, Umid) VALUES (" + zona + ", " + temp + ", " + humi + ");")
    
                
                return 'Ho registrato questo: zona ' + zona + ' - Temperatura ' + temp + '*C - Umidita ' + humi +'%'
            
            except sqlite3.Error, e:
                return "Error %s:" % e.args[0]
            
            finally:
                if connessione:
                    connessione.commit()
                    connessione.close()
        
        # Arriva un dato di consumo di corrente => http://[ip]:8000/?tab=corr&a=1&w=2500
        elif (tabella =="corr"):
            zona = data.a
            watt = data.w
            
            connessione = None
        
            try:
                connessione = sqlite3.connect('/home/pi/domotica.db')
                
                cursore = connessione.cursor()
                # inserisco la lettura della corrente
                cursore.execute("INSERT INTO Corrente (Luogo, Consumo) VALUES (" + zona + ", " + watt + ");")
    
                
                return 'Ho registrato questo: zona ' + zona + ' - Consumo ' + watt + ' Watt'
            
            except sqlite3.Error, e:
                return "Error %s:" % e.args[0]
            
            finally:
                if connessione:
                    connessione.commit()
                    connessione.close()

if __name__ == "__main__":

    app.run()
