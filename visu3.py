import dash
from dash import html, dcc, callback
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import numpy as np
from datetime import datetime
import pycountry

# Initialisation de l'application Dash avec suppress_callback_exceptions=True
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = 'Répartition Géographique des Films à Succès'

# Chargement des données
df = pd.read_csv("data/combined.csv")

# Fonction pour convertir ISO-2 en ISO-3
def convert_iso2_to_iso3(iso2_code):
    try:
        if pd.isna(iso2_code) or iso2_code == '':
            return None
        country = pycountry.countries.get(alpha_2=iso2_code)
        if country:
            return country.alpha_3
        return None
    except Exception as e:
        return None

# Prétraitement des données
def extract_countries(countries_json):
    try:
        countries_json = countries_json.replace('""', '"')
        countries_list = json.loads(countries_json)
        # Extraire les codes ISO-2 et les convertir en ISO-3
        iso2_codes = [country['iso_3166_1'] for country in countries_list]
        iso3_codes = [convert_iso2_to_iso3(code) for code in iso2_codes]
        # Filtrer les codes None
        return [code for code in iso3_codes if code]
    except Exception as e:
        return []

def extract_genres(genres_json):
    try:
        genres_json = genres_json.replace('""', '"')
        genres_list = json.loads(genres_json)
        return [genre['name'] for genre in genres_list]
    except Exception as e:
        return []

# Extraction des pays et genres
df['countries'] = df['production_countries'].apply(extract_countries)
df['genres_list'] = df['genres'].apply(extract_genres)

# Conversion des dates et création de la colonne décennie
df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
df['release_year'] = df['release_date'].dt.year
df['decade'] = (df['release_year'] // 10) * 10
df = df.dropna(subset=['release_year', 'budget', 'revenue', 'popularity', 'vote_average'])

# Explosion des pays pour avoir une ligne par pays de production
countries_df = df.explode('countries')
countries_df = countries_df[countries_df['countries'].notna() & (countries_df['countries'] != '')]

# Liste des genres uniques pour le filtre
all_genres = sorted(list(set([genre for sublist in df['genres_list'].dropna() for genre in sublist])))

# Création des options pour les sliders
decades = sorted(countries_df['decade'].unique())
min_year = 1970
max_year = int(decades[-1]) if decades else 2020

# Création des sliders de seuil pour chaque critère
revenue_slider = dcc.Slider(
    id='revenue-threshold-slider',
    min=1,
    max=200,
    step=10,
    marks={10: '10M$', 50: '50M$', 100: '100M$', 200: '200M$'},
    value=50,
    tooltip={"placement": "bottom", "always_visible": True}
)

popularity_slider = dcc.Slider(
    id='popularity-threshold-slider',
    min=5,
    max=100,
    step=5,
    marks={5: '5', 25: '25', 50: '50', 100: '100'},
    value=25,
    tooltip={"placement": "bottom", "always_visible": True}
)

vote_slider = dcc.Slider(
    id='vote-threshold-slider',
    min=5,
    max=9,
    step=0.5,
    marks={5: '5', 6: '6', 7: '7', 8: '8', 9: '9'},
    value=7,
    tooltip={"placement": "bottom", "always_visible": True}
)

# Layout de l'application
app.layout = html.Div(style={'font-family': 'Arial, sans-serif', 'margin': '0', 'padding': '0'}, children=[
    # En-tête
    html.Header(style={
        'background-color': '#2c3e50',
        'color': 'white',
        'padding': '20px',
        'text-align': 'center'
    }, children=[
        html.H1('Répartition Géographique des Films à Succès', style={'margin': '0'}),
        html.P('Analyse de la distribution mondiale des films selon différents critères de succès', 
               style={'margin-top': '10px'})
    ]),
    
    # Conteneur principal
    html.Div(style={'display': 'flex', 'flex-wrap': 'wrap', 'padding': '20px'}, children=[
        # Panneau de contrôle
        html.Div(style={
            'width': '300px',
            'padding': '20px',
            'background-color': '#f8f9fa',
            'border-radius': '5px',
            'box-shadow': '0 2px 4px rgba(0,0,0,0.1)',
            'margin-right': '20px'
        }, children=[
            html.H3('Critères de Succès'),
            
            # Sélection du critère de succès
            html.Div(style={'margin-bottom': '20px'}, children=[
                html.Label('Sélectionner le critère:'),
                dcc.RadioItems(
                    id='success-criteria',
                    options=[
                        {'label': 'Revenu total', 'value': 'revenue'},
                        {'label': 'Popularité moyenne', 'value': 'popularity'},
                        {'label': 'Note moyenne', 'value': 'vote_average'}
                    ],
                    value='revenue',
                    labelStyle={'display': 'block', 'margin': '10px 0'}
                )
            ]),
            
            # Slider pour la décennie
            html.Div(style={'margin-bottom': '20px'}, children=[
                html.Label('Période (décennie):'),
                dcc.RangeSlider(
                    id='decade-slider',
                    min=min_year,
                    max=max_year,
                    step=10,
                    marks={year: str(year) for year in range(min_year, max_year+1, 10)},
                    value=[1980, 2020]
                )
            ]),
            
            # Sliders pour le seuil de succès (tous inclus mais affichés conditionnellement)
            html.Div(style={'margin-bottom': '20px'}, children=[
                html.Label('Seuil de succès:'),
                html.Div(id='revenue-slider-container', style={'display': 'block'}, children=[revenue_slider]),
                html.Div(id='popularity-slider-container', style={'display': 'none'}, children=[popularity_slider]),
                html.Div(id='vote-slider-container', style={'display': 'none'}, children=[vote_slider])
            ]),
            
            # Sélection du genre
            html.Div(children=[
                html.Label('Filtrer par genre:'),
                dcc.Dropdown(
                    id='genre-filter',
                    options=[{'label': genre, 'value': genre} for genre in all_genres],
                    value=None,
                    placeholder='Tous les genres'
                )
            ]),
            
            # Ajout d'un indicateur de débogage
            html.Div(id='debug-info', style={'margin-top': '20px', 'font-size': '12px', 'color': '#666'})
        ]),
        
        # Zone de visualisation
        html.Div(style={
            'flex': '1',
            'min-width': '600px',
            'background-color': 'white',
            'border-radius': '5px',
            'box-shadow': '0 2px 4px rgba(0,0,0,0.1)',
            'padding': '20px'
        }, children=[
            dcc.Graph(
                id='choropleth-map',
                style={'height': '70vh'}
            ),
            html.Div(id='map-info', style={'margin-top': '20px', 'text-align': 'center'})
        ])
    ])
])

# Callback pour afficher le slider approprié en fonction du critère sélectionné
@callback(
    [Output('revenue-slider-container', 'style'),
     Output('popularity-slider-container', 'style'),
     Output('vote-slider-container', 'style')],
    [Input('success-criteria', 'value')]
)
def toggle_slider_visibility(criteria):
    revenue_style = {'display': 'block'} if criteria == 'revenue' else {'display': 'none'}
    popularity_style = {'display': 'block'} if criteria == 'popularity' else {'display': 'none'}
    vote_style = {'display': 'block'} if criteria == 'vote_average' else {'display': 'none'}
    return revenue_style, popularity_style, vote_style

# Callback pour mettre à jour la carte choroplèthe
@callback(
    [Output('choropleth-map', 'figure'),
     Output('map-info', 'children'),
     Output('debug-info', 'children')],
    [Input('success-criteria', 'value'),
     Input('decade-slider', 'value'),
     Input('revenue-threshold-slider', 'value'),
     Input('popularity-threshold-slider', 'value'),
     Input('vote-threshold-slider', 'value'),
     Input('genre-filter', 'value')]
)
def update_choropleth(criteria, decade_range, revenue_threshold, popularity_threshold, vote_threshold, genre):
    # Sélectionner le seuil approprié en fonction du critère
    if criteria == 'revenue':
        threshold = revenue_threshold
    elif criteria == 'popularity':
        threshold = popularity_threshold
    else:  # vote_average
        threshold = vote_threshold
    
    # Filtrer par décennie
    filtered_df = countries_df[(countries_df['decade'] >= decade_range[0]) & 
                              (countries_df['decade'] <= decade_range[1])]
    
    # Filtrer par genre si sélectionné
    if genre:
        filtered_df = filtered_df[filtered_df['genres_list'].apply(lambda x: genre in x if isinstance(x, list) else False)]
    
    # Filtrer par seuil de succès et marquer les films qui dépassent le seuil
    if criteria == 'revenue':
        filtered_df['meets_threshold'] = filtered_df[criteria] >= threshold * 1000000
        threshold_text = f"{threshold}M$"
    else:
        filtered_df['meets_threshold'] = filtered_df[criteria] >= threshold
        threshold_text = str(threshold)
    
    # Agréger les données par pays - compter le nombre de films qui dépassent le seuil
    agg_df = filtered_df.groupby('countries').agg({
        'meets_threshold': 'sum',  # Compte les films qui dépassent le seuil
        'title': 'count'           # Compte total de films
    }).reset_index()
    
    # Renommer les colonnes pour plus de clarté
    agg_df.rename(columns={
        'meets_threshold': 'successful_films',
        'title': 'total_films'
    }, inplace=True)
    
    # Créer la carte choroplèthe
    if criteria == 'revenue':
        title = f"Nombre de Films avec Revenu ≥ {threshold_text} par Pays"
    elif criteria == 'popularity':
        title = f"Nombre de Films avec Popularité ≥ {threshold} par Pays"
    else:
        title = f"Nombre de Films avec Note ≥ {threshold} par Pays"
    
    # Ajouter des informations pour le hover
    hover_data = {
        'total_films': True,
        'successful_films': True
    }
    
    # Définir une échelle de couleur fixe
    # Déterminer le maximum global pour l'échelle de couleur
    max_films = 200  # Valeur maximale fixe pour l'échelle
    
    # Créer la carte choroplèthe avec des teintes de rouge et une échelle fixe
    fig = px.choropleth(
        agg_df,
        locations='countries',
        locationmode='ISO-3',
        color='successful_films',  # Utiliser le nombre de films qui dépassent le seuil
        hover_name='countries',
        hover_data=hover_data,
        color_continuous_scale='Reds',
        range_color=[0, max_films],  # Échelle fixe
        labels={
            'successful_films': 'Films qui dépassent le seuil',
            'total_films': 'Nombre total de films'
        },
        title=title
    )
    
    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='natural earth'
        ),
        margin=dict(l=0, r=0, t=50, b=0),
        coloraxis_colorbar=dict(
            title="Nombre de films"
        )
    )
    
    # Texte d'information
    period_text = f"{decade_range[0]} à {decade_range[1]}"
    genre_text = f"Genre: {genre}" if genre else "Tous les genres"
    total_successful = agg_df['successful_films'].sum()
    total_films = agg_df['total_films'].sum()
    
    info_text = html.Div([
        html.P(f"Période: {period_text} | {genre_text} | Seuil de succès: {threshold_text}"),
        html.P(f"Films qui dépassent le seuil: {total_successful} sur {total_films} films ({(total_successful/total_films*100):.1f}%)")
    ])
    
    # Information de débogage
    debug_text = f"Données agrégées: {len(agg_df)} pays, max={agg_df['successful_films'].max()} films dépassant le seuil"
    
    return fig, info_text, debug_text

# Démarrage du serveur
if __name__ == '__main__':
    app.run(debug=True)