import os
import pandas as pd
from .utils import getCleanDataset


def prepareEnergy(dataset: pd.DataFrame):
    dataset.rename(
        {
            "TimeStamp": "TIMESTAMP",
            "Ea_Imp": "EnergyConsumption",
        },
        axis=1,
        inplace=True,
    )
    # Removes T and Z from the timestamp to not have problems with UTC and all formats are the same
    dataset["TIMESTAMP"] = dataset["TIMESTAMP"].apply(
        lambda x: x.replace("T", " ").replace("Z", "")
    )

    dataset["END_DATE"] = pd.to_datetime(dataset["TIMESTAMP"])
    dataset["START_DATE"] = dataset["END_DATE"] - pd.Timedelta("15 min")

    dataset.drop(["id", "TIMESTAMP"], axis=1, inplace=True)

    # dataset = dataset.groupby(["TIMESTAMP"]).sum(numeric_only=True).reset_index()

    # print(dataset)

    return dataset.groupby(["START_DATE", "END_DATE"]).sum().reset_index()


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
