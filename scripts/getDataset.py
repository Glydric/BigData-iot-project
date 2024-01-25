import os
import pandas as pd
from datetime import datetime


def productionFixComma(line: str):
    if line.count(",") == 8:
        return line.replace(",", ".", 3).replace(".", ",", 2).replace("\n", "")
    return line


def cleanDataset(df: pd.DataFrame):
    def f(x):
        # print(x)
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
        correctedFile = [productionFixComma(line) for line in file]

        head = correctedFile[0].split(",")

        correctedFile.remove(correctedFile[0])
        correctedFile.remove(correctedFile[1])

        data = [line.split(",") for line in correctedFile]
        df = pd.DataFrame(data)
        df.rename(columns={x: head[x] for x in range(0, len(head))}, inplace=True)
        return cleanDataset(df)


def prepareFermate(dataset: pd.DataFrame):
    # check if shift_date is the same as shift_start, shift_end, start_date, end_date
    assert (dataset["SHIFT_DATE"] == dataset["SHIFT_START"]).all()
    assert (dataset["SHIFT_START"] == dataset["SHIFT_END"]).all()
    assert (dataset["SHIFT_END"] == dataset["START_DATE"]).all()
    assert (dataset["START_DATE"] == dataset["END_DATE"]).all()
    dataset.drop(
        ["SHIFT_START", "SHIFT_END", "START_DATE", "END_DATE"], axis=1, inplace=True
    )

    # using date to determine the timestamp
    dataset.rename(columns={"SHIFT_DATE": "TIMESTAMP"}, inplace=True)
    dataset["TIMESTAMP"] = pd.to_datetime(dataset["TIMESTAMP"], format="%d-%b-%y")

    # duplicate the rows to prepare a row for each 15 minutes
    dataset = dataset.loc[dataset.index.repeat(96), :].reset_index(drop=True)

    idx_dup = dataset.duplicated(keep="first")

    # Update the timestamp
    i = 0

    def f(x):
        nonlocal i
        i += 1
        return x + i * pd.to_timedelta("15min")

    dataset.loc[idx_dup, "TIMESTAMP"] = dataset.loc[idx_dup, "TIMESTAMP"].apply(f)

    # print((df["SHIFT_CODE"] == 0).all())  # TODO checkWhy

    return dataset


# Get the stops
def getFermate(id: str, year: str, month: str, day: str):
    base_dir = "dataset/fermi/Fermate"

    dataset = getCleanDataset(f"{base_dir}/FERMATE {year}{month}.csv")
    # this automatically handles the "0101" -> "101" conversion as df["RESOURCE"].dtypes is int64
    dataset = dataset[dataset["RESOURCE"] == int(id)]

    dataset = dataset[dataset["SHIFT_DATE"].str.startswith(f"{day}")]  # TODO testme

    if dataset.empty:
        raise Exception("Data not found")

    # remove the resource column as it is the id we are looking for
    dataset.drop("RESOURCE", axis=1, inplace=True)

    if dataset.empty:
        return dataset

    return prepareFermate(dataset)


def prepareProductions(dataset: pd.DataFrame):
    dataset["TIMESTAMP_INIZIO"] = pd.to_datetime(dataset["TIMESTAMP_INIZIO"])
    dataset["TIMESTAMP_FINE"] = pd.to_datetime(dataset["TIMESTAMP_FINE"])
    dataset["NUMERO_PEZZI_PROD"] = pd.to_numeric(dataset["NUMERO_PEZZI_PROD"])

    dataset["TIMESTAMP"] = dataset[["TIMESTAMP_INIZIO", "TIMESTAMP_FINE"]].mean(axis=1)

    dataset.drop(["TIMESTAMP_INIZIO", "TIMESTAMP_FINE"], axis=1, inplace=True)

    def f(x: pd.Series):
        head = x.head(1)

        head["NUMERO_PEZZI_PROD"] = x["NUMERO_PEZZI_PROD"].to_numpy().sum()

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

    # print(dataset[dataset["ID"].str.startswith("5542100")].head())

    grouper = pd.Grouper(key="TIMESTAMP", freq="15T")
    dataset = dataset.groupby(grouper).apply(f)

    # Grouper used TIMESTAMP as index, here we convert to column
    dataset.drop("TIMESTAMP", axis=1, inplace=True)
    dataset = dataset.reset_index()

    dataset.drop("ID", axis=1, inplace=True)

    return dataset


# Get the productions
def getProductions(id: str, year: str, month: str, day: str):
    base_dir = "dataset/productions"

    dataset = pd.DataFrame()

    for f in os.listdir(f"{base_dir}"):
        if not f.startswith(f"Tormatic_20{year}{month}{day}"):
            continue
        # print(f"{base_dir}/{f}")

        df = getProductionWithFixedComma(f"{base_dir}/{f}")

        df.drop(0, inplace=True)

        df["COD_MACC"] = pd.to_numeric(df["COD_MACC"])
        df.dropna(inplace=True)
        df = df.astype({"COD_MACC": "int32"})

        df = df[df["COD_MACC"] == int(id)]

        dataset = pd.concat([dataset, df], ignore_index=True)

    if dataset.empty:
        return dataset

    return prepareProductions(dataset)


def prepareEnergy(dataset: pd.DataFrame):
    dataset.rename(columns={"TimeStamp": "TIMESTAMP"}, inplace=True)
    # Removes T and Z from the timestamp to not have problems with UTC and all formats are the same
    dataset["TIMESTAMP"] = dataset["TIMESTAMP"].apply(
        lambda x: x.replace("T", " ").replace("Z", "")
    )
    dataset["TIMESTAMP"] = pd.to_datetime(dataset["TIMESTAMP"])

    dataset.drop(["id"], axis=1, inplace=True)

    return dataset


# Get the energy consumption values
def getEnergy(id: str, year: str, month: str, day: str):
    base_dir = "dataset/energy"
    file = "location_Tormatic-channel_{}-register_Ea_Imp_20{}-{}-{}"

    dfs = []

    for f in os.listdir(f"{base_dir}"):
        if f.startswith(file.format(int(id), year, month, day)):
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
        df["TIMESTAMP"] = df["TIMESTAMP"].dt.round("15min")

        if dataset.empty:
            dataset = df
        else:
            assert dataset["TIMESTAMP"].dtype == df["TIMESTAMP"].dtype

            dataset = dataset.merge(df, on="TIMESTAMP", how="outer")

    return dataset


def getEntireDataset(id: int, year: str, month: str, day: str):
    fermate = getFermate(id, year, month, day)
    productions = getProductions(id, year, month, day)
    energy = getEnergy(id, year, month, day)
    # energy = getEnergy("310", "22", "08", "24")

    if fermate.empty:
        print("WARNING, Fermate was Empty")
    if productions.empty:
        print("WARNING, Productions was Empty")
    if energy.empty:
        print("WARNING, Energy was Empty")
    # merge1 = pd.merge(fermate, productions, on="TIMESTAMP", how="outer")
    # return pd.merge(merge1, energy, on="TIMESTAMP", how="outer")
    return mergeDataset([fermate, productions, energy])


def getAvailableMachines():
    """This gets the machine ids that have an energy file. Then for each ID it creates a disct with the years
    it spans and for each of them a set with the months. The format is like
    {
        '108': {
            '2022': (7, 8, 9, 10),
            '2023': (1,,2, 3, 4, 7, 8, 9, 10)
        },
        '302': {
            '2022': (7, 8, 9, 10),
            '2023': (1,,2, 3, 4, 7, 8, 9, 10)
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
    # productions = getProductions("211", "21", "12", "17")
    # print("prod\n")
    # print(productions.head())

    # fermate = getFermate("618", "22", "11")
    # print("fermate\n")
    # print(fermate.head())

    # energy = getEnergy("618", "22", "11", "04")
    # print("energy\n")
    # print(energy.head())

    # pd.merge(fermate, productions, on="TIMESTAMP", how="outer")
    pd.set_option("display.max_rows", None)

    # completeDataset = getEntireDataset("0105", "23", "05", "30")
    completeDataset = getEntireDataset("0301", "22", "11", "24")
    """
    machines = getAvailableMachines()

    for machineId in machines:
        for year in machines[machineId].keys():
            for month in machines[machineId][year]:
                completeDataset = getEntireDataset(machineId, year, month) 
    """

    try:
        print("\n----- Entire Dataset ------\n")
        # completeDataset = completeDataset.dropna()
        completeDataset["TIMESTAMP"] = completeDataset["TIMESTAMP"].dt.strftime(
            "%Y-%m-%d %H:%M"
        )
        # count = completeDataset[completeDataset.groupby("TIMESTAMP").count() > 1]
        # print(count)

        print(completeDataset.head())
    except Exception as e:
        print(e)
    except e:
        print(e)
