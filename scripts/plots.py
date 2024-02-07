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

path = './dataset/energy/location_Tormatic-channel_108-register_Ea_Imp_2022-08-10T00-00-00Z_2022-08-10T23-59-59Z.csv'
df = pd.read_csv(path)

times = df["TimeStamp"]
energy = df["Ea_Imp"]

fig = make_subplots(rows=3, cols=1, subplot_titles=['Energy Consumption', 'Production', 'Stops'], shared_xaxes=True, vertical_spacing=0.06)
fig.append_trace(
    go.Scatter(x=times, y=energy, name='Energy consumption', marker=dict(size=10)),
    row=1, col=1
)
fig.append_trace(
    go.Scatter(x=times, y=energy, name='Production', marker=dict(size=10)),
    row=2, col=1
)
fig.append_trace(
    go.Scatter(x=times, y=energy, name='Stops', marker=dict(size=10)),
    row=3, col=1
)

fig.update_traces(mode="markers+lines")
fig.update_layout(height=800, width=1700, title_text=f"Machine 108 - {date.strftime('%B, %Y')}")
fig.show()