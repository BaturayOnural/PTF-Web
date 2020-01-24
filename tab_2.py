
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import dash
import dash_table
import pandas as pd

df = pd.read_csv('plants1.csv')
df2 = pd.read_csv('plants2.csv')
df3= pd.read_csv('plants3.csv')

tab_2_layout = [
                html.Div( children = [
                html.H3("DAM"),
                html.Div(
                dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i} for i in df.columns],
    data=df.to_dict("rows"),
    editable=True,
    style_header={'backgroundColor': 'rgb(30,30,30)'},
    style_cell={
            'backgroundColor': 'rgb(50, 50, 50)',
            'color': 'white',
            'text_align': 'center',
            'font_size':'25px'

    }
), style={'margin-left':'85px'}

                    ),
html.H3("WIND"),
html.Div(
dash_table.DataTable(
    id='table2',
    columns=[{"name": i, "id": i} for i in df2.columns],
    data=df2.to_dict("rows"),
    editable=True,
    style_header={'backgroundColor': 'rgb(30, 30, 30)'},
    style_cell={
            'backgroundColor': 'rgb(50, 50, 50)',
            'color': 'white',
            'text_align': 'center',
            'font_size':'25px'

    }
), style={'margin-left':'305px'}

    )
,
html.H3("SOLAR"),
html.Div(
dash_table.DataTable(
    id='table3',
    columns=[{"name": i, "id": i} for i in df3.columns],
    data=df3.to_dict("rows"),
    editable=True,
    style_header={'backgroundColor': '#94a8a8'},
    style_cell={
        'backgroundColor': 'white',
        'color': '#7f7f7f',
        'font_family': 'Open Sans',
        'font_size': '25px',
        'text_align': 'center',

    }
), style={'margin-left':'355px'}
    )

], style={  'padding': '70px 0', 'text-align': 'center', 'margin-top':'-50px'})]
                

