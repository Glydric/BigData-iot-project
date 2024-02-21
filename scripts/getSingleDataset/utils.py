import pandas as pd


def cleanDataset(df: pd.DataFrame):
    def f(x: str):
        # print(df.columns)
        return x.strip()

    for c in df.columns:
        if df[c].dtype == "object":  # if it is a string
            df[c] = df[c].str.strip()
        df.rename(columns={c: f(c)}, inplace=True)
    return df


def getCleanDataset(file: str, dtypes = None):
    df = pd.read_csv(file, delimiter=",", dtype=dtypes)
    return cleanDataset(df)
