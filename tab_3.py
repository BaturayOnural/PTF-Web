import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import csv
import json
import base64
import datetime
import requests
import pathlib
import math
import pandas as pd
import flask
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly as py
import plotly.graph_objs as go
import plotly.express as px

from dash.dependencies import Input, Output, State
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from plotly import tools
from plotly.graph_objs.layout import yaxis, xaxis
from plotly.subplots import make_subplots
import os
import dash_table

tabs_styles = {
    'height': '40px'
}
tab_style = {
    'borderBottom': '0px solid #d6d6d6',
    'padding': '5px',
    'fontWeight': 'bold'
}

tab_selected_style = {
    'borderTop': '0px solid #d6d6d6',
    'borderBottom': '0px solid #d6d6d6',
    'backgroundColor': '#94a8a8',
    'color': 'white',
    'padding': '5px'
}

df = pd.read_csv('planning.csv')
# Right Panel Div
tab_3_layout =   [
                html.Div(style={'margin-left':'100px'}, children = [
                        html.Br(),
                html.Br(),
                html.Br(),
                html.Br(),
                dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i} for i in df.columns],
    data=df.to_dict("rows"),
    editable=True,
    row_selectable='single',
    style_header={'backgroundColor': '#94a8a8'},
    style_cell={
        'backgroundColor': 'white',
        'color': '#7f7f7f',
        'font_family': 'Open Sans',
        'font_size': '25px',
        'text_align': 'center',

    }
    ),
    html.Div(id="tab3-but-div", children=[
                            html.Label("     "),
                    html.Br(),
                    html.Button('Solve', id='solve-button', style={'font-size':'14px'}),
                    html.Div(style={'display': 'inline-block', 'margin-left':'615px'}, children=[
                    html.Label("   Bid Price "),
                    dcc.Input(
                        id="bid_price",
                        type="number",
                        min=0,
                        max=24,
                        placeholder="0",
                        value=0,
                    )]),
                    html.Div(style={'display': 'inline-block'}, children=[
                    html.Label("   DAM vs IM(%) "),
                    dcc.Input(
                        id="vs",
                        type="number",
                        min=0,
                        max=100,
                        placeholder="0",
                        value=0,
                    )]),

                    html.Button('Generate Bid Matrix', id='generate-bid-button', style={'font-size':'14px'})]
        , style={'display':'inline-block'})

                
                ]
                )
                ]

