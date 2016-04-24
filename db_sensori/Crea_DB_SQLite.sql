-- Struttura del DB per il istema di controllo di casa

-- Tabella dei luoghi (le camere della casa)

CREATE TABLE Luoghi
(
    ID INTEGER PRIMARY KEY ASC,
    Descrizione TEXT NOT NULL
);

-- Questi sono i luoghi standard

INSERT INTO Luoghi (ID, Descrizione) VALUES(1, "Balcone Cortile");
INSERT INTO Luoghi (ID, Descrizione) VALUES(2, "Balcone Strada");
INSERT INTO Luoghi (ID, Descrizione) VALUES(3, "Cucina");
INSERT INTO Luoghi (ID, Descrizione) VALUES(4, "Sala");
INSERT INTO Luoghi (ID, Descrizione) VALUES(5, "Camera");
INSERT INTO Luoghi (ID, Descrizione) VALUES(6, "Studio");
INSERT INTO Luoghi (ID, Descrizione) VALUES(7, "Bagno");
INSERT INTO Luoghi (ID, Descrizione) VALUES(8, "Lavanderia");

-- Tabella per le temperature

CREATE TABLE Temperature
(
    ID INTEGER PRIMARY KEY ASC,
    Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    Luogo INTEGER,
    Temp REAL,
    Umid INTEGER
);

-- Tabella per la rilevazione del consumo di corrente

CREATE TABLE Corrente
(
    ID INTEGER PRIMARY KEY ASC,
    Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    Luogo INTEGER,
    Consumo INTEGER
);

-- Tabella degli allarmi

CREATE TABLE Allarmi
(
    ID INTEGER PRIMARY KEY ASC,
    Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    Luogo INTEGER,
    Descrizione TEXT,
    Avvisato TEXT DEFAULT "NO",
    DataOraCessato TIMESTAMP  
);
