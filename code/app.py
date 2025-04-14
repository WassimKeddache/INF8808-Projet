
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

from components.description import get_description
from components.header import get_header
from components.heatmap_budget.heatmap_budget import get_heatmap_budget
from components.countries_chart.countries_chart import get_countries_chart
from components.matrix_diagram.matrix_diagram import get_matrix_diagram
from components.entities_chart.entities_chart import get_entities_chart

#import preprocess as preproc
header = get_header()
heatmap_budget = get_heatmap_budget()

app = dash.Dash(__name__)
app.title = 'Projet | INF8808'

app.layout = html.Div(
    className='app-container',
    children=[
        html.Header(
            className='main-header',
            children=[
                get_header()
            ]
        ),
        html.Main(
            className='main-content',
            children=[
                get_description(),
                get_matrix_diagram(),
                get_heatmap_budget(),
                get_countries_chart(),
                get_entities_chart(),
            ]
        ),
        html.Footer(
            className='main-header',
            children=[
                html.P("© ...")
            ]
        )
    ]
)