import os
import pandas as pd
from .utils import getCleanDataset


valid_fermate = [
    "Manutenzione ordinaria",
    "Manutenzione straordinaria",
    "Affilatura Utensile",
    "Affilatura utensile",
    "Sostituzione utensile",
]

def drops(dataset: pd.DataFrame):

    # why the following data is always the same
    # if dataset["Fermate"].diff(0).all():
    #     print("WARNING, you are dropping SHIFT_CODE that is not always the same")
    #     print(dataset["Fermate"].unique())

    if (dataset["STAGE"] != 10).all():
        print("WARNING, you are dropping STAGE that is not always the same")
        print(dataset["STAGE"].unique())

    # if (dataset["STOP_CODE"] != 2).all():
    # print("WARNING, you are dropping STOP_CODE that is not always the same")
    # print(dataset["STOP_CODE"].unique())

    if (dataset["QTY_SCRAP"] != 0).all():
        print("WARNING, you are dropping QTY_SCRAP that is not always the same")
        print(dataset["QTY_SCRAP"].unique())

    if (dataset["QTY_GOOD"] != 0).all():
        print("WARNING, you are dropping QTY_GOOD that is not always the same")
        print(dataset["QTY_GOOD"].unique())

    # we choose SHIFT_CODE but it can be any column

    dataset.drop(
        [
            "SHIFT_DATE",
            "SHIFT_START",
            "SHIFT_END",
            "SHIFT_CODE",
             
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

def prepareFermate(dataset: pd.DataFrame):
    # check if shift_date is the same as shift_start, shift_end, start_date, end_date
    assert (dataset["SHIFT_START"] == dataset["START_DATE"]).all()
    assert (dataset["SHIFT_END"] == dataset["END_DATE"]).all()

    dataset = drops(dataset)

    dataset["START_DATE"] = pd.to_datetime(dataset["START_DATE"]).dt.floor("15min")
    dataset["END_DATE"] = pd.to_datetime(dataset["END_DATE"]).dt.floor("15min")
    dataset.rename(columns={"DESFERM": "Stop"}, inplace=True)

    time_interval = dataset["END_DATE"] - dataset["START_DATE"]
    time_interval = time_interval.dt.total_seconds() / 60 / 15

    dataset.drop(["END_DATE"], axis=1, inplace=True)

    dataset = dataset.loc[dataset.index.repeat(time_interval)]

    total_number = time_interval.sum()
    assert total_number == dataset.shape[0], f"{total_number} {dataset.shape[0]}"

    # --- Porta al quarto d'ora
    # Group by 'START_DATE' and generate a sequence of minutes for each group
    minutes_to_add = dataset.groupby("START_DATE").cumcount()

    # Convert the sequence of minutes to a timedelta and add it to 'START_DATE'
    dataset["START_DATE"] = dataset["START_DATE"] + pd.to_timedelta(
        minutes_to_add, unit="m"
    )

    dataset["START_DATE"] = dataset["START_DATE"].dt.floor("15min")
    dataset = (
        dataset.groupby(["START_DATE", "Stop"])
        .sum(numeric_only=True)
        .reset_index()
        .head(50)
    )

    dataset["END_DATE"] = dataset["START_DATE"] + pd.Timedelta("15min")

    dataset = dataset.groupby(["START_DATE", "END_DATE", "Stop"]).count().reset_index()

    return dataset[dataset["Stop"].isin(valid_fermate)]


# Get the stops
def getFermate(id: str, year: str, month: str):
    base_dir = "dataset/fermi/Fermate"

    dfs = []
    # dataset = getCleanDataset(f"{base_dir}/FERMATE {year}{month}.csv")
    for f in os.listdir(base_dir):
        if not f.startswith(f"FERMATE "):
            continue
        df = getCleanDataset(f"{base_dir}/{f}")

        # this automatically handles the "0101" -> "101" conversion as df["RESOURCE"].dtypes is int64
        df = df[df["RESOURCE"] == int(id)]
        # remove the resource column as it is the id we are already filtered it
        df.drop("RESOURCE", axis=1, inplace=True)
        dfs.append(df)

    if dfs == []:
        return pd.DataFrame()

    dataset = pd.concat(dfs, ignore_index=True)

    if dataset.empty:
        return dataset

    return prepareFermate(dataset)
