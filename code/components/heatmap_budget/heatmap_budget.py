import dash
from dash import html, dcc, callback
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime
import numpy as np
from .heatmap_budget_data import data_instance

def get_heatmap_budget():
    return html.Div(className='content', children=[
        html.Div(className='dashboard-card', children=[
            # Main content
            html.Div(className='card-content', children=[
                # Conteneur pour les deux heatmaps - toujours côte à côte
                html.Div(className='heatmaps-container', children=[
                    # Heatmap de gauche (budget)
                    dcc.Graph(
                        id='budget-heatmap',
                        config={'displayModeBar': False},
                        className='heatmap-graph'
                    ),
                    
                    # Heatmap de droite (métrique sélectionnable)
                    dcc.Graph(
                        id='metric-heatmap',
                        config={'displayModeBar': False},
                        className='heatmap-graph'
                    )
                ]),
                
                # Rangée avec le choix de métrique à gauche et hover info centré
                html.Div(className='controls-and-info-row', children=[
                    # Choix de métrique à gauche
                    html.Div(id='hover-info'),
                    # Hover info centré
                    html.Div(className='metric-selector-container', children=[
                        dcc.RadioItems(
                            id='metric-selector',
                            options=[
                                {'label': 'Revenu moyen', 'value': 'revenue'},
                                {'label': 'Vote moyen', 'value': 'vote_average'}
                            ],
                            value='revenue',
                            className='radio-group',
                            inputClassName='radio-input',
                            labelClassName='radio-label'
                        )
                    ]),
                ]),
            ]),
        ]),
        
        # Store pour stocker les données des heatmaps
        dcc.Store(id='heatmap-data-store')
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
        colorscale = [
            [0.0, "#ffffff"],   # blanc
            [0.2, "#f9c6b5"],   # rose très clair
            [0.4, "#f39271"],   # orange clair
            [0.6, "#ec6842"],   # orange foncé
            [0.8, "#e43d12"],   # rouge-orangé intense
            [1.0, "#a0210c"],   # rouge brun très foncé
        ],
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
        title= {
            'text': 'Budget moyen par genre (depuis 1970, par année)',
            'font': {
                'color': '#e43d12',
            },
            'x': 0.5,  # Centrer le titre horizontalement
            'xanchor': 'center'
        },
        xaxis=dict(
            title='Année',
            tickmode='array',
            tickvals=tick_years,
            ticktext=[str(year) for year in tick_years],
            tickangle=90
        ),
        yaxis=dict(
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
        margin=dict(l=150, r=50, t=80, b=100),  # Augmenter la marge gauche pour les labels
    )
    
    # Créer la heatmap pour la métrique sélectionnée
    metric_labels = {
        'revenue': 'Revenu moyen (USD)',
        'vote_average': 'Vote moyen'
    }
    
    # Utiliser les échelles de couleur standard
    color_scales = {
        'revenue': [
            [0.0, "#ffffff"],   # blanc
            [0.2, "#fbe8c2"],   # crème très clair
            [0.4, "#f6d27c"],   # jaune pâle
            [0.6, "#f1be3e"],   # jaune foncé
            [0.8, "#efb11d"],   # jaune orangé intense
            [1.0, "#a87410"],   # brun doré foncé
        ],
        'vote_average': [
            [0.0, "#ffffff"],   # blanc
            [0.2, "#ffe6ec"],   # rose très clair
            [0.4, "#ffc7d3"],   # rose pastel
            [0.6, "#ffa2b6"],   # rose saumon intense
            [0.8, "#e17b93"],   # rose framboise
            [1.0, "#b5536a"],   # vieux rose foncé
        ]
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
    
    # D6536D e43d12
    title_color = '#efb11d' if selected_metric == 'revenue' else '#b5536a'
    
    metric_fig.update_layout(
        title=
        {
            'text': f'{metric_labels[selected_metric]} par genre (depuis 1970, par année)',
            'font': {
                'color': title_color,
            },
            'x': 0.5,  # Centrer le titre horizontalement
            'xanchor': 'center'
        },
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
    [Output('hover-info', 'children')],
    [Input('budget-heatmap', 'hoverData'),
     Input('metric-heatmap', 'hoverData')],
    [State('metric-selector', 'value')]
)
def update_hover_info(budget_hover, metric_hover, selected_metric):
    # Déterminer quel graphique a déclenché le callback
    ctx = dash.callback_context
    if not ctx.triggered:
        # Si aucun déclencheur, cacher le div
        return [html.Div()]
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Obtenir les données de survol
    if trigger_id == 'budget-heatmap' and budget_hover:
        hover_data = budget_hover['points'][0]
    elif trigger_id == 'metric-heatmap' and metric_hover:
        hover_data = metric_hover['points'][0]
    else:
        # Si pas de données de survol, cacher le div
        return [html.Div()]
    
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
    
    hover_info = html.Div(
        className= 'heatmap-hover-info',
        children=
        [
            html.Div(
                className="heatmap-hover-label-container",
                children=[
                    html.Span("Genre:", className="heatmap-hover-label"),
                    html.Span(f"{genre}", className="heatmap-hover-value"),
                    html.Span("Année:", className="heatmap-hover-label"),
                    html.Span(f"{year}", className="heatmap-hover-value"),
                ]
            ),
            html.Div(className="heatmap-hover-label-container", children= [
                    html.Strong("Budget moyen: ", className="heatmap-hover-label"),
                    html.Span(f"{budget:,.2f} USD", className="heatmap-hover-value"),
                    html.Strong(f"{metric_labels[selected_metric]}: ", className="heatmap-hover-label"),
                    html.Span(f"{metric_value:,.2f}" + (" USD" if selected_metric == 'revenue' else ""), className="heatmap-hover-value")
            ])
        ]
    )
    
    return [hover_info]

def get_heatmap_budget_text():
    return html.Div(
        className='text',
        children=[
            html.H1(
                "GENRE ET BUDGET",
                className='text-title'
            ),
            html.P(
                """
                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. 
                Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. 
                Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. 
                Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. 
                Curabitur pretium tincidunt lacus. Nulla gravida orci a odio. Nullam varius, turpis et commodo pharetra, est eros bibendum elit, 
                nec luctus magna felis sollicitudin mauris. Integer in mauris eu nibh euismod gravida. Duis ac tellus et risus vulputate vehicula. 
                Donec lobortis risus a elit. Etiam tempor. Ut ullamcorper, ligula eu tempor congue, eros est euismod turpis, 
                id tincidunt sapien risus a quam. Maecenas fermentum consequat mi. Donec fermentum. Pellentesque malesuada nulla a mi. 
                Duis sapien sem, aliquet nec, commodo eget, consequat quis, neque.
                """,
                className='text-paragraph'
            ),
        ]
    )