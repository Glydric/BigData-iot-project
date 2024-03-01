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
- Then I used a visual library named Plotly to visually show the data to think on the possible analysis

Possible relations are

- The production problems could be related to the voltage spikes or drops
- Problems/productions rate

## Remove the useless machines

First of all I removed from dataset the months without enough data, the results are the followings:

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

# Feasibility analysis

It seems that we have enough data to make a machine learning model, but we need to check if the data is correlated.
First of all i merged the months of the same machine to have a wider view of the lifecycle of a single machine, this allows me to better understand if a machine have enough data to be suitable for ML, those are the results:

- Machine 108, have only 1 month of incomplete data, i'll remove it
- Machine 110, the data shows inconsistency on the stops, as sometime increases with productions and EC, sometimes decreases
- Machine 301, at the beginning the stops do not changes the productions, then the stops follows EC, then it shows consistency and inconsistency unpredictably
- Machine 302, sometimes the stops increases with the productions, sometimes decreases
- Machine 303, we don't have enough data
- Machine 304, we don't have enough data
- Machine 306, may be interesting, in the second half, the EC sometimes is related to the stops, sometimes to the productions
- Machine 307, we don't have enough data
- Machine 308, we don't have enough data
- Machine 310, we don't have enough data
- Machine 313, if the first half the Stops leads to a decrease in EC and Productions, while on the second half this is not true
- Machine 315, sometimes the stops increases with the productions and EC, sometimes decreases
- Machine 319, sometimes the stops increases with the productions and EC, sometimes decreases
- Machine 515, sometimes the stops increases with the productions and EC, sometimes decreases
- Machine 610, sometimes the stops increases with the productions and EC, sometimes decreases
- ...

At the end I used Pearson correlation to compute and remove the machines that does not have at least one correlated value.
The results are:

- Machine 304
- Machine 515
- Machine 110
- Machine 306
- Machine 302
- Machine 303
- Machine 301
- Machine 315
- Machine 314
- Machine 611
- Machine 610
- Machine 612
- Machine 618
- Machine 108
- Machine 309

We have a total of 2389 rows of data, that are probably not enough to make a machine learning model, but we can try to make a model and see the results.

# Machine Learning

## Test 1
After we prepared data for the model we train using 80% of the data and test using the remaining 20%. I used the shuffled method to randomize the data to overfitting. The result is an average Mean Square Error of 1.5

## Test 2
Then I tried to use the latest data to train the model while use the whole dataset to test the model without shuffling, the result is even worse than the previous as it have an average Mean Square Error of 2.12

This means that the model is not able to predict the failures in our context, but as we have different correlations probably the data is not enough to make a model. 

# TODO

- nel timestamp Prendere il valore precedente se inizio ed il valore successivo se la fine
- Istogram boosting (parametro poasson(poisson?) true?)
- (opzionale) Aggiungere il tipo di materiale
- Generare un dataset che contiene solo l'articolo e il materiale
- Obiettivo finale: cercare di prevedere i fallimenti in base ai dati di produzione e di tensione (e magari anche in base al tipo di prodotto e di materiale)
  - Innanzitutto è necessaria un'analisi di fattibilità, ci sono 3 casistiche
    - Machine Learning infattibile (dati non correlati)
    - Machine Learning possibile ma non preciso (dati correlati ma insufficienti)
    - Machine Learning possibile e preciso (dati correlati e sufficienti)
  - Nel caso l'analisi di fattibilità fosse positiva si implementa un modello di Machine Learning
  - Per prevedere quando sarà da fare nuova sostituzione utensile dobbiamo avere abbastanza dati
