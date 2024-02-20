import os
import pandas as pd
from .utils import getCleanDataset


def prepareEnergy(dataset: pd.DataFrame):
    dataset.rename(columns={"TimeStamp": "TIMESTAMP"}, inplace=True)
    # Removes T and Z from the timestamp to not have problems with UTC and all formats are the same
    dataset["TIMESTAMP"] = dataset["TIMESTAMP"].apply(
        lambda x: x.replace("T", " ").replace("Z", "")
    )
    dataset["TIMESTAMP"] = pd.to_datetime(dataset["TIMESTAMP"])

    dataset.drop(["id"], axis=1, inplace=True)

    def f(x: pd.Series):
        head = x.head(1)

        head["Ea_Imp"] = x["Ea_Imp"].sum()

        return head

    # day group
    grouper = pd.Grouper(key="TIMESTAMP", freq="1D")
    dataset = dataset.groupby(grouper).apply(f, include_groups=False)

    dataset = dataset.reset_index()

    dataset.rename({"Ea_Imp": "EnergyConsumption"}, axis=1, inplace=True)

    dataset.drop(["level_1"], axis=1, inplace=True)

    return dataset


# Get the energy consumption values
def getEnergy(id: str, year: str, month: str):
    base_dir = "dataset/energy"
    file = "location_Tormatic-channel_{}-register_Ea_Imp_20{}-{}-"

    dfs = []

    for f in os.listdir(f"{base_dir}"):
        if f.startswith(file.format(int(id), year, month)):
            dfs.append(getCleanDataset(f"{base_dir}/{f}"))

    if dfs == []:
        return pd.DataFrame()

    dataset = pd.concat(dfs, ignore_index=True)

    if dataset.empty:
        return dataset
    return prepareEnergy(dataset)
