import os
import pandas as pd
from .utils import cleanDataset

def productionFixComma(line: str, columns: int):
    newline = line.replace("\n", "")

    if line.count(",") == columns:
        newline = newline.replace(",", ".", 3).replace(".", ",", 2)

    return newline


def getProductionWithFixedComma(name: str):
    # previous = datetime.now()
    with open(name) as file:
        lines = file.readlines()

        head = lines[0].split(",")

        correctedFile = [productionFixComma(line, len(head)) for line in lines]

        correctedFile.remove(correctedFile[0])
        correctedFile.remove(correctedFile[1])

        lines_data = [line.split(",") for line in correctedFile]

        df = pd.DataFrame(lines_data)
        df.rename(columns={x: head[x] for x in range(0, len(head))}, inplace=True)

        # print(datetime.now() - previous)
        return cleanDataset(df)


def prepareProductions(dataset: pd.DataFrame, year: int, month: int):
    dataset["TIMESTAMP_INIZIO"] = pd.to_datetime(dataset["TIMESTAMP_INIZIO"])
    dataset["TIMESTAMP_FINE"] = pd.to_datetime(dataset["TIMESTAMP_FINE"])
    dataset["NUMERO_PEZZI_PROD"] = pd.to_numeric(dataset["NUMERO_PEZZI_PROD"])

    dataset["TIMESTAMP"] = dataset[["TIMESTAMP_INIZIO", "TIMESTAMP_FINE"]].mean(axis=1)

    dataset.drop(["TIMESTAMP_INIZIO", "TIMESTAMP_FINE"], axis=1, inplace=True)

    dataset = dataset[dataset["TIMESTAMP"].dt.strftime("%y-%m") == f"{year}-{month}"]

    def f(x: pd.Series):
        head = x.head(1)

        head["NUMERO_PEZZI_PROD"] = x["NUMERO_PEZZI_PROD"].sum()

        return head

    grouper = pd.Grouper(key="TIMESTAMP", freq="1D")
    dataset = dataset.groupby(grouper).apply(f, include_groups=False)

    # Grouper used TIMESTAMP as index, here we convert to column
    dataset = dataset.reset_index()

    dataset.drop("ID", axis=1, inplace=True)

    if dataset["EXP_STATUS"].eq("0").all():
        dataset.drop("EXP_STATUS", axis=1, inplace=True)

    dataset.rename({"NUMERO_PEZZI_PROD": "Productions"}, axis=1, inplace=True)

    # TODO review those drops
    # this is to remove a strange column that is created on grouping
    dataset.drop(["level_1"], axis=1, inplace=True)
    dataset.drop(["COD_ART"], axis=1, inplace=True)
    if "ODP" in dataset.columns:
        dataset.drop(["ODP"], axis=1, inplace=True)

    return dataset


# Get the productions
def getProductions(id: str, year: str, month: str):
    base_dir = "dataset/productions"

    dfs = []

    for f in os.listdir(f"{base_dir}"):
        if not f.startswith(f"Tormatic_20{year}{month}"):
            continue

        df = getProductionWithFixedComma(f"{base_dir}/{f}")

        df.dropna(inplace=True)
        df.drop(0, inplace=True)

        # print(df.loc[[210]])
        # print(f)

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