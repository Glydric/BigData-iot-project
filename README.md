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

So I find out some possible machines and month with good data to analyze:
- machine 306 - 2023/01
- machine 306 - 2023/06
- machine 306 - 2022/12
- machine 305 - 2022/12
- machine 305 - 2023/01
- machine 315 - 2022/12
- machine 315 - 2023/01
- machine 315 - 2023/03
- machine 315 - 2023/06
- machine 315 - 2023/07
- machine 618 - 2023/01
- machine 618 - 2023/03
- machine 618 - 2023/06
- machine 618 - 2023/07
- machine 618 - 2022/12
machine 108 - 2022/11
machine 108 - 2022/12
machine 108 - 2023/06
machine 108 - 2023/07
machine 610 - 2023/01
machine 610 - 2023/06
machine 610 - 2023/07
machine 610 - 2022/12
machine 301 - 2022/12
machine 301 - 2023/01
machine 301 - 2023/03
machine 304 - 2022/12
machine 304 - 2023/01
machine 304 - 2023/07
machine 307 - 2023/01
machine 307 - 2023/03
machine 307 - 2023/05
machine 307 - 2023/06
machine 307 - 2023/07
machine 307 - 2022/12
machine 611 - 2022/12
machine 611 - 2023/01
machine 611 - 2023/03
machine 611 - 2023/06
machine 611 - 2023/07
machine 308 - 2022/12
machine 308 - 2023/01
machine 308 - 2023/06
machine 515 - 2023/01
machine 515 - 2023/06
machine 515 - 2023/07
machine 515 - 2023/08
machine 515 - 2022/12
machine 110 - 2023/01
machine 110 - 2023/03
machine 110 - 2023/05
machine 110 - 2023/06
machine 110 - 2023/07
machine 110 - 2022/12
machine 614 - 2023/01
machine 614 - 2023/03
machine 614 - 2023/06
machine 614 - 2023/07
machine 614 - 2022/11
machine 614 - 2022/12
machine 302 - 2022/12
machine 302 - 2023/01
machine 302 - 2023/03
machine 302 - 2023/06
machine 302 - 2023/07
machine 302 - 2023/01
machine 319 - 2023/07
machine 319 - 2022/12
machine 612 - 2023/01
machine 612 - 2023/03
machine 612 - 2023/07
machine 612 - 2022/12
machine 313 - 2023/01
machine 313 - 2022/12
machine 313 - 2023/01
machine 310 - 2023/06
machine 310 - 2022/12
machine 303 - 2023/01
machine 303 - 2023/03
machine 303 - 2023/07
machine 303 - 2022/12
machine 309 - 2022/12
machine 314 - 2023/01
machine 304 - 2022/12


Possible relations are
- The production problems could be related to the voltage spikes or drops
- Problems/productions rate

# TODO
- (opzionale) Aggiungere il tipo di materiale
 - Generare un dataset che contiene l'articolo e il materiale
- Obiettivo finale: cercare di prevedere i fallimenti in base ai dati di produzione e di tensione (e magari anche in base al tipo di prodotto e di materiale)
  - Innanzitutto è necessaria un'analisi di fattibilità, ci sono 3 casistiche
    - Machine Learning infattibile (dati non correlati)
    - Machine Learning possibile ma non preciso (dati correlati ma insufficienti)
    - Machine Learning possibile e preciso (dati correlati e sufficienti)
  - Successivamente è possibile procedere con l'implementazione di un modello di Machine Learning