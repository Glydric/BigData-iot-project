import os
import pandas as pd
from datetime import datetime


def productionFixComma(line: str, columns: int):
    newline = line.replace("\n", "")

    if line.count(",") == columns:
        newline = newline.replace(",", ".", 3).replace(".", ",", 2)

    return newline


def cleanDataset(df: pd.DataFrame):
    def f(x: str):
        # print(df.columns)
        return x.strip()

    for c in df.columns:
        if df[c].dtype == "object":  # if it is a string
            df[c] = df[c].str.strip()
        df.rename(columns={c: f(c)}, inplace=True)
    return df


def getCleanDataset(file: str):
    df = pd.read_csv(file, delimiter=",")
    return cleanDataset(df)


def getProductionWithFixedComma(name: str):
    with open(name) as file:
        lines = file.readlines()

        head = lines[0].split(",")

        correctedFile = [productionFixComma(line, len(head)) for line in lines]

        correctedFile.remove(correctedFile[0])
        correctedFile.remove(correctedFile[1])

        lines_data = [line.split(",") for line in correctedFile]

        df = pd.DataFrame(lines_data)
        df.rename(columns={x: head[x] for x in range(0, len(head))}, inplace=True)

        return cleanDataset(df)


def prepareFermate(dataset: pd.DataFrame):
    # check if shift_date is the same as shift_start, shift_end, start_date, end_date
    assert (dataset["SHIFT_DATE"] == dataset["SHIFT_START"]).all()
    assert (dataset["SHIFT_START"] == dataset["SHIFT_END"]).all()
    assert (dataset["SHIFT_END"] == dataset["START_DATE"]).all()
    assert (dataset["START_DATE"] == dataset["END_DATE"]).all()
    dataset.drop(
        ["SHIFT_DATE", "SHIFT_START", "SHIFT_END", "START_DATE", "END_DATE"],
        axis=1,
        inplace=True,
    )

    return dataset


# Get the stops
def getFermate(id: str, year: str, month: str):
    base_dir = "dataset/fermi/Fermate"

    dataset = getCleanDataset(f"{base_dir}/FERMATE {year}{month}.csv")
    # this automatically handles the "0101" -> "101" conversion as df["RESOURCE"].dtypes is int64
    dataset = dataset[dataset["RESOURCE"] == int(id)]

    # remove the resource column as it is the id we are looking for
    dataset.drop("RESOURCE", axis=1, inplace=True)

    if dataset.empty:
        raise Exception("Data not found")

    if dataset.empty:
        return dataset

    dataset["TIMESTAMP"] = pd.to_datetime(dataset["SHIFT_DATE"], format="%d-%b-%y")

    dataset = dataset[dataset["TIMESTAMP"].dt.strftime("%y-%m") == f"{year}-{month}"]

    return prepareFermate(dataset)


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

        # LOGS
        # if (
        #     x["TIMESTAMP"]
        #     .dt.strftime("%Y-%m-%d %H")
        #     .str.startswith("2023-03-31 08")
        #     .any()
        # ):
        #     print(x)
        #     print(head["NUMERO_PEZZI_PROD"])

        return head

    grouper = pd.Grouper(key="TIMESTAMP", freq="1D")
    dataset = dataset.groupby(grouper).apply(f, include_groups=False)

    # Grouper used TIMESTAMP as index, here we convert to column
    dataset = dataset.reset_index()

    dataset.drop("ID", axis=1, inplace=True)

    return dataset


# Get the productions
def getProductions(id: str, year: str, month: str):
    base_dir = "dataset/productions"

    dfs = []

    for f in os.listdir(f"{base_dir}"):
        if not f.startswith(f"Tormatic_20{year}{month}"):
            continue

        df = getProductionWithFixedComma(f"{base_dir}/{f}")

        df.drop(0, inplace=True)

        df["COD_MACC"] = pd.to_numeric(df["COD_MACC"])
        df.dropna(inplace=True)
        df = df.astype({"COD_MACC": "int32"})

        df = df[df["COD_MACC"] == int(id)]

        dfs.append(df)

    if dfs == []:
        return pd.DataFrame()

    dataset = pd.concat(dfs, ignore_index=True)

    if dataset.empty:
        return dataset

    return prepareProductions(dataset, year, month)


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

    return dataset


def getEntireDataset(id: int, year: str, month: str):
    fermate = getFermate(id, year, month)
    productions = getProductions(id, year, month)
    energy = getEnergy(id, year, month)
    # energy = getEnergy("310", "22", "08", "24")

    if fermate.empty:  # FIXME fix date
        print("WARNING, Fermate was Empty")
    if productions.empty:  # FIXME fix date
        print("WARNING, Productions was Empty")
    if energy.empty:
        print("WARNING, Energy was Empty")

    assert "TIMESTAMP" in fermate.columns
    assert "TIMESTAMP" in productions.columns
    assert "TIMESTAMP" in energy.columns

    # print(fermate.dropna())
    # print(productions.dropna())
    # print(energy.dropna())
    return mergeDataset([fermate, productions, energy])


def getAvailableMachines():
    """This gets the machine ids that have an energy file. Then for each ID it creates a disct with the years
    it spans and for each of them a set with the months. The format is like
    {
        '108': {
            '2022': (7, 8, 9, 10),
            '2023': (1, 2, 3, 4, 7, 8, 9, 10)
        },
        '302': {
            '2022': (7, 8, 9, 10),
            '2023': (1, 2, 3, 4, 7, 8, 9, 10)
        }
    }
    """
    base_dir = "dataset/energy"
    idsList = set()
    date_format = "%Y-%m-%dT%H-%M-%SZ"
    machines = {}

    for f in os.listdir(base_dir):
        if "location_Tormatic" in f:
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

    # completeDataset = getEntireDataset("0105", "23", "05")
    id = "0301"
    completeDataset = getEntireDataset("0301", "23", "05")

    # machines = getAvailableMachines()

    # for machineId in machines:
    #     for year in machines[machineId].keys():
    #         for month in machines[machineId][year]:
    #             completeDataset = getEntireDataset(machineId, year, month)

    # print(getFermate(id, "22", "11"))
    try:
        print(f"\n----- Entire Dataset {id} ------\n")
        completeDataset = completeDataset.dropna()

        if (completeDataset["COD_MACC"] == 301).all():
            completeDataset.drop("COD_MACC", axis=1, inplace=True)

        # TODO check why the following data is always the same
        if (completeDataset["SHIFT_CODE"] == 0).all():
            completeDataset.drop("SHIFT_CODE", axis=1, inplace=True)

        if (completeDataset["STAGE"] == 10).all():
            completeDataset.drop("STAGE", axis=1, inplace=True)

        if (completeDataset["STOP_CODE"] == 2).all():
            completeDataset.drop("STOP_CODE", axis=1, inplace=True)

        if (completeDataset["QTY_SCRAP"] == 0).all():
            completeDataset.drop("QTY_SCRAP", axis=1, inplace=True)

        if (completeDataset["QTY_GOOD"] == 0).all():
            completeDataset.drop("QTY_GOOD", axis=1, inplace=True)

        # assert (completeDataset["QTY_SCRAP"] == 0).all()

        print(completeDataset)
        print(completeDataset.shape)

    except Exception as e:
        print(e)
