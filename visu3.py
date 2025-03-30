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

# Layout de l'application
app.layout = html.Div(style={'font-family': 'Arial, sans-serif', 'margin': '0', 'padding': '0'}, children=[
    # En-tête
    html.Header(style={
        'background-color': '#2c3e50',
        'color': 'white',
        'padding': '20px',
        'text-align': 'center'
    }, children=[
        html.H1('Top 10 Pays par Critère de Films', style={'margin': '0'}),
        html.P('Analyse des pays selon le nombre de films remplissant différents critères', 
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
                        {'label': 'Revenu > 10M$', 'value': 'revenue'},
                        {'label': 'Note > 7', 'value': 'vote_average'}
                    ],
                    value='revenue',
                    labelStyle={'display': 'block', 'margin': '10px 0'}
                )
            ]),
            
            # Sélection du genre
            html.Div(style={'margin-bottom': '20px'}, children=[
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
                id='bar-chart',
                style={'height': '70vh'},
                config={'displayModeBar': True}
            ),
            html.Div(id='chart-info', style={'margin-top': '20px', 'text-align': 'center'})
        ])
    ])
])

# Callback pour mettre à jour le graphique en barres
@callback(
    [Output('bar-chart', 'figure'),
     Output('chart-info', 'children'),
     Output('debug-info', 'children')],
    [Input('success-criteria', 'value'),
     Input('genre-filter', 'value')]
)
def update_bar_chart(criteria, selected_genre):
    # Définir le seuil en fonction du critère
    if criteria == 'revenue':
        threshold = 10 * 1000000  # 10M$
        threshold_text = "10M$"
    else:  # vote_average
        threshold = 7
        threshold_text = "7"
    
    # Filtrer les films qui dépassent le seuil
    filtered_df = countries_df.copy()
    filtered_df['meets_threshold'] = filtered_df[criteria] >= threshold
    
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
    
    # Trier par nombre de films réussis et prendre les 10 premiers
    top_countries = agg_df.sort_values('successful_films', ascending=False).head(10)
    
    # Préparer les données pour le graphique
    countries = top_countries['countries'].tolist()
    successful_films = top_countries['successful_films'].tolist()
    
    # Préparer les données pour le genre
    genre_data = [0] * len(countries)
    ratio_data = [0] * len(countries)
    
    # Si un genre est sélectionné, calculer les données du genre
    if selected_genre:
        # Filtrer les films du genre sélectionné
        genre_filtered_df = filtered_df[filtered_df['genres_list'].apply(lambda x: selected_genre in x if isinstance(x, list) else False)]
        
        # Agréger les données par pays pour le genre sélectionné
        genre_agg_df = genre_filtered_df.groupby('countries').agg({
            'meets_threshold': 'sum'  # Compte les films du genre qui dépassent le seuil
        }).reset_index()
        
        genre_agg_df.rename(columns={
            'meets_threshold': 'genre_successful_films'
        }, inplace=True)
        
        # Fusionner avec les pays du top 10
        genre_top_countries = pd.merge(
            top_countries[['countries', 'successful_films']], 
            genre_agg_df, 
            on='countries', 
            how='left'
        ).fillna(0)
        
        # Mettre à jour les données du genre
        genre_data = genre_top_countries['genre_successful_films'].tolist()
        ratio_data = [g/t*100 if t > 0 else 0 for g, t in zip(genre_data, successful_films)]
    
    # Créer un DataFrame pour le graphique
    chart_df = pd.DataFrame({
        'country': countries,
        'total': successful_films,
        'genre': genre_data,
        'ratio': ratio_data
    })
    
    # Trier le DataFrame pour l'affichage (du plus grand au plus petit)
    chart_df = chart_df.sort_values('total', ascending=True)
    
    # Créer le graphique avec Plotly Express (plus stable pour les barres)
    if selected_genre:
        # Utiliser un graphique à barres empilées
        fig = px.bar(
            chart_df,
            y='country',
            x=['genre', 'total'],  # Première valeur = genre, deuxième valeur = reste
            orientation='h',
            barmode='relative',  # Mode relatif pour l'empilement
            color_discrete_sequence=['#e74c3c', '#3498db'],  # Rouge pour genre, bleu pour total
            labels={
                'country': 'Pays',
                'value': 'Nombre de Films',
                'variable': 'Catégorie'
            },
            title=f"Top 10 Pays par Nombre de Films avec {criteria} > {threshold_text}"
        )
        
        # Modifier la légende
        fig.data[0].name = selected_genre
        fig.data[1].name = f'Autres films avec {criteria} > {threshold_text}'
        
        # Ajouter des informations personnalisées pour le survol
        for i, trace in enumerate(fig.data):
            if i == 0:  # Trace du genre
                trace.hovertemplate = '<b>%{y}</b><br>' + f'{selected_genre}: ' + '%{x}<br><extra></extra>'
            else:  # Trace du total
                trace.hovertemplate = '<b>%{y}</b><br>Total: %{customdata}<br>Ratio: %{text}<extra></extra>'
                trace.customdata = chart_df['total'].tolist()
                trace.text = [f"{r:.1f}%" for r in chart_df['ratio'].tolist()]
    else:
        # Utiliser un graphique à barres simple
        fig = px.bar(
            chart_df,
            y='country',
            x='total',
            orientation='h',
            color_discrete_sequence=['#3498db'],  # Bleu pour total
            labels={
                'country': 'Pays',
                'total': 'Nombre de Films'
            },
            title=f"Top 10 Pays par Nombre de Films avec {criteria} > {threshold_text}"
        )
        
        # Modifier la légende
        fig.data[0].name = f'Films avec {criteria} > {threshold_text}'
        
        # Ajouter des informations personnalisées pour le survol
        fig.data[0].hovertemplate = '<b>%{y}</b><br>Films: %{x}<extra></extra>'
    
    # Mise en page du graphique
    fig.update_layout(
        xaxis_title="Nombre de Films",
        yaxis_title="Pays",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=20, r=20, t=60, b=20),
        height=600
    )
    
    # Texte d'information
    genre_text = f"Genre: {selected_genre}" if selected_genre else "Aucun genre sélectionné"
    total_successful = sum(successful_films)
    
    # Si un genre est sélectionné, calculer le total pour ce genre
    genre_total = sum(genre_data) if selected_genre else 0
    ratio_text = f"Ratio {selected_genre}/Total: {genre_total/total_successful*100:.1f}%" if selected_genre and total_successful > 0 else ""
    
    info_text = html.Div([
        html.P(f"Critère: {criteria} > {threshold_text} | {genre_text}"),
        html.P(f"Total des films dans le top 10 pays: {total_successful} {ratio_text}")
    ])
    
    # Information de débogage
    debug_text = f"Données agrégées: {len(agg_df)} pays, max={agg_df['successful_films'].max()} films dépassant le seuil"
    
    return fig, info_text, debug_text

# Démarrage du serveur
if __name__ == '__main__':
    app.run(debug=True)