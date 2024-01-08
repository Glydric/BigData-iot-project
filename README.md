# BigData-iot-project

This project is about data analysis, a machine generates data A, B, and C the data is get from Kestra, passed to Apache Spark to analyze and find the relations, then the data is stored in a database, and finally, the data is visualized.
 - A dataset are the productions
 - B dataset are the voltages
 - C dataset are the problems

Data is send every 15 minutes. 
Possible relations are 
 - The production problems could be related to the voltage spikes or drops
 - Problems/productions rate

## Getting Started
We use Docker Compose to create the infrastructure