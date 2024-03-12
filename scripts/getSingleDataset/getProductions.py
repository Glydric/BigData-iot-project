import os
import pandas as pd
from .utils import cleanDataset, getCleanDataset
import numpy as np


def productionFixComma(line: str, columns: int):
    newline = line.replace("\n", "")

    if line.count(",") == columns:
        newline = newline.replace(",", ".", 3).replace(".", ",", 2)

    return newline


def getProductionWithFixedComma(name: str):
    # previous = datetime.now()
    with open(name, errors="ignore") as file:
        lines = file.readlines()

        head = lines[0].split(",")

        correctedFile = [productionFixComma(line, len(head)) for line in lines]

        correctedFile.remove(correctedFile[0])
        correctedFile.remove(correctedFile[1])

        lines_data = [line.split(",") for line in correctedFile]

        df = pd.DataFrame(lines_data)
        df.rename(columns={x: head[x] for x in range(0, len(head))}, inplace=True)

        return cleanDataset(df)


def handleDate(dataset: pd.DataFrame):
    dataset["START_DATE"] = pd.to_datetime(dataset["START_DATE"])
    dataset["END_DATE"] = pd.to_datetime(dataset["END_DATE"])

    time_interval = dataset["END_DATE"] - dataset["START_DATE"]
    dataset.drop(["END_DATE"], axis=1, inplace=True)

    # Porta al minuto
    time_interval = time_interval.dt.total_seconds() / 60
    dataset["Productions"] = dataset["Productions"] / time_interval

    # Duplicate the rows in base of the time interval
    dataset = dataset.loc[dataset.index.repeat(time_interval)]

    # --- Porta al quarto d'ora

    # Group by 'START_DATE' and generate a sequence of minutes for each group
    minutes_to_add = dataset.groupby("START_DATE").cumcount()

    # Convert the sequence of minutes to a timedelta and add it to 'START_DATE'
    dataset["START_DATE"] = dataset["START_DATE"] + pd.to_timedelta(
        minutes_to_add, unit="m"
    )

    total_number = time_interval.sum()
    assert total_number == dataset.shape[0], f"{total_number} {dataset.shape[0]}"

    dataset["START_DATE"] = dataset["START_DATE"].dt.floor("15min")
    dataset = (
        dataset
        .groupby(["START_DATE", "COD_ART"])
        .sum(numeric_only=True)
        .reset_index()
        .head(50)
    )

    assert not dataset.isna()["COD_ART"].any(), dataset.isna()["COD_ART"].any()
    assert "COD_ART" in dataset.columns

    dataset["END_DATE"] = dataset["START_DATE"] + pd.Timedelta("15min")

    return dataset


def prepareProductions(dataset: pd.DataFrame, year: int, month: int):
    dataset.rename(
        {
            "TIMESTAMP_INIZIO": "START_DATE",
            "TIMESTAMP_FINE": "END_DATE",
            "NUMERO_PEZZI_PROD": "Productions",
        },
        axis=1,
        inplace=True,
    )

    dataset.drop(["ID"], axis=1, inplace=True)
    dataset["Productions"] = pd.to_numeric(dataset["Productions"])

    # TODO review those drops
    if "EXP_STATUS" in dataset.columns and dataset["EXP_STATUS"].eq("0").all():
        dataset.drop("EXP_STATUS", axis=1, inplace=True)

    if "ODP" in dataset.columns:
        dataset.drop(["ODP"], axis=1, inplace=True)

    dataset = handleDate(dataset)

    return dataset.groupby(["START_DATE", "END_DATE", "COD_ART"]).sum().reset_index()


# Get the productions
def getProductions(id: str, year: str, month: str, debug=False):
    base_dir = "dataset/productions"

    dfs = []

    for f in os.listdir(f"{base_dir}"):
        if not f.startswith(f"Tormatic_20{year}{month}"):
            continue

        try:
            df = getCleanDataset(
                f"{base_dir}/{f}",
                {
                    "COD_MACC": int,
                    "NUMERO_PEZZI_PROD": float,
                    "ID": int,
                    "EXP_STATUS": int,
                },
            )
        except Exception as e:
            if debug:
                print(f"Using fix on Production file {f}, Error {e}")
            df = getProductionWithFixedComma(f"{base_dir}/{f}")

        df.dropna(inplace=True)
        df.drop(0, inplace=True)

        if "COD_MACC" not in df.columns:
            continue

        df["COD_MACC"] = pd.to_numeric(df["COD_MACC"])

        df.dropna(inplace=True)
        df = df.astype({"COD_MACC": "int32"})

        df = df[df["COD_MACC"] == int(id)]

        df.drop(["COD_MACC"], axis=1, inplace=True)

        dfs.append(df)

    if dfs == []:
        return pd.DataFrame()

    dataset = pd.concat(dfs, ignore_index=True)

    if dataset.empty:
        return dataset

    return prepareProductions(dataset, year, month)
