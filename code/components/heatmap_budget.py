import dash
from dash import html, dcc, callback
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime
import numpy as np
from data import data_instance

def get_heatmap_budget():
    return html.Div(className='content', children=[
    html.Div(className='viz-container', children=[
        # Conteneur pour les deux heatmaps
        html.Div(className='heatmaps-container', style={'display': 'flex'}, children=[
            # Heatmap de gauche (budget)
            html.Div(className='heatmap-left', style={'width': '50%'}, children=[
                html.H3('Budget moyen par genre et année'),
                dcc.Graph(id='budget-heatmap')
            ]),
            
            # Heatmap de droite (métrique sélectionnable)
            html.Div(className='heatmap-right', style={'width': '50%'}, children=[
                html.H3('Métrique par genre et année'),
                dcc.Graph(id='metric-heatmap')
            ])
        ]),
        
        # Div pour afficher les informations de survol combinées
        html.Div(id='hover-info', style={
            'padding': '10px',
            'backgroundColor': '#f9f9f9',
            'border': '1px solid #ddd',
            'borderRadius': '5px',
            'marginTop': '10px',
            'minHeight': '50px',
            'display': 'none'  # Caché par défaut
        }),
        
        # Contrôles (seulement le sélecteur de métrique, pas de slider)
        html.Div(className='controls', children=[
            # Sélecteur de métrique pour la heatmap de droite
            html.Div(className='metric-selector', children=[
                html.Label('Sélectionner une métrique:'),
                dcc.RadioItems(
                    id='metric-selector',
                    options=[
                        {'label': 'Revenu moyen', 'value': 'revenue'},
                        {'label': 'Vote moyen', 'value': 'vote_average'}
                    ],
                    value='revenue',
                    labelStyle={'display': 'inline-block', 'margin-right': '20px'}
                )
            ])
        ]),
        
        # Store pour stocker les données des heatmaps
        dcc.Store(id='heatmap-data-store')
    ])
])

# Callback pour mettre à jour les deux heatmaps en fonction du sélecteur de métrique
@callback(
    [Output('budget-heatmap', 'figure'),
     Output('metric-heatmap', 'figure')],
    [Input('metric-selector', 'value')]
)
def update_heatmaps(selected_metric):
    # Utiliser toutes les données depuis 1970, par année
    data = data_instance.get_heatmap_data()
    
    all_genre_names = data['all_genre_names']
    budget_min_avg = data['budget_min_avg']
    budget_max_avg = data['budget_max_avg']
    metric_ranges = data['metric_ranges']
    years = data['years']

    budget_df = data['budget_df']
    revenue_df = data['revenue_df']
    vote_df = data['vote_df']

    # Calculer les moyennes par genre et année
    budget_df = budget_df
    metric_df = vote_df if selected_metric == 'vote_average' else revenue_df
    
    # Définir les années à afficher (tous les 5 ans)
    tick_years = [year for year in years if (year - 1970) % 5 == 0]
    
    # Définir l'ordre des genres (identique pour les deux heatmaps)
    genre_order = all_genre_names
    
    # Créer la heatmap pour le budget
    budget_fig = go.Figure(data=go.Heatmap(
        z=budget_df['budget'],
        x=budget_df['release_date'],
        y=budget_df['genre'],
        colorscale='Reds',
        zmin=budget_min_avg,
        zmax=budget_max_avg,
        customdata=np.stack((
            budget_df['genre'],
            budget_df['release_date'],
            budget_df['budget'],
            metric_df[selected_metric]
        ), axis=-1),
        hoverinfo='none',  # Désactiver l'info-bulle par défaut
        hovertemplate=None
    ))
    
    # Modification pour s'assurer que tous les genres sont affichés
    budget_fig.update_layout(
        title='Budget moyen par genre (depuis 1970, par année)',
        xaxis=dict(
            title='Année',
            tickmode='array',
            tickvals=tick_years,
            ticktext=[str(year) for year in tick_years],
            tickangle=90
        ),
        yaxis=dict(
            title='Genre',
            categoryorder='array',
            categoryarray=genre_order,  # Utiliser l'ordre défini
            showticklabels=True,
            # Assurer que tous les labels sont affichés
            tickmode='array',
            tickvals=list(range(len(genre_order))),
            ticktext=genre_order
        ),
        coloraxis_colorbar=dict(
            title='Budget moyen (USD)'
        ),
        margin=dict(l=150, r=50, t=80, b=100)  # Augmenter la marge gauche pour les labels
    )
    
    # Créer la heatmap pour la métrique sélectionnée
    metric_labels = {
        'revenue': 'Revenu moyen (USD)',
        'vote_average': 'Vote moyen'
    }
    
    # Utiliser les échelles de couleur standard
    color_scales = {
        'revenue': 'Blues',
        'vote_average': 'Greens'
    }
    
    metric_fig = go.Figure(data=go.Heatmap(
        z=metric_df[selected_metric],
        x=metric_df['release_date'],
        y=metric_df['genre'],
        colorscale=color_scales[selected_metric],
        zmin=metric_ranges[selected_metric][0],
        zmax=metric_ranges[selected_metric][1],
        customdata=np.stack((
            metric_df['genre'],
            metric_df['release_date'],
            budget_df['budget'],
            metric_df[selected_metric]
        ), axis=-1),
        hoverinfo='none',  # Désactiver l'info-bulle par défaut
        hovertemplate=None
    ))
    
    metric_fig.update_layout(
        title=f'{metric_labels[selected_metric]} par genre (depuis 1970, par année)',
        xaxis=dict(
            title='Année',
            tickmode='array',
            tickvals=tick_years,
            ticktext=[str(year) for year in tick_years],
            tickangle=90
        ),
        yaxis=dict(
            title='',
            categoryorder='array',
            categoryarray=genre_order,  # Utiliser le même ordre que pour le budget
            showticklabels=False  # Garder à False pour ne pas afficher les labels
        ),
        coloraxis_colorbar=dict(
            title=metric_labels[selected_metric]
        ),
        margin=dict(l=0, r=50, t=80, b=100)
    )
    
    return budget_fig, metric_fig

# Callback pour mettre à jour les informations de survol
@callback(
    [Output('hover-info', 'children'),
     Output('hover-info', 'style')],
    [Input('budget-heatmap', 'hoverData'),
     Input('metric-heatmap', 'hoverData')],
    [State('metric-selector', 'value'),
     State('hover-info', 'style')]
)
def update_hover_info(budget_hover, metric_hover, selected_metric, current_style):
    # Déterminer quel graphique a déclenché le callback
    ctx = dash.callback_context
    if not ctx.triggered:
        # Si aucun déclencheur, cacher le div
        current_style['display'] = 'none'
        return "", current_style
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Obtenir les données de survol
    if trigger_id == 'budget-heatmap' and budget_hover:
        hover_data = budget_hover['points'][0]
    elif trigger_id == 'metric-heatmap' and metric_hover:
        hover_data = metric_hover['points'][0]
    else:
        # Si pas de données de survol, cacher le div
        current_style['display'] = 'none'
        return "", current_style
    
    # Extraire les données personnalisées
    genre = hover_data['customdata'][0]
    year = int(hover_data['customdata'][1])
    budget = hover_data['customdata'][2]
    metric_value = hover_data['customdata'][3]
    
    # Créer le contenu HTML pour afficher les informations
    metric_labels = {
        'revenue': 'Revenu moyen',
        'vote_average': 'Vote moyen'
    }
    
    hover_info = html.Div([
        html.H4(f"Genre: {genre}, Année: {year}"),
        html.Div([
            html.Div([
                html.Strong("Budget moyen: "),
                html.Span(f"{budget:,.2f} USD")
            ]),
            html.Div([
                html.Strong(f"{metric_labels[selected_metric]}: "),
                html.Span(f"{metric_value:,.2f}" + (" USD" if selected_metric == 'revenue' else ""))
            ])
        ])
    ])
    
    # Afficher le div
    current_style['display'] = 'block'
    
    return hover_info, current_style