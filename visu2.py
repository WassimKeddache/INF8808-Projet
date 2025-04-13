import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import json
import itertools

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
df = df[(df['budget'] > 0) & (df['revenue'] > 0)]

# Définir les paires personnalisées (sans runtime)
# factor_pairs = [
#     ('budget', 'revenue'),
#     ('budget', 'popularity'),
#     ('budget', 'vote_average'),
#     ('revenue', 'popularity'),
#     ('revenue', 'vote_average'),
#     ('popularity', 'vote_average'),
# ]


# Map des labels
factor_label_map = {
    'budget': 'Budget (USD)',
    'revenue': 'Revenu (USD)',
    'popularity': 'Popularité',
    'vote_average': 'Note moyenne',
    'runtime' : 'Duration (min)'
}


factor_pairs = list(itertools.combinations(factor_label_map.keys(), 2))

# Créer une matrice de comparaison pairwise
def generate_comparison_matrix():
    variables = list(factor_label_map.keys())
    matrix = pd.DataFrame('', index=variables, columns=variables)
    for x, y in factor_pairs:
        i, j = variables.index(x), variables.index(y)
        if i > j:
            matrix.iloc[i, j] = 'x'
        elif j > i:
            matrix.iloc[j, i] = 'x'
    return matrix

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
        'overflowY': 'scroll',
        'padding': '20px'
    }, children=[
        html.Div(
            id='scatter-plots-container'
        )
    ])
])
@app.callback(
    Output('scatter-plots-container', 'children'),
    [Input('dummy', 'children')]
)
def update_scatter_plots(_):
    scatter_plots = []
    
    
    # Création d'un bloc d'interprétation en haut, sur toute la largeur
    interpretation_block = html.Div(
        style={
            'width': '100%',
            'border': '1px solid #ccc',
            'padding': '20px',
            'boxSizing': 'border-box',
            'marginBottom': '20px'
        },
        children=[
            html.H4("Interprétations"),
            html.P("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor "
                   "incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud "
                   "exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.")
        ]
    )

    for x, y in factor_pairs:
        x_label = factor_label_map[x]
        y_label = factor_label_map[y]

        columns_needed = list({x, y, 'title', 'release_year', 'vote_average', 'budget', 'revenue', 'runtime'})
        subset = df[columns_needed].dropna()

        if x in ['budget', 'revenue']:
            subset = subset[subset[x] > 0]
        if y in ['budget', 'revenue']:
            subset = subset[subset[y] > 0]

        # Sous-échantillonnage
        subset = subset.iloc[::4]

        if subset.empty:
            scatter_plots.append(
                html.Div(
                    style={'width': '400px', 'height': '400px', 'border': '1px dashed gray',
                           'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'},
                    children=[html.P(f"Aucune donnée pour : {x_label} vs {y_label}")]
                )
            )
            continue

        # Calcul du coefficient de corrélation
        # Ici, on utilise la méthode .corr() de pandas
        correlation = subset[x].corr(subset[y])
        
        # Création du graphique
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
            autosize=True,
            height=400,
            margin=dict(l=40, r=20, t=50, b=40),
        )

        if x in ['budget', 'revenue']:
            fig.update_xaxes(type='log')
        if y in ['budget', 'revenue']:
            fig.update_yaxes(type='log')

        # Composant graphique avec affichage du coefficient en dessous
        graph_block = html.Div(
            style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'},
            children=[
                dcc.Graph(
                    figure=fig,
                    config={'responsive': True},
                    style={'width': '100%', 'maxWidth': '400px', 'height': '400px'}
                ),
                html.Div(
                    style={'marginTop': '10px'},
                    children=[
                        html.P(f"Facteur de corrélation : {correlation:.2f}",
                               style={'fontWeight': 'bold', 'textAlign': 'center'})
                    ]
                )
            ]
        )

        scatter_plots.append(graph_block)

    # Arrange plots in rows as before: 4, 3, 2, 1 plots per row
    rows = [4, 3, 2, 1]
    base_num_cols = rows[0]  # This will be 4, so the first row is "full" at 100%

    layout = []
    index = 0
    for num_cols in rows:
        # Grab the scatter plots that belong to this row
        row_children = scatter_plots[index : index + num_cols]
        index += num_cols

        # Compute the row width as a fraction of the first row’s width
        row_width = f"{(num_cols / base_num_cols) * 100}%"
        
        # Use CSS grid to place the given number of columns in this row
        row_style = {
            'display': 'grid',
            'gridTemplateColumns': f'repeat({num_cols}, 1fr)',
            'gridGap': '20px',
            'width': row_width,
            'marginLeft': '0',
            'marginRight': '0',
            'marginBottom': '20px'
        }

        
        

        layout.append(html.Div(style=row_style, children=row_children))

    final_layout = [interpretation_block] + layout
    return final_layout


# Démarrage
if __name__ == '__main__':
    app.run_server(debug=True)