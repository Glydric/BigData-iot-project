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


def mergeDataset(dfs: list[pd.DataFrame]):
    dataset = pd.DataFrame()

    dfs = [df for df in dfs if not df.empty]

    for df in dfs:
        if dataset.empty:
            dataset = df
        else:
            assert dataset["START_DATE"].dtype == df["START_DATE"].dtype
            assert dataset["END_DATE"].dtype == df["END_DATE"].dtype

            dataset = dataset.merge(df, on=["START_DATE", "END_DATE"], how="outer")

    dups = dataset[dataset.duplicated(keep=False)]
    assert dups.shape[0] == 0, dups
    dataset["Stop"] = dataset["Stop"].fillna("Running")

    return dataset


def getEntireDataset(id: int, year_int: int, month_int: int, debug=True):
    year = str(year_int)[slice(2, 4)]
    month = f"{month_int:02d}"

    if debug:
        print("__Getting Fermate__")

    fermate = getFermate(id, year, month)
    if fermate.empty:
        if debug:
            print("WARNING, Fermate was Empty on ", id, year, month)
        return pd.DataFrame()

    if debug:
        print("__Getting Productions__")

    productions = getProductions(id, year, month, debug)
    if productions.empty:
        if debug:
            print("WARNING, Productions was Empty on ", id, year, month)
        return pd.DataFrame()

    if debug:
        print("__Getting Enegy Consumption__")

    energy = getEnergy(id, year, month)
    if energy.empty:
        if debug:
            print("WARNING, Energy was Empty on ", id, year, month)
        return pd.DataFrame()

    assert "END_DATE" in fermate.columns
    assert "END_DATE" in productions.columns
    assert "END_DATE" in energy.columns
    assert "START_DATE" in fermate.columns
    assert "START_DATE" in productions.columns
    assert "START_DATE" in energy.columns

    return mergeDataset([fermate, productions, energy])


def forEveryMachine(fn):
    for machineId, year, month in getList():
        fn(machineId, year, month)

def getList():
    machines = getAvailableMachines()

    list = []
    for machineId in machines:
        for year in machines[machineId].keys():
            for month in machines[machineId][year]:
                list.append((machineId, year, month))
    
    return list
