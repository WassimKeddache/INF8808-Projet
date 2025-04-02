
# -*- coding: utf-8 -*-

'''
    File name: app.py
    Author: Olivia Gélinas
    Course: INF8808
    Python Version: 3.8

    This file contains the source code for TP5.
'''
import json

import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State

import plotly.graph_objects as go

from components.header import get_header
from components.heatmap_budget import get_heatmap_budget

#import preprocess as preproc
header = get_header()
heatmap_budget = get_heatmap_budget()

app = dash.Dash(__name__)
app.title = 'Projet | INF8808'

app.layout = html.Div(
    className='column',
    children=[
        html.Header(
            children=[
                header
            ]
        ),
        html.Main(
            children=[
                heatmap_budget
            ]
        )

    ]
)
