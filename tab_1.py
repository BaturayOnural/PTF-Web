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
    'backgroundColor': '#21252C',
    'color': '#b2b2b2',
    'padding': '5px'
}

# Right Panel Div
tab_1_layout =   [
                html.Div(
                    id='tabs', children=[
                    dcc.Tabs(
                        id='tabs-with-classes',
                        value='tab-1',
                        parent_className='custom-tabs',
                        className='custom-tabs-container',
                        children=[
                            dcc.Tab(
                                label='DAM',
                                value='tab-1',
                                className='custom-tab',
                                selected_className='custom-tab--selected',
                            style=tab_style, selected_style=tab_selected_style

                            ),
                            dcc.Tab(
                                label='IM',
                                value='tab-2',
                                className='custom-tab',
                                selected_className='custom-tab--selected',
                            style=tab_style, selected_style=tab_selected_style
                            ),
                            dcc.Tab(
                                label='Flow',
                                value='tab-3',
                                className='custom-tab',
                                selected_className='custom-tab--selected',
                            style=tab_style, selected_style=tab_selected_style
                            ),

                        ]
                     )]


                ),

                html.Div(style={'text-align': 'Center'} , children=[
                html.Br(),
                html.Div(style={'display': 'inline-block'}, children=[
                    html.Div(style={'display': 'inline-block'}, children= [
                        html.Label("Start Date "),
                        dcc.DatePickerSingle(id="begin_date", placeholder=datetime.datetime.now().date()),
                    ]),
                    html.Div(style={'display': 'inline-block'}, children=[
                        html.Label(" End Date "),
                        dcc.DatePickerSingle(id="end_date", placeholder=datetime.datetime.now().date()),
                    ]),
                    html.Div(style={'display': 'inline-block'}, children=[
                    html.Label(" Beginning Hour "),
                    dcc.Input(
                        id="begin_hour",
                        type="number",
                        min = 0,
                        max = 24,
                        placeholder="0",
                        value=0,

                    )]),
                    html.Div(style={'display': 'inline-block'}, children=[
                    html.Label(" Ending Hour "),
                    dcc.Input(
                        id="end_hour",
                        type="number",
                        min=0,
                        max=24,
                        placeholder="24",
                        value=24,
                    )]),
                    html.Div(style={'display': 'inline-block'}, children=[
                        html.Label("     "),
                        html.Button('Apply Filtering', id='apply-button'),
                    ]),
                    html.Br(),
                    html.Br(),

                    html.Div(children=[
                        html.Label(" Forecast Horizon(Days) "),
                        dcc.Input(
                            id="number_horizon",
                            type="number",
                            min=1,
                            max=10,
                            placeholder="1"
                        )], style={'display': 'inline-block'}),
                    html.Div(style={'display': 'inline-block'}, children=[
                        html.Label("     "),
                        html.Button('Apply Forecasting', id='apply-button-forecast'),
                            ]),
                    html.Div( children=[
                        html.Div(children=[
                            html.Label(" Total # Hours "),
                            dcc.Input(
                                id="number_total",
                                type="number",
                                min=1,
                                max=10,
                                placeholder="1"
                            )], style={'display': 'inline-block', 'margin-left':'20px'}),
                        html.Div(children=[
                            html.Label(" Preferred Hours "),
                            dcc.Input(
                                id="pref_hours",
                                type="text",
                                placeholder="11-17"
                            )], style={'display': 'inline-block'}),
                        html.Div( children=[
                             html.Label("     "),
                            html.Button('Suggest Operating Period', id='apply-button2'),
                        ],style={'display': 'inline-block'} ),
                    ], style={'display': 'inline-block'}),




                ]),
            html.Br(),





            html.Br(),]),
            html.Div(
                # Charts Div
                id="Charts-general", children=[
                    html.Div(
                        id="charts",
                        className="row",

                    )

                ]
            ),
            html.Br(),
            html.Br(),
    html.Div(style={'text-align': 'Center'}, children=[
        html.Div(
            id="SOP",
            children=[

            ],
            style={'display': 'inline-table', 'text-align': 'center'}

        ),

        html.Div(
            id="SOP2",
            children=[

            ],
            style={'display': 'inline-table', 'text-align': 'center'}

        ),
    ])]

