# BigData-iot-project

This project is about data analysis, a machine generates data A, B, and C the data analyzed, then it is stored in a database, and finally visualized.

## Dataset

The dataset is formed by
- Energy Consumption, small files in the form of energy/location*Tormatic_channel*{id}...csv
- Productions, a big files in the form of energy/Tomatic*{date}*...csv
- Stops, a big files in the form of fermi/FERMATE\ YYMM.csv - The names are made of YY (year) and MM (month)
We firstly need to merge those files into a single file for each channel and date

## Dataset analysis
The analysis is made using the Jupyter Notebook and pandas library
- First of all, I need to merge the dataset into a single file
  - To do this I have to clean the dataset to prepare the merge, problems like different timestamps and different formats do not allow the data to be merged
- Then I used a visual library like Plotly to make show the data and think on the possible analysis to do

Possible relations are
- The production problems could be related to the voltage spikes or drops
- Problems/productions rate

## Remove the useless machines
First of all I removed from dataset the machines without enough data and get the followings:
- Machine 306 - 2023/03
- Machine 306 - 2023/06
- Machine 306 - 2023/07
- Machine 306 - 2023/08
- Machine 306 - 2022/12
- Machine 315 - 2022/12
- Machine 315 - 2023/03
- Machine 618 - 2023/03
- Machine 108 - 2023/03
- Machine 108 - 2023/07
- Machine 108 - 2023/08
- Machine 610 - 2023/01
- Machine 610 - 2023/06
- Machine 610 - 2023/07
- Machine 610 - 2023/08
- Machine 610 - 2022/12
- Machine 301 - 2023/01
- Machine 301 - 2023/03
- Machine 301 - 2023/06
- Machine 301 - 2022/12
- Machine 304 - 2023/01
- Machine 304 - 2023/03
- Machine 304 - 2023/06
- Machine 307 - 2023/03
- Machine 307 - 2023/06
- Machine 611 - 2022/12
- Machine 611 - 2023/03
- Machine 611 - 2023/06
- Machine 611 - 2023/08
- Machine 308 - 2023/01
- Machine 308 - 2023/03
- Machine 515 - 2023/01
- Machine 515 - 2023/03
- Machine 515 - 2023/06
- Machine 515 - 2023/07
- Machine 515 - 2023/08
- Machine 515 - 2022/12
- Machine 110 - 2023/01
- Machine 110 - 2023/03
- Machine 110 - 2023/06
- Machine 110 - 2023/07
- Machine 110 - 2023/08
- Machine 110 - 2022/12
- Machine 614 - 2023/01
- Machine 614 - 2023/03
- Machine 614 - 2023/06
- Machine 614 - 2023/07
- Machine 302 - 2022/12
- Machine 302 - 2023/03
- Machine 302 - 2023/06
- Machine 319 - 2023/03
- Machine 319 - 2023/06
- Machine 319 - 2023/07
- Machine 319 - 2022/12
- Machine 612 - 2023/01
- Machine 612 - 2023/03
- Machine 612 - 2023/07
- Machine 612 - 2022/12
- Machine 313 - 2023/01
- Machine 313 - 2023/03
- Machine 310 - 2023/03
- Machine 310 - 2023/06
- Machine 303 - 2023/03
- Machine 303 - 2023/06
- Machine 303 - 2022/12
- Machine 309 - 2023/03
- Machine 309 - 2023/06
- Machine 314 - 2023/03
- Machine 314 - 2023/06

Then I checked for the graph and taked the ones that seems to have a good correlation, getting the followings
- Machine 108 - 2023/07
- Machine 110 - 2022/12
- Machine 110 - 2023/01
- Machine 110 - 2023/03
- Machine 110 - 2023/06
- Machine 110 - 2023/07
- Machine 301 - 2022/12
- Machine 301 - 2023/01
- Machine 301 - 2023/03
- Machine 302 - 2022/12
- Machine 302 - 2023/03
- Machine 302 - 2023/06
- Machine 303 - 2022/12
- Machine 303 - 2023/03
- Machine 304 - 2023/01
- Machine 306 - 2022/12
- Machine 306 - 2023/06
- Machine 307 - 2023/03
- Machine 307 - 2023/06
- Machine 308 - 2023/01
- Machine 310 - 2023/06
- Machine 313 - 2023/01
- Machine 315 - 2022/12
- Machine 315 - 2023/03
- Machine 319 - 2022/12
- Machine 319 - 2023/07
- Machine 515 - 2022/12
- Machine 515 - 2023/01
- Machine 515 - 2023/06
- Machine 515 - 2023/07
- Machine 515 - 2023/08
- Machine 610 - 2022/12
- Machine 610 - 2023/01
- Machine 610 - 2023/06
- Machine 610 - 2023/07
- Machine 611 - 2022/12
- Machine 611 - 2023/03
- Machine 611 - 2023/06
- Machine 612 - 2022/12
- Machine 612 - 2023/01
- Machine 612 - 2023/03
- Machine 612 - 2023/07
- Machine 614 - 2023/01
- Machine 614 - 2023/03
- Machine 614 - 2023/06
- Machine 614 - 2023/07
- Machine 618 - 2023/03


# Feasibility analysis
It seems that we have enough data to make a machine learning model, but we need to check if the data is correlated and if the data is enough to make a model


# TODO
- (opzionale) Aggiungere il tipo di materiale
 - Generare un dataset che contiene l'articolo e il materiale
- Obiettivo finale: cercare di prevedere i fallimenti in base ai dati di produzione e di tensione (e magari anche in base al tipo di prodotto e di materiale)
  - Innanzitutto è necessaria un'analisi di fattibilità, ci sono 3 casistiche
    - Machine Learning infattibile (dati non correlati)
    - Machine Learning possibile ma non preciso (dati correlati ma insufficienti)
    - Machine Learning possibile e preciso (dati correlati e sufficienti)
  - Successivamente è possibile procedere con l'implementazione di un modello di Machine Learning