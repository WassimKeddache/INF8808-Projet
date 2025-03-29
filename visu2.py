import dash
from dash import html, dcc, callback
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import numpy as np

# Initialisation de l'application Dash
app = dash.Dash(__name__)
app.title = 'Analyse des Films'

# Chargement des données
df = pd.read_csv("data/combined.csv")

# Prétraitement des données
def extract_genres(genres_json):
    try:
        genres_json = genres_json.replace('""', '"')
        genres_list = json.loads(genres_json)
        return [genre['name'] for genre in genres_list]
    except Exception as e:
        return []

df['genres_list'] = df['genres'].apply(extract_genres)
df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
df['release_year'] = df['release_date'].dt.year

# Filtrer les données pour éliminer les valeurs extrêmes et les valeurs manquantes
df = df.dropna(subset=['budget', 'revenue', 'popularity', 'vote_count', 'vote_average', 'runtime'])
df = df[(df['budget'] > 0) & (df['revenue'] > 0) & (df['runtime'] > 0)]

# Définir les facteurs qui peuvent être sélectionnés pour l'axe y
y_factors = [
    {'label': 'Budget (USD)', 'value': 'budget'},
    {'label': 'Revenu (USD)', 'value': 'revenue'},
    {'label': 'Popularité', 'value': 'popularity'},
    {'label': 'Note moyenne', 'value': 'vote_average'},
    {'label': 'Durée (minutes)', 'value': 'runtime'}
]

# Définir les facteurs pour l'axe x (qui seront fixes)
x_factors = [
    {'name': 'revenue', 'label': 'Revenu (USD)'},
    {'name': 'popularity', 'label': 'Popularité'},
    {'name': 'runtime', 'label': 'Durée (minutes)'},
    {'name': 'vote_average', 'label': 'Note moyenne'},
    {'name': 'budget', 'label': 'Budget (USD)'}
]

# Layout de l'application
app.layout = html.Div(className='content', style={'display': 'flex', 'flex-direction': 'column', 'height': '100vh'}, children=[
    # En-tête
    html.Header(style={'padding': '10px 20px', 'background-color': '#f8f9fa', 'border-bottom': '1px solid #dee2e6'}, children=[
        html.H1('Analyse des Films'),
        html.P('Cette visualisation permet d\'analyser les relations entre différents facteurs de succès des films.')
    ]),
    
    # Contenu principal avec sidebar et scatter plots
    html.Div(style={'display': 'flex', 'flex': 1, 'overflow': 'hidden'}, children=[
        # Sidebar pour la sélection du facteur en ordonnée
        
        # Zone principale pour les scatter plots en rangée unique
        html.Div(style={
            'flex': 1,
            'overflow-x': 'auto',  # Permettre le défilement horizontal
            'white-space': 'nowrap'  # Empêcher le retour à la ligne
        }, children=[
            # Conteneur pour les scatter plots en rangée unique
            html.Div(
                id='scatter-plots-container',
                style={
                    'display': 'inline-flex',  # Afficher les éléments en ligne
                    'padding': '20px'
                }
            ),
        ])
    ]),
    html.Div(className='sidebar', style={
            'width': '250px',
            'padding': '20px',
            'overflow-y': 'auto'
        }, children=[
            html.H3('Sélectionner le facteur à afficher en ordonnée:'),
            dcc.RadioItems(
                id='y-factor-selector',
                options=y_factors,
                value='vote_average',  # Valeur par défaut
                labelStyle={'display': 'block', 'margin-bottom': '15px'}
            )
        ])
])

# Callback pour mettre à jour les scatter plots en fonction du facteur sélectionné
@callback(
    Output('scatter-plots-container', 'children'),
    [Input('y-factor-selector', 'value')]
)
def update_scatter_plots(selected_y_factor):
    # Obtenir le label du facteur sélectionné
    y_label = next(item['label'] for item in y_factors if item['value'] == selected_y_factor)
    
    # Créer un scatter plot pour chaque facteur x
    scatter_plots = []
    
    for i in range(len(x_factors)):
        # Ne pas créer un graphique si le facteur x est le même que le facteur y
        if x_factors[i]['name'] == selected_y_factor:
            continue
        
        # Créer le scatter plot
        fig = px.scatter(
            df,
            x=x_factors[i]['name'],
            y=selected_y_factor,
            hover_name='title',
            hover_data=['release_year', 'vote_average', 'budget', 'revenue'],
            opacity=0.7,
            color_discrete_sequence=['red']  # Définition de la couleur des points
        )
        
        # Configurer le layout du graphique
        fig.update_layout(
            xaxis_title=x_factors[i]['label'],
            yaxis= dict(
            title=y_label if i == 0 else '',  # Afficher le label de l'axe y uniquement pour le premier graphique
            showticklabels= i == 0  # Afficher les noms des genres
            ),
            height=500,
            width=400,
            margin=dict(l=40, r=20, t=50, b=40),
        )
        
        # Ajouter des échelles logarithmiques pour les valeurs monétaires
        if x_factors[i]['name'] in ['budget', 'revenue']:
            fig.update_xaxes(type='log')
        
        if selected_y_factor in ['budget', 'revenue']:
            fig.update_yaxes(type='log')
        
        # Créer un conteneur pour le graphique
        scatter_plot = html.Div(
            style={
                'display': 'inline-block',  # Afficher en ligne
                'margin-right': '20px',     # Espacement entre les graphiques
                'vertical-align': 'top'     # Aligner en haut
            },
            children=[dcc.Graph(figure=fig)]
        )
        
        scatter_plots.append(scatter_plot)
    
    return scatter_plots

# Démarrage du serveur
if __name__ == '__main__':
    app.run(debug=True)