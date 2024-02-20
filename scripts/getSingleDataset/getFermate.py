import os
import pandas as pd
from .utils import getCleanDataset


valid_fermate = [
    "Manutenzione ordinaria",
    "Manutenzione straordinaria",
    "Affilatura Utensile",
    "Sostituzione utensile",
]


def prepareFermate(dataset: pd.DataFrame):
    # check if shift_date is the same as shift_start, shift_end, start_date, end_date
    assert (dataset["SHIFT_DATE"] == dataset["SHIFT_START"]).all()
    assert (dataset["SHIFT_START"] == dataset["SHIFT_END"]).all()
    assert (dataset["SHIFT_END"] == dataset["START_DATE"]).all()
    assert (dataset["START_DATE"] == dataset["END_DATE"]).all()

    dataset = dataset[dataset["DESFERM"].isin(valid_fermate)]

    dataset.drop(
        ["SHIFT_DATE", "SHIFT_START", "SHIFT_END", "START_DATE", "END_DATE"],
        axis=1,
        inplace=True,
    )

    # TODO check why the following data is always the same
    if dataset["SHIFT_CODE"].diff(0).all():
        print("WARNING, you are dropping SHIFT_CODE that is not always the same")
        print(dataset["SHIFT_CODE"].unique())

    if (dataset["STAGE"] != 10).all():
        print("WARNING, you are dropping STAGE that is not always the same")
        print(dataset["STAGE"].unique())

    if (dataset["STOP_CODE"] != 2).all():
        print("WARNING, you are dropping STOP_CODE that is not always the same")
        print(dataset["STOP_CODE"].unique())

    if (dataset["QTY_SCRAP"] != 0).all():
        print("WARNING, you are dropping QTY_SCRAP that is not always the same")
        print(dataset["QTY_SCRAP"].unique())

    if (dataset["QTY_GOOD"] != 0).all():
        print("WARNING, you are dropping QTY_GOOD that is not always the same")
        print(dataset["QTY_GOOD"].unique())

    dataset = dataset.groupby(["TIMESTAMP", "DESFERM"]).count().reset_index()

    # we choose SHIFT_CODE but it can be any column
    dataset.rename(columns={"SHIFT_CODE": "Fermate"}, inplace=True)

    dataset.drop(
        [
            "PRODUCTION_ORDER",
            "STAGE",
            "STOP_CODE",
            "T_STOP",
            "QTY_GOOD",
            "QTY_SCRAP",
        ],
        axis=1,
        inplace=True,
    )

    return dataset


# Get the stops
def getFermate(id: str, year: str, month: str):
    base_dir = "dataset/fermi/Fermate"

    dfs = []
    # dataset = getCleanDataset(f"{base_dir}/FERMATE {year}{month}.csv")
    for f in os.listdir(f"{base_dir}"):
        if not f.startswith(f"FERMATE "):
            continue
        df = getCleanDataset(f"{base_dir}/{f}")

        # this automatically handles the "0101" -> "101" conversion as df["RESOURCE"].dtypes is int64
        df = df[df["RESOURCE"] == int(id)]
        # remove the resource column as it is the id we are already filtered it
        df.drop("RESOURCE", axis=1, inplace=True)

        df["TIMESTAMP"] = pd.to_datetime(df["SHIFT_DATE"], format="%d-%b-%y")
        df = df[df["TIMESTAMP"].dt.strftime("%y-%m") == f"{year}-{month}"]

        dfs.append(df)

    if dfs == []:
        return pd.DataFrame()

    dataset = pd.concat(dfs, ignore_index=True)

    if dataset.empty:
        return dataset

    return prepareFermate(dataset)
