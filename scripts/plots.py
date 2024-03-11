from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import plotly.express as px


""" path = '0301 2022-11.csv'
df = pd.read_csv(path)
df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'])

dates = df['TIMESTAMP'].apply(lambda x: x.strftime('%Y-%m-%d')).unique()

print(dates)
date = '2022-11-21'

times = df.loc[df['TIMESTAMP'].apply(lambda x: x.strftime('%Y-%m-%d')) == date]['TIMESTAMP']
energy= df[df['TIMESTAMP'].apply(lambda x: x.strftime('%Y-%m-%d')) == date]['EnergyConsumption']

print(times.head())
print(energy.head()) """


colors = [
    "blue",
    "green",
    "#FF0000",
    "#00FFFF",
    "#FFFF00",
    "#000088",
    "#008800",
    "#880000",
    "#000044",
    "#004400",
    "#440000",
]


def trace(fig: go.Figure, df: pd.DataFrame, tag: str, color: str):
    fig.add_trace(
        go.Scatter(
            name=tag + " Energy",
            x=df["TIMESTAMP"],
            y=df["EnergyConsumption"],
            text=df["EnergyConsumption"],
            marker=dict(size=10, color=color),
            mode="markers+lines",
        ),
        col=1,
        row=1,
    )

    fig.add_trace(
        go.Scatter(
            name=tag + " Productions",
            x=df["TIMESTAMP"],
            y=df["Productions"],
            text=df["Productions"],
            marker=dict(size=10, color=color),
            mode="markers+lines",
        ),
        col=1,
        row=3,
    )

    fig.add_trace(
        go.Scatter(
            name=tag + " Stops",
            x=df["TIMESTAMP"],
            y=df["Stop"],
            text=df["DESFERM"] if "DESFERM" in df.columns else None,
            marker=dict(size=10, color=color),
            mode="markers",
        ),
        col=1,
        row=2,
    )


def correlation_plot(df: pd.DataFrame, id: int = None):
    text = "Dataset"
    if id:
        text += f" machine {id}"

    df.drop(df[df["Productions"] <= 0].index, inplace=True)
    df.drop(df[df["EnergyConsumption"] <= 0].index, inplace=True)

    fig = go.Figure()
    fig.update_layout(height=600, width=600, title_text=text)

    fig.update_xaxes(title_text="Productions")
    fig.update_yaxes(title_text="Energy Consumption")

    count = 0
    for mat in df["Material"].unique():
        color = "black" if mat == "Unknown" else colors[count % len(colors)]
        values = df[df["Material"] == mat]

        count += 1

        fig.add_trace(
            go.Scatter(
                name=mat,
                text=str(mat),
                x=values["Productions"],
                y=values["EnergyConsumption"],
                marker=dict(size=2, color=color),
                mode="markers",
            )
        )
    fig.show()


def plot(df: pd.DataFrame, id: int = None, year: int = None, month: int = None):
    count = 0

    df["START_DATE"] = pd.to_datetime(df["START_DATE"])
    df["END_DATE"] = pd.to_datetime(df["END_DATE"])
    df["TIMESTAMP"] = df[["START_DATE", "END_DATE"]].mean(axis=1)

    fig = make_subplots(
        rows=3,
        cols=1,
        subplot_titles=["Energy Consumption", "Stops", "Productions"],
        shared_xaxes=True,
        vertical_spacing=0.06,
    )

    text = "Dataset"
    if id:
        text += f" machine {id}"
    if year and month:
        text += f" - {year}/{month}"

    fig.update_layout(height=800, width=1280, title_text=text)

    for mat in df["Material"].unique():
        color = "black" if mat == "Unknown" else colors[count % len(colors)]
        values = df[df["Material"] == mat]

        trace(fig, values, str(mat), color)

        count += 1

    correlation_plot(fig, df)

    fig.show()


if __name__ == "__main__":
    path = "./dataset/energy/location_Tormatic-channel_108-register_Ea_Imp_2022-08-10T00-00-00Z_2022-08-10T23-59-59Z.csv"

    plot(pd.read_csv(path))
