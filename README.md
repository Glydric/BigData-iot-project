# BigData-iot-project

This project is about data analysis, a machine generates data A, B, and C the data is get from Kestra, passed to Apache Spark to analyze and find the relations, then the data is stored in a database, and finally, the data is visualized.

- A dataset are the productions
- B dataset are the voltages
- C dataset are the problems

Data is send every 15 minutes.
Possible relations are

- The production problems could be related to the voltage spikes or drops
- Problems/productions rate

## Dataset

the dataset is formed by

- energy files in the form of energy/location*Tormatic_channel*{id}...csv
- Production big file in the form of energy/Tomatic*{date}*...csv
- Problems big file in the form of fermi/FERMATE\ YYMM.csv - The names are made of YY (year) and MM (month)
  We firstly need to merge those files into a single file for each channel and date

## Getting Started

We use Docker Compose to create the infrastructure

# TODO

- Aggiungere il tipo di prodotto all'interno del dataset
- (opzionale) Aggiungere il tipo di materiale
 - Generare un dataset che contiene l'articolo e il materiale
- Obiettivo finale: cercare di prevedere i fallimenti in base ai dati di produzione e di tensione (e magari anche in base al tipo di prodotto e di materiale)
  - Innanzitutto è necessaria un'analisi di fattibilità, ci sono 3 casistiche
    - Machine Learning infattibile (dati non correlati)
    - Machine Learning possibile ma non preciso (dati correlati ma insufficienti)
    - Machine Learning possibile e preciso (dati correlati e sufficienti)
  - Successivamente è possibile procedere con l'implementazione di un modello di Machine Learning