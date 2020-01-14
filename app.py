# -*- coding: utf-8 -*-
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

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)

server = app.server

PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()

# Loading historical tick data
currency_pair_data = {
    "EURUSD": pd.read_csv(
        DATA_PATH.joinpath("EURUSD.csv"), index_col=1, parse_dates=["Date"]
    ),
    "USDJPY": pd.read_csv(
        DATA_PATH.joinpath("USDJPY.csv"), index_col=1, parse_dates=["Date"]
    ),
    "GBPUSD": pd.read_csv(
        DATA_PATH.joinpath("GBPUSD.csv"), index_col=1, parse_dates=["Date"]
    ),
    "USDCHF": pd.read_csv(
        DATA_PATH.joinpath("USDCHF.csv"), index_col=1, parse_dates=["Date"]
    ),
}

# Currency pairs
currencies = ["EURUSD", "USDCHF", "USDJPY", "GBPUSD"]

# API Requests for news div
news_requests = requests.get(
    "https://newsapi.org/v2/top-headlines?sources=bbc-news&apiKey=da8e2e705b914f9f86ed2e9692e66012"
)

# API Call to update news
def update_news():
    json_data = news_requests.json()["articles"]
    df = pd.DataFrame(json_data)
    df = pd.DataFrame(df[["title", "url"]])
    max_rows = 10
    return html.Div(
        children=[
            html.P(className="p-news", children="Warnings"),
            html.P(
                className="p-news float-right",
                children="Last update : "
                + datetime.datetime.now().strftime("%H:%M:%S"),
            ),
            html.Table(
                className="table-news",
                children=[
                    html.Tr(
                        children=[
                            html.Td(
                                children=[
                                    html.A(
                                        className="td-link",
                                        children=df.iloc[i]["title"],
                                        href=df.iloc[i]["url"],
                                        target="_blank",
                                    )
                                ]
                            )
                        ]
                    )
                    for i in range(min(len(df), max_rows))
                ],
            ),
        ]
    )


# Returns dataset for currency pair with nearest datetime to current time
def first_ask_bid(currency_pair, t):
    t = t.replace(year=2016, month=1, day=5)
    items = currency_pair_data[currency_pair]
    dates = items.index.to_pydatetime()
    index = min(dates, key=lambda x: abs(x - t))
    df_row = items.loc[index]
    int_index = items.index.get_loc(index)
    return [df_row, int_index]  # returns dataset row and index of row


# Creates HTML Bid and Ask (Buy/Sell buttons)
def get_row(data):
    index = data[1]
    current_row = data[0]

    return html.Div(
        children=[
            # Summary
            html.Div(
                id=current_row[0] + "summary",
                className="row summary",
                n_clicks=0,
                children=[
                    html.Div(
                        id=current_row[0] + "row",
                        className="row",
                        children=[
                            html.P(
                                current_row[0],  # currency pair name
                                id=current_row[0],
                                className="three-col",
                            ),
                            html.P(
                                current_row[1].round(5),  # Bid value
                                id=current_row[0] + "bid",
                                className="three-col",
                            ),
                            html.P(
                                current_row[2].round(5),  # Ask value
                                id=current_row[0] + "ask",
                                className="three-col",
                            ),
                            html.Div(
                                index,
                                id=current_row[0]
                                + "index",  # we save index of row in hidden div
                                style={"display": "none"},
                            ),
                        ],
                    )
                ],
            ),
            # Contents
            html.Div(
                id=current_row[0] + "contents",
                className="row details",
                children=[
                    # Button for buy/sell modal
                    html.Div(
                        className="button-buy-sell-chart",
                        children=[
                            html.Button(
                                id=current_row[0] + "Buy",
                                children="Buy/Sell",
                                n_clicks=0,
                            )
                        ],
                    ),
                    # Button to display currency pair chart
                    html.Div(
                        className="button-buy-sell-chart-right",
                        children=[
                            html.Button(
                                id=current_row[0] + "Button_chart",
                                children="Chart",
                                n_clicks=1
                                if current_row[0] in ["EURUSD", "USDCHF"]
                                else 0,
                            )
                        ],
                    ),
                ],
            ),
        ]
    )


# color of Bid & Ask rates
def get_color(a, b):
    if a == b:
        return "white"
    elif a > b:
        return "#45df7e"
    else:
        return "#da5657"


# Replace ask_bid row for currency pair with colored values
def replace_row(currency_pair, index, bid, ask):
    index = index + 1  # index of new data row
    new_row = (
        currency_pair_data[currency_pair].iloc[index]
        if index != len(currency_pair_data[currency_pair])
        else first_ask_bid(currency_pair, datetime.datetime.now())
    )  # if not the end of the dataset we retrieve next dataset row
    return [
        html.P(
            currency_pair, id=currency_pair, className="three-col"  # currency pair name
        ),
        html.P(

            new_row[1].round(5),  # Bid value
            id=new_row[0] + "bid",
            className="three-col",
            style={"color": get_color(new_row[1], bid)},
        ),
        html.P(
            new_row[2].round(5),  # Ask value
            className="three-col",
            id=new_row[0] + "ask",
            style={"color": get_color(new_row[2], ask)},
        ),
        html.Div(
            index, id=currency_pair + "index", style={"display": "none"}
        ),  # save index in hidden div
    ]


# Display big numbers in readable format
def human_format(num):
    try:
        num = float(num)
        # If value is 0
        if num == 0:
            return 0
        # Else value is a number
        if num < 1000000:
            return num
        magnitude = int(math.log(num, 1000))
        mantissa = str(int(num / (1000 ** magnitude)))
        return mantissa + ["", "K", "M", "G", "T", "P"][magnitude]
    except:
        return num


# Returns Top cell bar for header area
def get_top_bar_cell(cellTitle, cellValue):
    return html.Div(
        className="two-col",
        children=[
            html.P(className="p-top-bar", children=cellTitle),
            html.P(id=cellTitle, className="display-none", children=cellValue),
            html.P(children=human_format(cellValue)),
        ],
    )


# Returns HTML Top Bar for app layout
def get_top_bar(
    balance=50000, equity=50000, margin=0, fm=50000, m_level="%", open_pl=0
):
    return [
        get_top_bar_cell("Balance", balance),
        get_top_bar_cell("Equity", equity),
        get_top_bar_cell("Margin", margin),
        get_top_bar_cell("Free Margin", fm),
        get_top_bar_cell("Margin Level", m_level),
        get_top_bar_cell("Open P/L", open_pl),
    ]


####### STUDIES TRACES ######

# Moving average
def moving_average_trace(df, fig):
    df2 = df.rolling(window=5).mean()
    trace = go.Scatter(
        x=df2.index, y=df2["close"], mode="lines", showlegend=False, name="MA"
    )
    fig.append_trace(trace, 1, 1)  # plot in first row
    return fig


# Exponential moving average
def e_moving_average_trace(df, fig):
    df2 = df.rolling(window=20).mean()
    trace = go.Scatter(
        x=df2.index, y=df2["close"], mode="lines", showlegend=False, name="EMA"
    )
    fig.append_trace(trace, 1, 1)  # plot in first row
    return fig


# Bollinger Bands
def bollinger_trace(df, fig, window_size=10, num_of_std=5):
    price = df["close"]
    rolling_mean = price.rolling(window=window_size).mean()
    rolling_std = price.rolling(window=window_size).std()
    upper_band = rolling_mean + (rolling_std * num_of_std)
    lower_band = rolling_mean - (rolling_std * num_of_std)

    trace = go.Scatter(
        x=df.index, y=upper_band, mode="lines", showlegend=False, name="BB_upper"
    )

    trace2 = go.Scatter(
        x=df.index, y=rolling_mean, mode="lines", showlegend=False, name="BB_mean"
    )

    trace3 = go.Scatter(
        x=df.index, y=lower_band, mode="lines", showlegend=False, name="BB_lower"
    )

    fig.append_trace(trace, 1, 1)  # plot in first row
    fig.append_trace(trace2, 1, 1)  # plot in first row
    fig.append_trace(trace3, 1, 1)  # plot in first row
    return fig


# Accumulation Distribution
def accumulation_trace(df):
    df["volume"] = ((df["close"] - df["low"]) - (df["high"] - df["close"])) / (
        df["high"] - df["low"]
    )
    trace = go.Scatter(
        x=df.index, y=df["volume"], mode="lines", showlegend=False, name="Accumulation"
    )
    return trace


# Commodity Channel Index
def cci_trace(df, ndays=5):
    TP = (df["high"] + df["low"] + df["close"]) / 3
    CCI = pd.Series(
        (TP - TP.rolling(window=10, center=False).mean())
        / (0.015 * TP.rolling(window=10, center=False).std()),
        name="cci",
    )
    trace = go.Scatter(x=df.index, y=CCI, mode="lines", showlegend=False, name="CCI")
    return trace


# Price Rate of Change
def roc_trace(df, ndays=5):
    N = df["close"].diff(ndays)
    D = df["close"].shift(ndays)
    ROC = pd.Series(N / D, name="roc")
    trace = go.Scatter(x=df.index, y=ROC, mode="lines", showlegend=False, name="ROC")
    return trace


# Stochastic oscillator %K
def stoc_trace(df):
    SOk = pd.Series((df["close"] - df["low"]) / (df["high"] - df["low"]), name="SO%k")
    trace = go.Scatter(x=df.index, y=SOk, mode="lines", showlegend=False, name="SO%k")
    return trace


# Momentum
def mom_trace(df, n=5):
    M = pd.Series(df["close"].diff(n), name="Momentum_" + str(n))
    trace = go.Scatter(x=df.index, y=M, mode="lines", showlegend=False, name="MOM")
    return trace


# Pivot points
def pp_trace(df, fig):
    PP = pd.Series((df["high"] + df["low"] + df["close"]) / 3)
    R1 = pd.Series(2 * PP - df["low"])
    S1 = pd.Series(2 * PP - df["high"])
    R2 = pd.Series(PP + df["high"] - df["low"])
    S2 = pd.Series(PP - df["high"] + df["low"])
    R3 = pd.Series(df["high"] + 2 * (PP - df["low"]))
    S3 = pd.Series(df["low"] - 2 * (df["high"] - PP))
    trace = go.Scatter(x=df.index, y=PP, mode="lines", showlegend=False, name="PP")
    trace1 = go.Scatter(x=df.index, y=R1, mode="lines", showlegend=False, name="R1")
    trace2 = go.Scatter(x=df.index, y=S1, mode="lines", showlegend=False, name="S1")
    trace3 = go.Scatter(x=df.index, y=R2, mode="lines", showlegend=False, name="R2")
    trace4 = go.Scatter(x=df.index, y=S2, mode="lines", showlegend=False, name="S2")
    trace5 = go.Scatter(x=df.index, y=R3, mode="lines", showlegend=False, name="R3")
    trace6 = go.Scatter(x=df.index, y=S3, mode="lines", showlegend=False, name="S3")
    fig.append_trace(trace, 1, 1)
    fig.append_trace(trace1, 1, 1)
    fig.append_trace(trace2, 1, 1)
    fig.append_trace(trace3, 1, 1)
    fig.append_trace(trace4, 1, 1)
    fig.append_trace(trace5, 1, 1)
    fig.append_trace(trace6, 1, 1)
    return fig


## MAIN CHART TRACES (STYLE tab)
def line_trace(df):
    trace = go.Scatter(
        x=df.index, y=df["close"], mode="lines", showlegend=False, name="line"
    )
    return trace


def area_trace(df):
    trace = go.Scatter(
        x=df.index, y=df["close"], showlegend=False, fill="toself", name="area"
    )
    return trace


def bar_trace(df):
    return go.Ohlc(
        x=df.index,
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        increasing=dict(line=dict(color="#888888")),
        decreasing=dict(line=dict(color="#888888")),
        showlegend=False,
        name="bar",
    )


def colored_bar_trace(df):
    return go.Ohlc(
        x=df.index,
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        showlegend=False,
        name="colored bar",
    )


def candlestick_trace(df):
    return go.Candlestick(
        x=df.index,
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        increasing=dict(line=dict(color="#00ff00")),
        decreasing=dict(line=dict(color="white")),
        showlegend=False,
        name="candlestick",
    )


# For buy/sell modal
def ask_modal_trace(currency_pair, index):
    df = currency_pair_data[currency_pair].iloc[index - 10 : index]  # returns ten rows
    return go.Scatter(x=df.index, y=df["Ask"], mode="lines", showlegend=False)


# For buy/sell modal
def bid_modal_trace(currency_pair, index):
    df = currency_pair_data[currency_pair].iloc[index - 10 : index]  # returns ten rows
    return go.Scatter(x=df.index, y=df["Bid"], mode="lines", showlegend=False)


# returns modal figure for a currency pair
def get_modal_fig(currency_pair, index):
    fig = tools.make_subplots(
        rows=2, shared_xaxes=True, shared_yaxes=False, cols=1, print_grid=False
    )

    fig.append_trace(ask_modal_trace(currency_pair, index), 1, 1)
    fig.append_trace(bid_modal_trace(currency_pair, index), 2, 1)

    fig["layout"]["autosize"] = True
    fig["layout"]["height"] = 375
    fig["layout"]["margin"] = {"t": 5, "l": 50, "b": 0, "r": 5}
    fig["layout"]["yaxis"]["showgrid"] = True
    fig["layout"]["yaxis"]["gridcolor"] = "#3E3F40"
    fig["layout"]["yaxis"]["gridwidth"] = 1
    fig["layout"].update(paper_bgcolor="#21252C", plot_bgcolor="#21252C")

    return fig


# Returns graph figure
def get_fig(currency_pair, ask, bid, type_trace, studies, period):
    # Get OHLC data
    data_frame = currency_pair_data[currency_pair]
    t = datetime.datetime.now()
    data = data_frame.loc[
        : t.strftime(
            "2016-01-05 %H:%M:%S"
        )  # all the data from the beginning until current time
    ]
    data_bid = data["Bid"]
    df = data_bid.resample(period).ohlc()

    subplot_traces = [  # first row traces
        "accumulation_trace",
        "cci_trace",
        "roc_trace",
        "stoc_trace",
        "mom_trace",
    ]
    selected_subplots_studies = []
    selected_first_row_studies = []
    row = 1  # number of subplots

    if studies:
        for study in studies:
            if study in subplot_traces:
                row += 1  # increment number of rows only if the study needs a subplot
                selected_subplots_studies.append(study)
            else:
                selected_first_row_studies.append(study)

    fig = tools.make_subplots(
        rows=row,
        shared_xaxes=True,
        shared_yaxes=True,
        cols=1,
        print_grid=False,
        vertical_spacing=0.12,
    )

    # Add main trace (style) to figure
    fig.append_trace(eval(type_trace)(df), 1, 1)

    # Add trace(s) on fig's first row
    for study in selected_first_row_studies:
        fig = eval(study)(df, fig)

    row = 1
    # Plot trace on new row
    for study in selected_subplots_studies:
        row += 1
        fig.append_trace(eval(study)(df), row, 1)

    fig["layout"][
        "uirevision"
    ] = "The User is always right"  # Ensures zoom on graph is the same on update
    fig["layout"]["margin"] = {"t": 50, "l": 50, "b": 50, "r": 25}
    fig["layout"]["autosize"] = True
    fig["layout"]["height"] = 400
    fig["layout"]["xaxis"]["rangeslider"]["visible"] = False
    fig["layout"]["xaxis"]["tickformat"] = "%H:%M"
    fig["layout"]["yaxis"]["showgrid"] = True
    fig["layout"]["yaxis"]["gridcolor"] = "#3E3F40"
    fig["layout"]["yaxis"]["gridwidth"] = 1
    fig["layout"].update(paper_bgcolor="#21252C", plot_bgcolor="#21252C")

    return fig


# returns chart div
def chart_div(pair):
    return html.Div(
        id=pair + "graph_div",
        className="display-none",
        children=[
            # Menu for Currency Graph
            html.Div(
                id=pair + "menu",
                className="not_visible",
                children=[
                    # stores current menu tab
                    html.Div(
                        id=pair + "menu_tab",
                        children=["Studies"],
                        style={"display": "none"},
                    ),
                    html.Span(
                        "Style",
                        id=pair + "style_header",
                        className="span-menu",
                        n_clicks_timestamp=2,
                    ),
                    html.Span(
                        "Studies",
                        id=pair + "studies_header",
                        className="span-menu",
                        n_clicks_timestamp=1,
                    ),
                    # Studies Checklist
                    html.Div(
                        id=pair + "studies_tab",
                        children=[
                            dcc.Checklist(
                                id=pair + "studies",
                                options=[
                                    {
                                        "label": "Accumulation/D",
                                        "value": "accumulation_trace",
                                    },
                                    {
                                        "label": "Bollinger bands",
                                        "value": "bollinger_trace",
                                    },
                                    {"label": "MA", "value": "moving_average_trace"},
                                    {"label": "EMA", "value": "e_moving_average_trace"},
                                    {"label": "CCI", "value": "cci_trace"},
                                    {"label": "ROC", "value": "roc_trace"},
                                    {"label": "Pivot points", "value": "pp_trace"},
                                    {
                                        "label": "Stochastic oscillator",
                                        "value": "stoc_trace",
                                    },
                                    {
                                        "label": "Momentum indicator",
                                        "value": "mom_trace",
                                    },
                                ],
                                value=[],
                            )
                        ],
                        style={"display": "none"},
                    ),
                    # Styles checklist
                    html.Div(
                        id=pair + "style_tab",
                        children=[
                            dcc.RadioItems(
                                id=pair + "chart_type",
                                options=[
                                    {
                                        "label": "candlestick",
                                        "value": "candlestick_trace",
                                    },
                                    {"label": "line", "value": "line_trace"},
                                    {"label": "mountain", "value": "area_trace"},
                                    {"label": "bar", "value": "bar_trace"},
                                    {
                                        "label": "colored bar",
                                        "value": "colored_bar_trace",
                                    },
                                ],
                                value="colored_bar_trace",
                            )
                        ],
                    ),
                ],
            ),
            # Chart Top Bar
            html.Div(
                className="row chart-top-bar",
                children=[
                    html.Span(
                        id=pair + "menu_button",
                        className="inline-block chart-title",
                        children="".join(pair),
                        n_clicks=0,
                    ),
                    # Dropdown and close button float right
                    html.Div(
                        className="graph-top-right inline-block",
                        children=[
                            html.Div(
                                className="inline-block",
                                children=[
                                    dcc.Dropdown(
                                        className="dropdown-period",
                                        id=pair + "dropdown_period",
                                        options=[
                                            {"label": "5 min", "value": "5Min"},
                                            {"label": "15 min", "value": "15Min"},
                                            {"label": "30 min", "value": "30Min"},
                                        ],
                                        value="15Min",
                                        clearable=False,
                                    )
                                ],
                            ),
                            html.Span(
                                id=pair + "close",
                                className="chart-close inline-block float-right",
                                children="×",
                                n_clicks=0,
                            ),
                        ],
                    ),
                ],
            ),
            # Graph div
            html.Div(
                dcc.Graph(
                    id=pair + "chart",
                    className="chart-graph",
                    config={"displayModeBar": False, "scrollZoom": True},
                )
            ),
        ],
    )


# returns modal Buy/Sell
def modal(pair):
    return html.Div(
        id=pair + "modal",
        className="modal",
        style={"display": "none"},
        children=[
            html.Div(
                className="modal-content",
                children=[
                    html.Span(
                        id=pair + "closeModal", className="modal-close", children="×"
                    ),
                    html.P(id="modal" + pair, children=pair),
                    # row div with two div
                    html.Div(
                        className="row",
                        children=[
                            # graph div
                            html.Div(
                                className="six columns",
                                children=[
                                    dcc.Graph(
                                        id=pair + "modal_graph",
                                        config={"displayModeBar": False},
                                    )
                                ],
                            ),
                            # order values div
                            html.Div(
                                className="six columns modal-user-control",
                                children=[
                                    html.Div(
                                        children=[
                                            html.P("Volume"),
                                            dcc.Input(
                                                id=pair + "volume",
                                                className="modal-input",
                                                type="number",
                                                value=0.1,
                                                min=0,
                                                step=0.1,
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        children=[
                                            html.P("Type"),
                                            dcc.RadioItems(
                                                id=pair + "trade_type",
                                                options=[
                                                    {"label": "Buy", "value": "buy"},
                                                    {"label": "Sell", "value": "sell"},
                                                ],
                                                value="buy",
                                                labelStyle={"display": "inline-block"},
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        children=[
                                            html.P("SL TPS"),
                                            dcc.Input(
                                                id=pair + "SL",
                                                type="number",
                                                min=0,
                                                step=1,
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        children=[
                                            html.P("TP TPS"),
                                            dcc.Input(
                                                id=pair + "TP",
                                                type="number",
                                                min=0,
                                                step=1,
                                            ),
                                        ]
                                    ),
                                ],
                            ),
                        ],
                    ),
                    html.Div(
                        className="modal-order-btn",
                        children=html.Button(
                            "Order", id=pair + "button_order", n_clicks=0
                        ),
                    ),
                ],
            )
        ],
    )


# Dash App Layout
app.layout = html.Div(
    className="row",
    children=[
        # Interval component for live clock
        dcc.Interval(id="interval", interval=1 * 1000, n_intervals=0),
        # Interval component for ask bid updates
        dcc.Interval(id="i_bis", interval=5 * 1000, n_intervals=0),
        # Interval component for graph updates
        dcc.Interval(id="i_tris", interval=5 * 1000, n_intervals=0),
        # Interval component for graph updates
        dcc.Interval(id="i_news", interval=1 * 60000, n_intervals=0),
        # Left Panel Div
        html.Div(
            className="three columns div-left-panel",
            children=[
                # Div for Left Panel App Info
                html.Div(
                    className="div-info",
                    children=[
                        html.P(
                            """
                            MCP-Web
                            """
                        ),
                        html.H6(className="title-header", children="MCP-Web"),
                        html.P(
                            """
                            This app continually queries csv files and updates MCP charts with the provided data.
                            The app also serves a view of predictions over the previous MCP data.
                            """
                        ),
                    ],
                ),
                # Ask Bid Currency Div
                html.Div(
                    className="div-currency-toggles",
                    children=[
                        html.P(
                            id="live_clock",
                            className="three-col",
                            children=datetime.datetime.now().strftime("%H:%M:%S"),
                        ),
                        html.P(className="three-col", children="Bid"),
                        html.P(className="three-col", children="Ask"),
                        html.Div(
                            id="pairs",
                            className="div-bid-ask",
                            children=[
                                get_row(first_ask_bid(pair, datetime.datetime.now()))
                                for pair in currencies
                            ],
                        ),
                    ],
                ),
                # Div for News Headlines
                html.Div(
                    className="div-news",
                    children=[html.Div(id="news", children=update_news())],
                ),
            ],
        ),
        # Right Panel Div
        html.Div(
            className="nine columns div-right-panel",
            children=[

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
                                selected_className='custom-tab--selected'
                            ),
                            dcc.Tab(
                                label='IM',
                                value='tab-2',
                                className='custom-tab',
                                selected_className='custom-tab--selected'
                            ),
                            dcc.Tab(
                                label='Flow',
                                value='tab-3',
                                className='custom-tab',
                                selected_className='custom-tab--selected'
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

                    )]),
                    html.Div(style={'display': 'inline-block'}, children=[
                    html.Label(" Ending Hour "),
                    dcc.Input(
                        id="end_hour",
                        type="number",
                        min=0,
                        max=24,
                        placeholder="24"
                    )]),
                    html.Div(style={'display': 'inline-block'}, children=[
                    html.Label(" Forecast Horizon(Days) "),
                    dcc.Input(
                        id="number_horizon",
                        type="number",
                        min=1,
                        max=10,
                        placeholder="1"
                    )]),

                    html.Div(style={'display': 'inline-block'}, children=[
                        html.Label("     "),
                        html.Button('Apply', id='apply-button'),
                    ]),
                ]),
            html.Br(),
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
            ],
        ),
        # Hidden div that stores all clicked charts (EURUSD, USDCHF, etc.)
        html.Div(id="charts_clicked", style={"display": "none"}),
        # Hidden div for each pair that stores orders
        html.Div(
            children=[
                html.Div(id=pair + "orders", style={"display": "none"})
                for pair in currencies
            ]
        ),
        html.Div([modal(pair) for pair in currencies]),
        # Hidden Div that stores all orders
        html.Div(id="orders", style={"display": "none"}),
    ],
)

# Dynamic Callbacks

# Replace currency pair row
def generate_ask_bid_row_callback(pair):
    def output_callback(n, i, bid, ask):
        return replace_row(pair, int(i), float(bid), float(ask))

    return output_callback


# returns string containing clicked charts
def generate_chart_button_callback():
    def chart_button_callback(*args):
        pairs = ""
        for i in range(len(currencies)):
            if args[i] > 0:
                pair = currencies[i]
                if pairs:
                    pairs = pairs + "," + pair
                else:
                    pairs = pair
        return pairs

    return chart_button_callback


# Function to update Graph Figure
def generate_figure_callback(pair):
    def chart_fig_callback(n_i, p, t, s, pairs, a, b, old_fig):

        if pairs is None:
            return {"layout": {}, "data": {}}

        pairs = pairs.split(",")
        if pair not in pairs:
            return {"layout": {}, "data": []}

        if old_fig is None or old_fig == {"layout": {}, "data": {}}:
            return get_fig(pair, a, b, t, s, p)

        fig = get_fig(pair, a, b, t, s, p)
        return fig

    return chart_fig_callback


# Function to close currency pair graph
def generate_close_graph_callback():
    def close_callback(n, n2):
        if n == 0:
            if n2 == 1:
                return 1
            return 0
        return 0

    return close_callback


# Function to open or close STYLE or STUDIES menu
def generate_open_close_menu_callback():
    def open_close_menu(n, className):
        if n == 0:
            return "not_visible"
        if className == "visible":
            return "not_visible"
        else:
            return "visible"

    return open_close_menu


# Function for hidden div that stores the last clicked menu tab
# Also updates style and studies menu headers
def generate_active_menu_tab_callback():
    def update_current_tab_name(n_style, n_studies):
        if n_style >= n_studies:
            return "Style", "span-menu selected", "span-menu"
        return "Studies", "span-menu", "span-menu selected"

    return update_current_tab_name


# Function show or hide studies menu for chart
def generate_studies_content_tab_callback():
    def studies_tab(current_tab):
        if current_tab == "Studies":
            return {"display": "block", "textAlign": "left", "marginTop": "30"}
        return {"display": "none"}

    return studies_tab


# Function show or hide style menu for chart
def generate_style_content_tab_callback():
    def style_tab(current_tab):
        if current_tab == "Style":
            return {"display": "block", "textAlign": "left", "marginTop": "30"}
        return {"display": "none"}

    return style_tab


# Open Modal
def generate_modal_open_callback():
    def open_modal(n):
        if n > 0:
            return {"display": "block"}
        else:
            return {"display": "none"}

    return open_modal


# Function to close modal
def generate_modal_close_callback():
    def close_modal(n, n2):
        return 0

    return close_modal


# Function for modal graph - set modal SL value to none
def generate_clean_sl_callback():
    def clean_sl(n):
        return 0

    return clean_sl


# Function for modal graph - set modal SL value to none
def generate_clean_tp_callback():
    def clean_tp(n):
        return 0

    return clean_tp


# Function to create figure for Buy/Sell Modal
def generate_modal_figure_callback(pair):
    def figure_modal(index, n, old_fig):
        if (n == 0 and old_fig is None) or n == 1:
            return get_modal_fig(pair, index)
        return old_fig  # avoid to compute new figure when the modal is hidden

    return figure_modal


# Resize pair div according to the number of charts displayed
def generate_show_hide_graph_div_callback(pair):
    def show_graph_div_callback(charts_clicked):
        if pair not in charts_clicked:
            return "display-none"

        charts_clicked = charts_clicked.split(",")  # [:4] max of 4 graph
        len_list = len(charts_clicked)

        classes = "chart-style"
        if len_list % 2 == 0:
            classes = classes + " six columns"
        elif len_list == 3:
            classes = classes + " four columns"
        else:
            classes = classes + " twelve columns"
        return classes

    return show_graph_div_callback


# Generate Buy/Sell and Chart Buttons for Left Panel
def generate_contents_for_left_panel():
    def show_contents(n_clicks):
        if n_clicks is None:
            return "display-none", "row summary"
        elif n_clicks % 2 == 0:
            return "display-none", "row summary"
        return "row details", "row summary-open"

    return show_contents


# Loop through all currencies
for pair in currencies:

    # Callback for Buy/Sell and Chart Buttons for Left Panel
    app.callback(
        [Output(pair + "contents", "className"), Output(pair + "summary", "className")],
        [Input(pair + "summary", "n_clicks")],
    )(generate_contents_for_left_panel())


    # updates the ask and bid prices
    app.callback(
        Output(pair + "row", "children"),
        [Input("i_bis", "n_intervals")],
        [
            State(pair + "index", "children"),
            State(pair + "bid", "children"),
            State(pair + "ask", "children"),
        ],
    )(generate_ask_bid_row_callback(pair))


# Callback to update live clock
@app.callback(Output("live_clock", "children"), [Input("interval", "n_intervals")])
def update_time(n):
    return datetime.datetime.now().strftime("%H:%M:%S")


# Callback to update news
@app.callback(Output("news", "children"), [Input("i_news", "n_intervals")])
def update_news_div(n):
    return update_news()

def interpret(n, begin_hour, end_hour, number_horizon, begin_date, end_date):
    print(begin_hour, end_hour, number_horizon, begin_date, end_date)

    #connect i/o -> make sure you are updating the main graph - left side
    create_csv(12,12,12,12)



@app.callback(Output("Charts-general", 'children'), [Input('tabs-with-classes', 'value'), Input('apply-button', 'n_clicks')], [
        State('begin_hour', 'value'), State('end_hour', 'value'), State('number_horizon', 'value'), State('begin_date', 'date'), State('end_date', 'date')    ])
def render_content(tab, n, begin_hour, end_hour, number_horizon, begin_date, end_date):
    print(tab)
    if tab == 'tab-1':

        nms = [begin_date, end_date, begin_hour, end_hour]

        f = open('filters.csv', 'w')

        with f:

            writer = csv.writer(f)
            writer.writerow(nms)

        create_csv(begin_date, end_date, begin_hour, end_hour)
        df = pd.read_csv('trace_tl.csv')

        fig = make_subplots(rows=1, cols=1, shared_yaxes=True, shared_xaxes=True)

        fig.add_trace(
            go.Scatter(x=df['Date'], y=df['TL'], name="MCP-TL", line_color='deepskyblue'),

            row=1, col=1
        )
        fig.update_layout(
            title="MCP Data w/Forecast",
            xaxis_title="Dates",
            yaxis_title="TL Price",
            font=dict(
                family="Courier New, monospace",
                size=14,
                color="#7f7f7f"
            ),
          )

        fig["layout"].update(paper_bgcolor="#21252C", plot_bgcolor="#21252C")

        df2 = pd.read_csv('forecast.csv')
        df3 = pd.read_csv('forecast_lower.csv')
        df4 = pd.read_csv('forecast_upper.csv')

        fig.add_trace(
            go.Scatter(x=df2['Date'], y=df2['TL'], name="Mean"),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=df3['Date'], y=df3['TL'], name="Lower Bound"),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=df4['Date'], y=df4['TL'], name="Upper Bound"),
            row=1, col=1
        )


        fig.update_xaxes(showgrid=False, zeroline=False)
        fig.update_yaxes(showgrid=False, zeroline=False)
        fig.update_xaxes(showgrid=False, zeroline=False, col=1)
        fig.update_yaxes(showgrid=False, zeroline=False, col=1)



        return [
            html.Div(
                dcc.Graph(id="Stock Chart", figure=fig)
            ),
        ]

    elif tab == 'tab-2':
        return html.Div([
            html.H3('Tab content 2')
        ])
    elif tab == 'tab-3':
        return html.Div([
            html.H3('Tab content 3')
        ])


def create_csv(begin_date, end_date, begin_hour, end_hour):
    os.system("python3 create_csv_traces.py")

if __name__ == "__main__":
    app.run_server(debug=True)
