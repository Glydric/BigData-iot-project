from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

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
    "#880000",
]


def trace(fig: go.Figure, values, art: str, color: str):
    fig.add_trace(
        go.Scatter(
            name=art + "Energy",
            x=values["TIMESTAMP"],
            y=values["EnergyConsumption"],
            text=values["EnergyConsumption"],
            marker=dict(size=10, color=color),
            mode="markers+lines",
        ),
        col=1,
        row=1,
    )

    fig.add_trace(
        go.Scatter(
            name=art + " Productions",
            x=values["TIMESTAMP"],
            y=values["Productions"],
            text=values["Productions"],
            marker=dict(size=10, color=color),
            mode="markers+lines",
        ),
        col=1,
        row=2,
    )

    fig.add_trace(
        go.Scatter(
            name=art + " Stops",
            x=values["TIMESTAMP"],
            y=values["Fermate"],
            text=values["DESFERM"] if "DESFERM" in values.columns else None,
            marker=dict(size=10, color=color),
        ),
        col=1,
        row=3,
    )


def plot(df, id: int = None, year: int = None, month: int = None):
    count = 0

    fig = make_subplots(
        rows=3,
        cols=1,
        subplot_titles=["Energy Consumption", "Productions", "Stops"],
        shared_xaxes=True,
        vertical_spacing=0.06,
    )

    text = "Dataset"
    if id and year and month:
        text += f" machine {id} - {year}/{month}"

    fig.update_layout(height=800, width=1280, title_text=text)

    for art in df["COD_ART"].unique():
        color = "black" if art == "Unknown" else colors[count % len(colors)]
        values = df[df["COD_ART"] == art]

        trace(fig, values, art, color)

        count += 1

    fig.show()


if __name__ == "__main__":
    path = "./dataset/energy/location_Tormatic-channel_108-register_Ea_Imp_2022-08-10T00-00-00Z_2022-08-10T23-59-59Z.csv"

    plot(pd.read_csv(path))
