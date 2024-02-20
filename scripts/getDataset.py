import os
import pandas as pd
from datetime import datetime
from plots import plot


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

    # TODO check why the following data is always the same
    if dataset["SHIFT_CODE"].diff(0).all():
        print("WARNING, you are dropping SHIFT_CODE that is not always the same")
        print(dataset["SHIFT_CODE"])

    if (dataset["STAGE"] != 10).all():
        print("WARNING, you are dropping STAGE that is not always the same")
        print(dataset["STAGE"])

    if (dataset["STOP_CODE"] != 2).all():
        print("WARNING, you are dropping STOP_CODE that is not always the same")
        print(dataset["STOP_CODE"])

    if (dataset["QTY_SCRAP"] != 0).all():
        print("WARNING, you are dropping QTY_SCRAP that is not always the same")
        print(dataset["QTY_SCRAP"])

    if (dataset["QTY_GOOD"] != 0).all():
        print("WARNING, you are dropping QTY_GOOD that is not always the same")
        print(dataset["QTY_GOOD"])

    dataset = dataset.groupby(["TIMESTAMP"]).count().reset_index()

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
            "DESFERM",
        ],
        axis=1,
        inplace=True,
    )

    return dataset


# Get the stops
# TODO check if works
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

    # completeDataset = completeDataset.dropna()

    return dataset


def getEntireDataset(id: int, year_int: int, month_int: int):
    year = str(year_int)[slice(2, 4)]
    month = f"{month_int:02d}"

    print("__Getting Fermate__")
    fermate = getFermate(id, year, month)
    if fermate.empty:
        print("WARNING, Fermate was Empty")
    else:
        assert "TIMESTAMP" in fermate.columns

    print("__Getting Productions__")
    productions = getProductions(id, year, month)
    if productions.empty:
        print("WARNING, Productions was Empty")
    else:
        assert "TIMESTAMP" in productions.columns

    print("__Getting Enegy Consumption__")
    energy = getEnergy(id, year, month)
    if energy.empty:
        print("WARNING, Energy was Empty")
    else:
        assert "TIMESTAMP" in energy.columns

    return mergeDataset([fermate, productions, energy])

def getAvailableMachines():
    base_dir = "dataset/energy"
    date_format = "%Y-%m-%dT%H-%M-%SZ"

    idsList = set()
    machines = {}

    for f in os.listdir(base_dir):
        if "location_Tormatic" not in f:
            continue
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

    id = "0301"
    try:

        machines = getAvailableMachines()
        dfs = []
        errors = []
        # try:
        #     print(getEntireDataset(306, 2022, 7))
        # except Exception as e:
        #     errors.append(e)

        for machineId in machines:
            for year in machines[machineId].keys():
                for month in machines[machineId][year]:
                    print(
                        f"\n\n----- Machine {machineId} Year {year} Month {month} ------"
                    )
                    try:
                        df = getEntireDataset(machineId, year, month)
                        plot(df, machineId)
                        
                        df["ID"] = machineId
                        dfs.append(df)
                    except Exception as e:
                        print(f"Error {e}")
                        errors.append(e)
                        errors.append(
                            {
                                "machineId": machineId,
                                "year": year,
                                "month": month,
                                "error": e,
                            }
                        )

        if errors != []:
            print(errors)
        completeDataset = pd.concat(dfs, ignore_index=True)

        print(f"\n----- Entire Dataset {id} ------\n")

        print(completeDataset)
        print(completeDataset.shape)
        plot(completeDataset)

    except Exception as e:
        print(e)
