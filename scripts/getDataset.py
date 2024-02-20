import os
import pandas as pd
from datetime import datetime
from .getSingleDataset.getProductions import getProductions
from .getSingleDataset.getFermate import getFermate
from .getSingleDataset.getEnergy import getEnergy


def getAvailableMachines():
    base_dir = "dataset/energy"
    date_format = "%Y-%m-%dT%H-%M-%SZ"

    idsList = set()
    machines = {}

    for f in os.listdir(base_dir):
        if "location_Tormatic" not in f:
            continue
        splittedFilename = f.split("_")
        machineId = splittedFilename[2].split("-")[0]

        date = datetime.strptime(splittedFilename[5], date_format)
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

def cleanDataset(dataset: pd.DataFrame):
    if "COD_ART" in dataset.columns:
        dataset["COD_ART"] = dataset["COD_ART"].fillna("Unknown")
    else:
        dataset["COD_ART"] = "Unknown"

    if "DESFERM" in dataset.columns:
        dataset["DESFERM"] = dataset["DESFERM"].fillna("Unknown")
    
    return dataset

def mergeDataset(dfs: list[pd.DataFrame]):
    dataset = pd.DataFrame()

    dfs = [df for df in dfs if not df.empty]

    for df in dfs:
        if dataset.empty:
            dataset = df
        else:
            assert dataset["TIMESTAMP"].dtype == df["TIMESTAMP"].dtype

            dataset = dataset.merge(df, on="TIMESTAMP", how="outer")

    return dataset


def getEntireDataset(id: int, year_int: int, month_int: int):
    print("\n")
    year = str(year_int)[slice(2, 4)]
    month = f"{month_int:02d}"

    fermate = getFermate(id, year, month)
    if fermate.empty:
        print("WARNING, Fermate was Empty on ", id, year, month)
        return pd.DataFrame()

    productions = getProductions(id, year, month)
    if productions.empty:
        print("WARNING, Productions was Empty on ", id, year, month)
        return pd.DataFrame()

    energy = getEnergy(id, year, month)
    if energy.empty:
        print("WARNING, Energy was Empty on ", id, year, month)
        return pd.DataFrame()

    assert "TIMESTAMP" in fermate.columns
    assert "TIMESTAMP" in productions.columns
    assert "TIMESTAMP" in energy.columns

    return mergeDataset([fermate, productions, energy])


def forEveryMachine(fn):
    machines = getAvailableMachines()

    for machineId in machines:
        for year in machines[machineId].keys():
            for month in machines[machineId][year]:
                fn(machineId, year, month)
