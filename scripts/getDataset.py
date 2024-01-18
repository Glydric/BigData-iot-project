import os
import pandas as pd


def getCleanDataset(file: str):
    df = pd.read_csv(file, delimiter=",")
    for c in df.columns:
        if df[c].dtype == "object":  # if it is a string
            df[c] = df[c].str.strip()
        df.rename(columns={c: c.strip()}, inplace=True)
    return df


# Get the stops
def getFermate(id: str, year: int, month: int):
    base_dir = "dataset/fermi/Fermate"

    df = getCleanDataset(f"{base_dir}/FERMATE {year}{month}.csv")
    # this automatically handles the "0101" -> "101" conversion as df["RESOURCE"].dtypes is int64
    # print(df["RESOURCE"].dtypes)
    data = df[df["RESOURCE"] == int(id)]
    print(data.head())

    if data.empty:
        raise Exception("Data not found")

    # remove the resource column as it is the id we are looking for
    data.drop("RESOURCE", axis=1, inplace=True)

    if data.empty:
        print("WARNING, Fermate was Empty")
    return data


# Get the productions
def getProductions(id: str, year: str, month: str, day: str):
    base_dir = "dataset/productions"

    dataset = pd.DataFrame()

    for f in os.listdir(f"{base_dir}"):
        if not f.startswith(f"Tormatic_20{year}{month}{day}"):
            continue

        df = getCleanDataset(f"{base_dir}/{f}")

        if "COD_PART" in df.columns:
            df = df[df["COD_PART"] == id]
            df.drop("COD_PART", axis=1, inplace=True)
        elif "COD_ART" in df.columns:
            df = df[df["COD_ART"] == id]
            df.drop("COD_ART", axis=1, inplace=True)
        else:
            print(df.head())
            raise Exception("Data not found - COD_ART or COD_PART not found")

        # We don't need to remove the followings as the filter already does it
        # data.drop(data.tail(1).index, inplace=True)
        # data.drop(0, inplace=True)
        dataset = pd.concat([dataset, df], ignore_index=True)

    if dataset.empty:
        print("WARNING, Productions was Empty")
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
    try:
        fermate = getFermate(id, year, month)
        productions = getProductions(id, year, month, day)
        energy = getEnergy(id, year, month, day)
        return pd.concat([energy, productions, fermate])
    except Exception as e:
        print(e)
        return None
    except e:
        print(e)
        return None


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

    allData = getEntireDataset("108", "22", "11", "05")
    print("allDataset\n")
    print(allData.head())
