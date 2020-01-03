import pandas as pd
import plotly.express as px

df = pd.read_csv('PTF-03012020.csv')

fig = px.line(df, x = 'Saat', y = 'PTF (TL/MWh)', title='MCP Visualization')
fig.show()
