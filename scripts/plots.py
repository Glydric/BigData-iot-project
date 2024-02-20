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

def plot(df, id: int = None):

    times = df["TIMESTAMP"]

    fig = make_subplots(rows=3, cols=1, subplot_titles=['Energy Consumption', 'Productions', 'Stops'], shared_xaxes=True, vertical_spacing=0.06)
    fig.append_trace(
        go.Scatter(
            x=times,
            y=df["EnergyConsumption"],
            name="Energy Consumption",
            marker=dict(size=10),
        ),
        row=1,
        col=1,
    )
    fig.append_trace(
        go.Scatter(
            x=times, y=df["Productions"], name="Production", marker=dict(size=10)
        ),
        row=2,
        col=1,
    )
    fig.append_trace(
        go.Scatter(
            x=times, y=df["Fermate"], name="Stops", marker=dict(size=10)
        ),
        row=3,
        col=1,
    )

    fig.update_traces(mode="markers+lines")
    
    text = f"Dataset macchine {id}" if id else "Dataset"
    fig.update_layout(height=800, width=1280, title_text=text)
    fig.show()

if __name__ == "__main__":
    path = "./dataset/energy/location_Tormatic-channel_108-register_Ea_Imp_2022-08-10T00-00-00Z_2022-08-10T23-59-59Z.csv"

    plot(pd.read_csv(path))