import os
import pandas as pd
from datetime import datetime
from plots import plot
from getSingleDataset.getProductions import getProductions
from getSingleDataset.getFermate import getFermate
from getSingleDataset.getEnergy import getEnergy


def mergeDataset(dfs: [pd.DataFrame]):
    dataset = pd.DataFrame()

    dfs = [df for df in dfs if not df.empty]

    for df in dfs:
        # df["TIMESTAMP"] = df["TIMESTAMP"].dt.round("1h")

        if dataset.empty:
            dataset = df
        else:
            assert dataset["TIMESTAMP"].dtype == df["TIMESTAMP"].dtype

            dataset = dataset.merge(df, on="TIMESTAMP", how="outer")

    # completeDataset = completeDataset.dropna()

    return dataset


def getEntireDataset(id: int, year_int: int, month_int: int):
    year = str(year_int)[slice(2, 4)]
    month = f"{month_int:02d}"

    print("__Getting Fermate__")
    fermate = getFermate(id, year, month)
    if fermate.empty:
        print("WARNING, Fermate was Empty")
    else:
        assert "TIMESTAMP" in fermate.columns

    print("__Getting Productions__")
    productions = getProductions(id, year, month)
    if productions.empty:
        print("WARNING, Productions was Empty")
    else:
        assert "TIMESTAMP" in productions.columns

    print("__Getting Enegy Consumption__")
    energy = getEnergy(id, year, month)
    if energy.empty:
        print("WARNING, Energy was Empty")
    else:
        assert "TIMESTAMP" in energy.columns

    return mergeDataset([fermate, productions, energy])


def getAvailableMachines():
    base_dir = "dataset/energy"
    date_format = "%Y-%m-%dT%H-%M-%SZ"

    idsList = set()
    machines = {}

    for f in os.listdir(base_dir):
        if "location_Tormatic" not in f:
            continue
        splitedFilename = f.split("_")
        machineId = splitedFilename[2].split("-")[0]

        date = datetime.strptime(splitedFilename[5], date_format)
        year = date.year
        month = date.month

        if machineId in machines.keys():
            if year in machines[machineId].keys():
                machines[machineId][year].add(month)
            else:
                machines[machineId][year] = set([month])

        else:
            machines[machineId] = {
                year: set([month]),
            }

        idsList.add(machineId)

    return machines


if __name__ == "__main__":
    pd.set_option("display.max_rows", None)
    pd.options.mode.copy_on_write = True

    id = "0301"
    try:

        machines = getAvailableMachines()
        dfs = []
        errors = []
        # try:
        #     print(getEntireDataset(306, 2022, 7))
        # except Exception as e:
        #     errors.append(e)

        for machineId in machines:
            for year in machines[machineId].keys():
                for month in machines[machineId][year]:
                    print(
                        f"\n\n----- Machine {machineId} Year {year} Month {month} ------"
                    )
                    try:
                        df = getEntireDataset(machineId, year, month)
                        plot(df, machineId)

                        df["ID"] = machineId
                        dfs.append(df)
                    except Exception as e:
                        print(f"Error {e}")
                        errors.append(e)
                        errors.append(
                            {
                                "machineId": machineId,
                                "year": year,
                                "month": month,
                                "error": e,
                            }
                        )

        if errors != []:
            print(errors)
        completeDataset = pd.concat(dfs, ignore_index=True)

        print(f"\n----- Entire Dataset {id} ------\n")

        print(completeDataset)
        print(completeDataset.shape)
        plot(completeDataset)

    except Exception as e:
        print(e)
