import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import json

# Initialisation
app = dash.Dash(__name__)
app.title = 'Analyse des Films'

# Chargement des données
df = pd.read_csv("data/combined.csv")

# Prétraitement
def extract_genres(genres_json):
    try:
        genres_json = genres_json.replace('""', '"')
        genres_list = json.loads(genres_json)
        return [genre['name'] for genre in genres_list]
    except Exception:
        return []

df['genres_list'] = df['genres'].apply(extract_genres)
df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
df['release_year'] = df['release_date'].dt.year

# Nettoyage global de base
df = df.dropna(subset=['budget', 'revenue', 'popularity', 'vote_count', 'vote_average', 'runtime'])
df = df[(df['budget'] > 0) & (df['revenue'] > 0) & (df['runtime'] > 0)]

# Définir les paires personnalisées
factor_pairs = [
    ('budget', 'vote_average'),
    ('budget', 'popularity'),
    ('vote_average', 'popularity'),
    ('vote_average', 'revenue'),
    ('popularity', 'revenue'),
    ('runtime', 'revenue'),
    ('runtime', 'popularity'),
    ('runtime', 'vote_average'),
]

# Map des labels
factor_label_map = {
    'budget': 'Budget (USD)',
    'revenue': 'Revenu (USD)',
    'popularity': 'Popularité',
    'vote_average': 'Note moyenne',
    'runtime': 'Durée (minutes)'
}

# Layout
app.layout = html.Div(style={
    'display': 'flex',
    'flexDirection': 'column',
    'minHeight': '100vh',
    'overflow': 'hidden'
}, children=[
    html.Header(style={'padding': '10px 20px', 'backgroundColor': '#f8f9fa', 'borderBottom': '1px solid #dee2e6'}, children=[
        html.H1('Analyse des Films'),
        html.P('Visualisation automatique des facteurs de succès.')
    ]),

    html.Div(id='dummy', style={'display': 'none'}),

    html.Div(style={
        'flex': 1,
        'overflowY': 'scroll'
    }, children=[
        html.Div(
            id='scatter-plots-container',
            style={
                'display': 'flex',
                'flexWrap': 'wrap',
                'gap': '20px',
                'padding': '20px',
                'justifyContent': 'flex-start',
                'alignItems': 'flex-start'
            }
        )
    ])
])

# Callback
@app.callback(
    Output('scatter-plots-container', 'children'),
    [Input('dummy', 'children')]
)
def update_scatter_plots(_):
    scatter_plots = []

    for x, y in factor_pairs:
        x_label = factor_label_map[x]
        y_label = factor_label_map[y]

        # Construire le sous-ensemble de données sans doublons
        columns_needed = list({x, y, 'title', 'release_year', 'vote_average', 'budget', 'revenue'})
        subset = df[columns_needed].dropna()

        # Filtrer les valeurs non-positives si on utilise un axe log
        if x in ['budget', 'revenue']:
            subset = subset[subset[x] > 0]
        if y in ['budget', 'revenue']:
            subset = subset[subset[y] > 0]

        if subset.empty:
            # Fallback si aucune donnée valide
            scatter_plots.append(html.Div(
                style={'width': '400px', 'height': '500px', 'border': '1px dashed gray', 'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'},
                children=[html.P(f"Aucune donnée pour : {x_label} vs {y_label}")]
            ))
            continue

        fig = px.scatter(
            subset,
            x=x,
            y=y,
            hover_name='title',
            hover_data=['release_year', 'vote_average', 'budget', 'revenue'],
            opacity=0.7,
            color_discrete_sequence=['red']
        )

        fig.update_layout(
            xaxis_title=x_label,
            yaxis_title=y_label,
            height=500,
            width=400,
            margin=dict(l=40, r=20, t=50, b=40),
        )

        if x in ['budget', 'revenue']:
            fig.update_xaxes(type='log')
        if y in ['budget', 'revenue']:
            fig.update_yaxes(type='log')

        scatter_plots.append(html.Div(
            style={'display': 'inline-block'},
            children=[dcc.Graph(figure=fig)]
        ))

    return scatter_plots

# Démarrage
if __name__ == '__main__':
    app.run_server(debug=True)
