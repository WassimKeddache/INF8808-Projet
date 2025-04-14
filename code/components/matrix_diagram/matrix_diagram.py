import dash
from dash import html, dcc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import pandas as pd
import json

app = dash.Dash(__name__)
app.title = 'Analyse des Films'

# ============================================================
# Data Loading and Preprocessing
# ============================================================
df = pd.read_csv("../data/combined.csv")

def extract_genres(genres_json):
    try:
        genres_json = genres_json.replace('""', '"')
        return [genre['name'] for genre in json.loads(genres_json)]
    except Exception:
        return []

df['genres_list'] = df['genres'].apply(extract_genres)
df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
df['release_year'] = df['release_date'].dt.year

df = df.dropna(subset=['budget', 'revenue', 'popularity', 'vote_count', 'vote_average', 'runtime'])
df = df[(df['budget'] > 0) & (df['revenue'] > 0)]

# ============================================================
# Label Mapping and Variables
# ============================================================
factor_label_map = {
    'budget': 'Budget (USD)',
    'revenue': 'Revenu (USD)',
    'popularity': 'Popularité',
    'vote_average': 'Note moyenne',
    'runtime': 'Duration (min)'
}
vars_for_corr = ['budget', 'revenue', 'popularity', 'vote_average', 'runtime']

# ============================================================
# Main Splom Figure and Correlation Table (Left and Right Columns)
# ============================================================

# Define dimensions for the Splom
dimensions = [
    dict(label=factor_label_map['budget'], values=df['budget']),
    dict(label=factor_label_map['revenue'], values=df['revenue']),
    dict(label=factor_label_map['popularity'], values=df['popularity']),
    dict(label=factor_label_map['vote_average'], values=df['vote_average']),
    dict(label=factor_label_map['runtime'], values=df['runtime'])
]

fig_splom = go.Figure(
    data=go.Splom(
        dimensions=dimensions,
        showupperhalf=False,             # Only lower triangle
        diagonal=dict(visible=False),    # Hide the diagonal
        marker=dict(
            color='red',
            opacity=0.7,
            line_color='white',
            line_width=0.5
        ),
        text=df['title'],
        customdata=df[['release_year', 'vote_average', 'budget', 'revenue']].values,
        hovertemplate=(
            "<b>%{text}</b><br>" +
            "Année: %{customdata[0]}<br>" +
            "Note moyenne: %{customdata[1]}<br>" +
            "Budget: %{customdata[2]:,}<br>" +
            "Revenu: %{customdata[3]:,}<extra></extra>"
        )
    )
)

fig_splom.update_layout(
    title=dict(
        text="Matrice triangulaire des variables des films",
        font={
            'color': '#e43d12',
        }
    ),
    autosize=False,
    width=1920,
    height=1080,
    margin=dict(l=0, r=20, t=50, b=40)
)

# Compute correlation matrix
corr_matrix = df[vars_for_corr].corr().round(2)

def generate_lower_corr_table(corr_matrix):
    header = [html.Th("Variable")] + [html.Th(col) for col in corr_matrix.columns]
    rows_list = []
    for i, row_name in enumerate(corr_matrix.index):
        cells = [html.Td(row_name)]
        for j, col_name in enumerate(corr_matrix.columns):
            if i > j:
                cells.append(html.Td(corr_matrix.iloc[i, j],
                                     style={'padding': '5px', 'border': '1px solid var(--border-color)'}))
            else:
                cells.append(html.Td("",
                                     style={'padding': '5px', 'border': '1px solid var(--border-color)',
                                            'backgroundColor': 'var(--background-color)'}))
        rows_list.append(html.Tr(cells))
    table = html.Table(
        [html.Thead(html.Tr(header))] +
        [html.Tbody(rows_list)],
        className="dashboard-card",
        style={
            'width': '100%',
            'borderCollapse': 'collapse',
            'textAlign': 'center',
            'marginTop': '20px'
        }
    )
    return table

corr_table = generate_lower_corr_table(corr_matrix)

# ============================================================
# Helper function for Individual Scatter Graphs
# ============================================================
def create_scatter(x_var, y_var):
    # Subsample the dataframe: take every 10th row for faster rendering
    dff = df.iloc[::10]
    fig = px.scatter(
        dff,
        x=x_var,
        y=y_var,
        hover_name="title",
        hover_data=["release_year", "vote_average", "budget", "revenue"],
        opacity=0.7,
        color_discrete_sequence=["red"]
    )
    fig.update_layout(
        title=f"{factor_label_map[y_var]} vs {factor_label_map[x_var]}",
        font={
            'color': '#e43d12',
        },
        margin=dict(l=40, r=20, t=50, b=40)
    )
    return dcc.Graph(
        figure=fig,
        config={'responsive': True},
        className="dashboard-card"
    )

# ============================================================
# Group Interpretations and Graphs
# ============================================================
interpretation_header = html.H4("Interprétation", className="countries-card-label")

# Group 1: Indicateurs financiers et d’audience : Budget, Revenue et Popularité
group1_header = html.H4("Groupe des indicateurs financiers et d’audience : Budget, Revenue et Popularité", className="countries-card-label")
group1_description = html.P(
    "Le budget présente une forte corrélation avec le revenue (0.71) : cela suggère qu’un investissement financier conséquent se traduit souvent par des revenus élevés. "
    "La popularité a également une corrélation modérée à forte avec le revenue (0.6) et une corrélation modérée avec le budget (0.43), soulignant que le buzz et la visibilité jouent un rôle important dans le succès commercial.",
    className='text-paragraph'
)
group1_interpretation = html.P(
    "Ces résultats indiquent que, pour le succès commercial, l’investissement (budget) et la capacité à générer du buzz (popularité) sont des facteurs déterminants.",
    className='text-paragraph'
)
group1_graphs = html.Div(
    style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '20px'},
    children=[
        create_scatter("budget", "revenue"),      # Revenue vs Budget
        create_scatter("budget", "popularity"),     # Popularité vs Budget
        create_scatter("revenue", "popularity")     # Popularité vs Revenue
    ]
)

# Group 2: Indicateurs de perception qualitative : Vote
group2_header = html.H4("Groupe des indicateurs de perception qualitative : Vote", className="countries-card-label")
group2_description = html.P(
    "La note moyenne a une très faible corrélation avec le budget (-0.03) et seulement une faible corrélation avec le revenue (0.19) et la popularité (0.29). "
    "Cela montre qu’un film peut avoir de bonnes performances commerciales même si sa qualité perçue par le public n’est pas particulièrement élevée, et inversement.",
    className='text-paragraph'
)
group2_interpretation = html.P(
    "La note moyenne semble être moins influente pour le succès commercial immédiat. Cela peut aussi refléter des cas où le bouche-à-oreille et d’autres mécanismes font que même un film moyennement noté peut attirer un large public.",
    className='text-paragraph'
)
group2_graphs = html.Div(
    style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '20px'},
    children=[
        create_scatter("budget", "vote_average"),   # Vote Average vs Budget
        create_scatter("revenue", "vote_average"),    # Vote Average vs Revenue
        create_scatter("popularity", "vote_average")  # Vote Average vs Popularité
    ]
)

# Group 3: Le rôle de la durée (Runtime)
group3_header = html.H4("Le rôle de la durée (Runtime)", className="countries-card-label")
group3_description = html.P(
    "La durée présente des corrélations faibles avec toutes les autres variables (0.23 avec le budget et le revenue, 0.18 avec la popularité, et 0.38 avec la note moyenne).",
    className='text-paragraph'
)
group3_interpretation = html.P(
    "La durée semble avoir peu d’impact direct sur le succès commercial ou la perception qualitative du film. "
    "Elle peut néanmoins jouer un rôle indirect (par exemple, une durée trop longue peut limiter le nombre de séances en salle, ou influencer la satisfaction des spectateurs dans certains genres).",
    className='text-paragraph'
)
group3_graphs = html.Div(
    style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '20px'},
    children=[
        create_scatter("budget", "runtime"),        # Runtime vs Budget
        create_scatter("revenue", "runtime"),         # Runtime vs Revenue
        create_scatter("popularity", "runtime"),      # Runtime vs Popularité
        create_scatter("vote_average", "runtime")     # Runtime vs Vote Average
    ]
)

# Synthèse
synthese_header = html.H4("Synthèse", className="countries-card-label")
synthese_description = html.P(
    "Le succès commercial (Revenu) est principalement associé à des investissements importants (budget) et à une forte interaction du public (popularité). "
    "La qualité perçue (Note moyenne), bien qu’importante d’un point de vue critique, n’explique pas à elle seule le succès commercial. "
    "La durée ne semble pas être un facteur majeur lorsqu’elle est prise isolément.",
    className='text-paragraph'
)

# ============================================================
# Final App Layout with CSS classes applied
# ============================================================
def get_matrix_diagram():
    return html.Div(className='content', children=[
        html.Div(className='dashboard-card', children=[
            html.Div(className='card-content', children=[
                # Header
                html.Header(
                    className="main-header",
                    children=[
                        html.Div(
                            className="header-content",
                            children=[
                                html.H1("Analyse des Films", className="app-title"),
                                html.P("Visualisation automatique des facteurs de succès.", className="header-subtitle")
                            ]
                        )
                    ]
                ),
                # Main Content
                html.Div(
                    className="main-content",
                    children=[
                        # Interpretation block above the main visualization
                        html.Div(
                            className="dashboard-card",
                            style={'marginBottom': '20px'},
                            children=[
                                html.H4("Interprétations" , className="countries-card-label"),
                                html.P(
                                    "La matrice triangulaire affiche la partie inférieure des relations entre les variables des films, "
                                    "tandis que le tableau de corrélation à droite présente les coefficients (r) pour chacune des paires. "
                                    "Les groupes suivants présentent des comparaisons spécifiques d'indicateurs.",
                                    className='text-paragraph'
                                )
                            ]
                        ),
                        # Main Visualization: Splom and correlation table side by side
                        html.Div(
                            style={
                                'display': 'flex', 
                                'flexDirection': 'column', 
                                'justifyContent': 'space-between', 
                                'alignItems': 'center'
                            },
                            children=[
                                # Splom Graph in its own block (full width)
                                html.Div(
                                    style={'width': '100%'},
                                    children=[dcc.Graph(figure=fig_splom, config={'responsive': True})]
                                ),
                                # Correlation Table below, with a width of 30% of the screen
                                html.Div(
                                    style={
                                        'width': '30%',
                                        'marginTop': '20px',
                                        'padding': '10px',
                                        'border': '1px solid #ccc',
                                        'backgroundColor': '#fafafa',
                                        'boxSizing': 'border-box'
                                    },
                                    children=[
                                        html.H4("Matrice de Corrélation (partie inférieure)", className="countries-card-label"),
                                        corr_table
                                    ]
                                )
                            ]
                        ),
                        # Individual Scatter Graph Groups
                        html.Div(
                            style={'marginTop': '40px'},
                            children=[
                                # Group 1: Financiers et Audience
                                group1_header,
                                group1_description,
                                interpretation_header,
                                group1_interpretation,
                                group1_graphs,
                                # Group 2: Vote
                                html.Br(),
                                group2_header,
                                group2_description,
                                interpretation_header,
                                group2_interpretation,
                                group2_graphs,
                                # Group 3: Runtime
                                html.Br(),
                                group3_header,
                                group3_description,
                                interpretation_header,
                                group3_interpretation,
                                group3_graphs,
                                # Synthèse
                                html.Br(),
                                synthese_header,
                                synthese_description
                            ]
                        )
                    ]
                )
            ])
        ])
    ])


if __name__ == '__main__':
    app.run_server(debug=True)
