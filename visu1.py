import dash
from dash import html, dcc, callback
from dash.dependencies import Input, Output, State
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

# Convertir les dates et supprimer les valeurs NaN AVANT la conversion en entier
df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')  # Handle invalid dates with 'coerce'
df = df.dropna(subset=['release_date'])  # Supprimer les lignes avec des dates invalides
df['release_date'] = df['release_date'].dt.year  # Extract the year
df['release_date'] = df['release_date'].astype(int)  # Maintenant on peut convertir en entier sans problème

# Exploser le DataFrame pour avoir une ligne par genre
df_exploded = df.explode('genres_list').rename(columns={'genres_list': 'genre'})

# Filtrer pour n'avoir que les données depuis 1970
df_exploded = df_exploded[df_exploded['release_date'] >= 1970]

df_exploded = df_exploded[~df_exploded['genre'].isna()]  # Supprimer les valeurs NaN

# Mis à jour des noms de genre
all_genre_names = sorted(df_exploded['genre'].unique())  # Trier les genres par ordre alphabétique

# Calculer les moyennes par genre et année pour tout le dataset
all_budget_avg = df_exploded.groupby(['genre', 'release_date'])['budget'].mean().reset_index()
all_revenue_avg = df_exploded.groupby(['genre', 'release_date'])['revenue'].mean().reset_index()
all_vote_avg = df_exploded.groupby(['genre', 'release_date'])['vote_average'].mean().reset_index()

# Calculer les valeurs min et max des MOYENNES pour chaque métrique
budget_min_avg = all_budget_avg['budget'].min()
budget_max_avg = all_budget_avg['budget'].max()

revenue_min_avg = all_revenue_avg['revenue'].min()
# Définir le max du revenu à 400 millions comme demandé
revenue_max_avg = 400000000  # 400 millions

vote_min_avg = all_vote_avg['vote_average'].min()
vote_max_avg = all_vote_avg['vote_average'].max()

# Dictionnaire des plages de valeurs pour chaque métrique (basé sur les moyennes)
metric_ranges = {
    'revenue': [revenue_min_avg, revenue_max_avg],
    'vote_average': [vote_min_avg, vote_max_avg]
}

# Obtenir toutes les années depuis 1970
years = sorted(df_exploded['release_date'].unique())

# Layout de l'application
app.layout = html.Div(className='content', children=[
    html.Header(children=[
        html.H1('Projet de Visualisation'),
        html.H2('Analyse des films par genre et année (depuis 1970)')
    ]),
    
    html.Main(className='viz-container', children=[
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
     Output('metric-heatmap', 'figure'),
     Output('heatmap-data-store', 'data')],
    [Input('metric-selector', 'value')]
)
def update_heatmaps(selected_metric):
    # Utiliser toutes les données depuis 1970, par année
    
    # Calculer les moyennes par genre et année
    budget_avg = df_exploded.groupby(['genre', 'release_date'])['budget'].mean().reset_index()
    metric_avg = df_exploded.groupby(['genre', 'release_date'])[selected_metric].mean().reset_index()
    
    # Créer un DataFrame complet avec toutes les combinaisons genre-année
    # Créer toutes les combinaisons possibles de genres et d'années
    complete_index = pd.MultiIndex.from_product(
        [all_genre_names, years],
        names=['genre', 'release_date']
    )
    
    # Créer des DataFrames complets avec des valeurs par défaut de 0
    complete_budget_df = pd.DataFrame(index=complete_index).reset_index()
    complete_budget_df = complete_budget_df.merge(
        budget_avg, on=['genre', 'release_date'], how='left'
    ).fillna(0)
    
    complete_metric_df = pd.DataFrame(index=complete_index).reset_index()
    complete_metric_df = complete_metric_df.merge(
        metric_avg, on=['genre', 'release_date'], how='left'
    ).fillna(0)
    
    # Fusionner les deux DataFrames pour avoir toutes les données dans un seul DataFrame
    combined_df = complete_budget_df.merge(
        complete_metric_df[['genre', 'release_date', selected_metric]],
        on=['genre', 'release_date'],
        how='left'
    )
    
    # Stocker les données pour les utiliser dans le callback de survol
    heatmap_data = combined_df.to_dict('records')
    
    # Définir les années à afficher (tous les 5 ans)
    tick_years = [year for year in years if (year - 1970) % 5 == 0]
    
    # Définir l'ordre des genres (identique pour les deux heatmaps)
    genre_order = all_genre_names
    
    # Créer la heatmap pour le budget
    budget_fig = go.Figure(data=go.Heatmap(
        z=complete_budget_df['budget'],
        x=complete_budget_df['release_date'],
        y=complete_budget_df['genre'],
        colorscale='Reds',
        zmin=budget_min_avg,
        zmax=budget_max_avg,
        customdata=np.stack((
            complete_budget_df['genre'],
            complete_budget_df['release_date'],
            complete_budget_df['budget'],
            complete_metric_df[selected_metric]
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
        z=complete_metric_df[selected_metric],
        x=complete_metric_df['release_date'],
        y=complete_metric_df['genre'],
        colorscale=color_scales[selected_metric],
        zmin=metric_ranges[selected_metric][0],
        zmax=metric_ranges[selected_metric][1],
        customdata=np.stack((
            complete_metric_df['genre'],
            complete_metric_df['release_date'],
            complete_budget_df['budget'],
            complete_metric_df[selected_metric]
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
    
    return budget_fig, metric_fig, heatmap_data

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

# Démarrage du serveur
if __name__ == '__main__':
    app.run(debug=True)