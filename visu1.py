import dash
from dash import html, dcc, callback
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime
import numpy as np

# Initialisation de l'application Dash
app = dash.Dash(__name__)
app.title = 'Projet de Visualisation'

df = pd.read_csv("data/combined.csv")

def extract_genres(genres_json):
    try:
        # Remplacer les doubles guillemets par des simples guillemets
        genres_json = genres_json.replace('""', '"')
        # Analyser le JSON
        genres_list = json.loads(genres_json)
        # Extraire les noms des genres
        return [genre['name'] for genre in genres_list]
    except Exception as e:
        print(f"Erreur lors de l'extraction des genres: {e}")
        print(f"JSON problématique: {genres_json}")
        return []

all_genre_names = df['genres'].apply(extract_genres).explode().unique()

# Appliquer la fonction pour extraire les genres
df['genres_list'] = df['genres'].apply(extract_genres)

df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')  # Handle invalid dates with 'coerce'
df['release_date'] = df['release_date'].dt.year  # Extract the year

df = df.dropna(subset=['release_date'])

# Exploser le DataFrame pour avoir une ligne par genre
df_exploded = df.explode('genres_list').rename(columns={'genres_list': 'genre'})

# Filtrer pour n'avoir que les données depuis 1970
df_exploded = df_exploded[df_exploded['release_date'] >= 1970]

df_exploded = df_exploded[~df_exploded['genre'].isna()]  # Supprimer les valeurs NaN

# Créer une colonne pour les périodes de 5 ans
df_exploded['period'] = ((df_exploded['release_date'] - 1970) // 5) * 5 + 1970

# Mis à jour des noms de genre
all_genre_names = df_exploded['genre'].unique()

# Calculer les moyennes par genre et période de 5 ans pour tout le dataset
all_budget_avg = df_exploded.groupby(['genre', 'period'])['budget'].mean().reset_index()
all_revenue_avg = df_exploded.groupby(['genre', 'period'])['revenue'].mean().reset_index()
all_popularity_avg = df_exploded.groupby(['genre', 'period'])['popularity'].mean().reset_index()
all_vote_avg = df_exploded.groupby(['genre', 'period'])['vote_average'].mean().reset_index()

# Calculer les valeurs min et max des MOYENNES pour chaque métrique
budget_min_avg = all_budget_avg['budget'].min()
budget_max_avg = all_budget_avg['budget'].max()

revenue_min_avg = all_revenue_avg['revenue'].min()
revenue_max_avg = all_revenue_avg['revenue'].max()

popularity_min_avg = all_popularity_avg['popularity'].min()
popularity_max_avg = all_popularity_avg['popularity'].max()

vote_min_avg = all_vote_avg['vote_average'].min()
vote_max_avg = all_vote_avg['vote_average'].max()

# Dictionnaire des plages de valeurs pour chaque métrique (basé sur les moyennes)
metric_ranges = {
    'revenue': [revenue_min_avg, revenue_max_avg],
    'popularity': [popularity_min_avg, popularity_max_avg],
    'vote_average': [vote_min_avg, vote_max_avg]
}

# Obtenir toutes les périodes de 5 ans depuis 1970
periods = sorted(df_exploded['period'].unique())

# Layout de l'application
app.layout = html.Div(className='content', children=[
    html.Header(children=[
        html.H1('Projet de Visualisation'),
        html.H2('Analyse des films par genre et période de 5 ans (depuis 1970)')
    ]),
    
    html.Main(className='viz-container', children=[
        # Conteneur pour les deux heatmaps
        html.Div(className='heatmaps-container', style={'display': 'flex'}, children=[
            # Heatmap de gauche (budget)
            html.Div(className='heatmap-left', style={'width': '50%'}, children=[
                html.H3('Budget moyen par genre et période'),
                dcc.Graph(id='budget-heatmap')
            ]),
            
            # Heatmap de droite (métrique sélectionnable)
            html.Div(className='heatmap-right', style={'width': '50%'}, children=[
                html.H3('Métrique par genre et période'),
                dcc.Graph(id='metric-heatmap')
            ])
        ]),
        
        # Contrôles (seulement le sélecteur de métrique, pas de slider)
        html.Div(className='controls', children=[
            # Sélecteur de métrique pour la heatmap de droite
            html.Div(className='metric-selector', children=[
                html.Label('Sélectionner une métrique:'),
                dcc.RadioItems(
                    id='metric-selector',
                    options=[
                        {'label': 'Revenu moyen', 'value': 'revenue'},
                        {'label': 'Popularité moyenne', 'value': 'popularity'},
                        {'label': 'Vote moyen', 'value': 'vote_average'}
                    ],
                    value='revenue',
                    labelStyle={'display': 'inline-block', 'margin-right': '20px'}
                )
            ])
        ])
    ])
])

# Callback pour mettre à jour les deux heatmaps en fonction du sélecteur de métrique
@callback(
    [Output('budget-heatmap', 'figure'),
     Output('metric-heatmap', 'figure')],
    [Input('metric-selector', 'value')]
)
def update_heatmaps(selected_metric):
    # Utiliser toutes les données depuis 1970, regroupées par périodes de 5 ans
    
    # Calculer les moyennes par genre et période
    budget_avg = df_exploded.groupby(['genre', 'period'])['budget'].mean().reset_index()
    metric_avg = df_exploded.groupby(['genre', 'period'])[selected_metric].mean().reset_index()
    
    # Créer un DataFrame complet avec toutes les combinaisons genre-période
    # Créer toutes les combinaisons possibles de genres et de périodes
    complete_index = pd.MultiIndex.from_product(
        [all_genre_names, periods],
        names=['genre', 'period']
    )
    
    # Créer des DataFrames complets avec des valeurs par défaut de 0
    complete_budget_df = pd.DataFrame(index=complete_index).reset_index()
    complete_budget_df = complete_budget_df.merge(
        budget_avg, on=['genre', 'period'], how='left'
    ).fillna(0)
    
    complete_metric_df = pd.DataFrame(index=complete_index).reset_index()
    complete_metric_df = complete_metric_df.merge(
        metric_avg, on=['genre', 'period'], how='left'
    ).fillna(0)
    
    # Créer la heatmap pour le budget avec une échelle de couleur fixe basée sur les moyennes
    budget_fig = go.Figure(data=go.Heatmap(
        z=complete_budget_df['budget'],
        x=complete_budget_df['period'],
        y=complete_budget_df['genre'],
        colorscale='Reds',  # Utiliser des teintes de rouge
        zmin=budget_min_avg,  # Utiliser le min des moyennes
        zmax=budget_max_avg,  # Utiliser le max des moyennes
        hovertemplate='<b>Genre:</b> %{y}<br><b>Période:</b> %{x}<br><b>Budget moyen:</b> %{z:,.2f} USD<extra></extra>'
    ))
    
    budget_fig.update_layout(
        title='Budget moyen par genre (depuis 1970, par période de 5 ans)',
        xaxis=dict(
            title='Période',
            tickmode='array',
            tickvals=periods,  # Utiliser les périodes exactes comme valeurs de tick
            ticktext=[f"{int(period)}-{str(int(period)+4)[-2:]}" for period in periods]  # Étiquettes des ticks
        ),
        yaxis=dict(
            title='Genre',
            categoryorder='category ascending',
            showticklabels=True  # Afficher les noms des genres
        ),
        coloraxis_colorbar=dict(
            title='Budget moyen (USD)'
        ),
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    # Créer la heatmap pour la métrique sélectionnée avec une échelle de couleur fixe
    metric_labels = {
        'revenue': 'Revenu moyen (USD)',
        'popularity': 'Popularité moyenne',
        'vote_average': 'Vote moyen'
    }
    
    metric_fig = go.Figure(data=go.Heatmap(
        z=complete_metric_df[selected_metric],
        x=complete_metric_df['period'],
        y=complete_metric_df['genre'],
        colorscale='Blues',  # Utiliser des teintes de bleu pour différencier
        zmin=metric_ranges[selected_metric][0],  # Utiliser le min des moyennes
        zmax=metric_ranges[selected_metric][1],  # Utiliser le max des moyennes
        hovertemplate=f'<b>Genre:</b> %{{y}}<br><b>Période:</b> %{{x}}<br><b>{metric_labels[selected_metric]}:</b> %{{z:,.2f}}<extra></extra>'
    ))
    
    metric_fig.update_layout(
        title=f'{metric_labels[selected_metric]} par genre (depuis 1970, par période de 5 ans)',
        xaxis=dict(
            title='Période',
            tickmode='array',
            tickvals=periods,  # Utiliser les périodes exactes comme valeurs de tick
            ticktext=[f"{int(period)}-{str(int(period)+4)[-2:]}" for period in periods]  # Étiquettes des ticks
        ),
        yaxis=dict(
            title='',  # Supprimer le titre de l'axe y
            showticklabels=False,  # Masquer les noms des genres
            categoryorder='category ascending'
        ),
        coloraxis_colorbar=dict(
            title=metric_labels[selected_metric]
        ),
        margin=dict(l=0, r=50, t=80, b=50)  # Réduire la marge gauche puisqu'il n'y a pas d'étiquettes
    )
    
    return budget_fig, metric_fig

# Démarrage du serveur
if __name__ == '__main__':
    app.run(debug=True)