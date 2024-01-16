import os
import pandas as pd

def getCleanDataset(file: str):
    df = pd.read_csv(file, delimiter=",")
    for c in df.columns:
        if df[c].dtype == "object": # if it is a string
            df[c] = df[c].str.strip()
        df.rename(columns={c: c.strip()}, inplace=True)
    return df


# Get the list of stops
def getFermate(cod_part: int, year: int, month: int):
    base_dir = "dataset/fermi/Fermate"

    df = getCleanDataset(f"{base_dir}/FERMATE {year}{month}.csv")
    data = df[df["RESOURCE"] == cod_part]

    return data


# Get the list of stops
def getProductions(cod_part: str, year: int, month: int, day: int):
    base_dir = "dataset/productions"

    master = pd.DataFrame()

    for f in os.listdir(f"{base_dir}"):
        if not f.startswith(f"Tormatic_20{year}{month}{day}"):
            continue

        df = getCleanDataset(f"{base_dir}/{f}")

        data = df[df["COD_PART"] == cod_part]
        # data.drop(data.tail(1).index, inplace=True)
        # data.drop(0, inplace=True)
        master = pd.concat([master, data], ignore_index=True)

    return master


if __name__ == "__main__":
    productions = getProductions("211", 21, 12, 17)
    fermate = getFermate(101, 22, 11)
    print(productions.head())
    print(fermate.head())

    # print(getLineNum(reader))
    # fermate = list(reader)
