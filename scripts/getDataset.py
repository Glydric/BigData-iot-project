import os
import numpy as np
import pandas as pd


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


def customResampler(df: pd.DataFrame):
    print(df.head())
    if df.dtypes == "object":
        return df.to_numpy()
    return np.sum(df)


# Get the stops
def getFermate(id: str, year: str, month: str, day: str):
    base_dir = "dataset/fermi/Fermate"

    df = getCleanDataset(f"{base_dir}/FERMATE {year}{month}.csv")
    # this automatically handles the "0101" -> "101" conversion as df["RESOURCE"].dtypes is int64
    df = df[df["RESOURCE"] == int(id)]

    df = df[df["SHIFT_DATE"].str.startswith(f"{day}")]  # TODO testme

    if df.empty:
        raise Exception("Data not found")

    # remove the resource column as it is the id we are looking for
    df.drop("RESOURCE", axis=1, inplace=True)

    if df.empty:
        print("WARNING, Fermate was Empty")

    # check if shift_date is the same as shift_start, shift_end, start_date, end_date
    assert (df["SHIFT_DATE"] == df["SHIFT_START"]).all()
    assert (df["SHIFT_START"] == df["SHIFT_END"]).all()
    assert (df["SHIFT_END"] == df["START_DATE"]).all()
    assert (df["START_DATE"] == df["END_DATE"]).all()
    df.drop(
        ["SHIFT_START", "SHIFT_END", "START_DATE", "END_DATE"], axis=1, inplace=True
    )

    # using date to determine the timestamp
    df.rename(columns={"SHIFT_DATE": "TIMESTAMP"}, inplace=True)
    df["TIMESTAMP"] = pd.to_datetime(df["TIMESTAMP"], format="%d-%b-%y")

    # duplicate the rows to prepare a row for each 15 minutes
    df = df.loc[df.index.repeat(96), :].reset_index(drop=True)

    idx_dup = df.duplicated(keep="first")

    # Update the timestamp
    i = 0

    def f(x):
        nonlocal i
        i += 1
        return x + i * pd.to_timedelta("15min")

    df.loc[idx_dup, "TIMESTAMP"] = df.loc[idx_dup, "TIMESTAMP"].apply(f)

    print((df["SHIFT_CODE"] == 0).all())  # TODO checkWhy

    return df


# Get the productions
def getProductions(id: str, year: str, month: str, day: str):
    base_dir = "dataset/productions"

    dataset = pd.DataFrame()

    for f in os.listdir(f"{base_dir}"):
        if not f.startswith(f"Tormatic_20{year}{month}{day}"):
            continue
        # print(f"{base_dir}/{f}")

        df = getProductionWithFixedComma(f"{base_dir}/{f}")

        if "COD_PART" in df.columns:
            df = df[df["COD_PART"] == id]
            df.drop("COD_PART", axis=1, inplace=True)
        elif "COD_ART" in df.columns:
            df = df[df["COD_ART"] == id]
            df.drop("COD_ART", axis=1, inplace=True)
        else:
            print(df.head())
            raise Exception("Data not found - COD_ART or COD_PART not found")

        # print(df.head())
        # We don't need to remove the followings as the filter already does it
        # data.drop(data.tail(1).index, inplace=True)
        # data.drop(0, inplace=True)
        dataset = pd.concat([dataset, df], ignore_index=True)

    if dataset.empty:
        print("WARNING, Productions was Empty")

    # dataset = dataset.resample("15T", on="TIMESTAMP_INIZIO").sum()  # FIXME
    # print(dataset.head())
    # DatetimeIndex, TimedeltaIndex or PeriodIndex

    return dataset


# Get the energies
def getEnergy(id: str, year: str, month: str, day: str):
    base_dir = "dataset/energy"

    dataset = pd.DataFrame()

    for f in os.listdir(f"{base_dir}"):
        if not f.startswith(
            f"location_Tormatic-channel_{id}-register_Ea_Imp_20{year}-{month}-{day}"
        ):
            continue

        df = getCleanDataset(f"{base_dir}/{f}")

        dataset = pd.concat([dataset, df], ignore_index=True)

    if dataset.empty:
        print("WARNING, Energy was Empty")
    return dataset


def getEntireDataset(id: int, year: str, month: str, day: str):
    fermate = getFermate(id, year, month, day)
    # print(fermate.head())
    productions = getProductions(id, year, month, day)
    # print(productions.empty)
    energy = getEnergy(id, year, month, day)
    # print(energy.empty)

    assert "TIMESTAMP" in fermate.columns
    assert "TIMESTAMP" in productions.columns
    assert "TIMESTAMP" in energy.columns

    merge1 = pd.merge(fermate, productions, on="TIMESTAMP", how="outer")
    return pd.merge(merge1, energy, on="TIMESTAMP", how="outer")


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

    allData = getEntireDataset("301", "23", "05", "30")
    try:
        print("allDataset\n")
        print(allData.head())
    except Exception as e:
        print(e)
    except e:
        print(e)
