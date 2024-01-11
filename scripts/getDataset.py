import os
import csv


# Get the list of stops
def getFermate():
    fermateDir = "dataset/fermi/Fermate"

    files = os.listdir(fermateDir)
    for f in files:
        with open(f"{fermateDir}/{f}", "r") as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            for row in reader:
                print(row)
            print(reader.line_num)
            # fermate = list(reader)
    # return fermate

if __name__ == "__main__":
    getFermate()