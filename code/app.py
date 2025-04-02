
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

import preprocess as preproc


app = dash.Dash(__name__)
app.title = 'Projet | INF8808'

app.layout = html.Div(
    className='row',
    children=[
        html.Div(
            className='Title',
            style={
                'justifyContent': 'center',
                'alignItems': 'center'
            },
            children=[
                html.H1(
                    "Titre de l'Application",
                    style={'fontSize': '32px', 'textAlign': 'center'}
                )
            ]
        )
    ]
)
