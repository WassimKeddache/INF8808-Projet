import dash
from dash import html, dcc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import pandas as pd
import json

app = dash.Dash(__name__)
app.title = 'Quels ingrédients font le succès d’un film ?'

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
    'runtime': 'Durée (min)'
}
vars_for_corr = ['budget', 'revenue', 'popularity', 'vote_average', 'runtime']

# ============================================================
# Helper function for Individual Scatter Graphs
# ============================================================

def create_scatter(x_var, y_var):
    dff = df.iloc[::10]
    fig = px.scatter(
        dff,
        x=x_var,
        y=y_var,
        hover_name="title",
        custom_data=["release_year", "vote_average", "budget", "revenue", "popularity", "runtime"],
        opacity=0.7,
        color_discrete_sequence=["red"],
        labels=factor_label_map
    )
    fig.update_layout(
        title=f"{factor_label_map[y_var]} vs {factor_label_map[x_var]}",
        font={
            'color': '#e43d12',
        },
        margin=dict(l=40, r=20, t=50, b=40),
        hoverlabel=dict(
        bgcolor='rgba(228, 61, 18, 0.15)',
        bordercolor='#e43d12',
        font=dict(color='black')
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(228, 61, 18, 0.15)',
            zeroline=False
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(228, 61, 18, 0.15)',
            zeroline=False
        )

    )
    fig.update_traces(
    hovertemplate=(
        "<b>%{hovertext}</b><br>" +
        "Année : %{customdata[0]}<br>" +
        "Vote moyen : %{customdata[1]}<br>" +
        "Budget : %{customdata[2]:,.0f} $<br>" +
        "Revenu : %{customdata[3]:,.0f} $<br>" +
        "Popularité : %{customdata[4]:.2f}<br>" +
        "Durée : %{customdata[5]:.0f} min<extra></extra>"
    )
)

    return dcc.Graph(
        figure=fig,
        config={'responsive': True},
        className="dashboard-card"
    )

# ============================================================
# Group Interpretations and Graphs
# ============================================================

group1_header = html.H4("1 - Groupe des indicateurs de succès financiers et d’audience : Budget, Revenue et Popularité", className="countries-card-label", style={'textAlign': 'center'}  )
group1_description = html.P(
    "Les données montrent une chose très claire : plus un film a un budget élevé, plus il a de chances de générer des revenus importants. La corrélation entre le budget et le revenu est forte (0.71). Mais l’argent ne fait pas tout. La popularité — un indicateur de visibilité ou d'engouement du public — est elle aussi bien corrélée au revenu (0.6) et au budget (0.43). Conclusion : un gros budget combiné à un bon niveau de buzz semble être un duo gagnant pour atteindre le succès commercial.",
    className='text-paragraph'
)
group1_graphs = html.Div(
    style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '20px'},
    children=[
        create_scatter("budget", "revenue"),
        create_scatter("budget", "popularity"),
        create_scatter("revenue", "popularity")
    ]
)

group2_header = html.H4("2 - Groupe des indicateurs de perception qualitative : Vote", className="countries-card-label", style={'textAlign': 'center'}  )
group2_description = html.P(
    "On pourrait croire qu’un film bien noté est forcément un film qui marche. Mais nos données racontent une autre histoire. La note moyenne n’a qu’une faible corrélation avec le revenu (0.19), et encore moins avec le budget (-0.03). Cela suggère qu’un film peut cartonner au box-office sans pour autant récolter des éloges du public ou des critiques. Conclusion : la qualité perçue est un facteur secondaire pour le succès immédiat. Un film “moyen” peut tout à fait trouver son public.",
    className='text-paragraph'
)
group2_graphs = html.Div(
    style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '20px'},
    children=[
        create_scatter("budget", "vote_average"),
        create_scatter("revenue", "vote_average"),
        create_scatter("popularity", "vote_average")
    ]
)

group3_header = html.H4("3 - Groupe des indicateurs de durée : Durée", className="countries-card-label", style={'textAlign': 'center'}  )
group3_description = html.P(
    "La durée des films est un indicateur qu’on pourrait croire plus influent. Pourtant, les chiffres montrent le contraire. Les corrélations entre la durée et les autres variables sont faibles (0.23 avec le budget et le revenu, 0.18 avec la popularité, 0.38 avec la note moyenne). Conclusion : la durée n’a pas d’impact direct fort. Elle peut jouer un rôle indirect, par exemple sur le nombre de séances ou le rythme d’un film, mais ce n’est pas un facteur déterminant en soi.",
    className='text-paragraph'
)
group3_graphs = html.Div(
    style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '20px'},
    children=[
        create_scatter("budget", "runtime"),
        create_scatter("revenue", "runtime"),
        create_scatter("popularity", "runtime"),
        create_scatter("vote_average", "runtime")
    ]
)

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
                html.Header(
                    className="main-header",
                    children=[
                        html.Div(
                            className="header-content",
                            children=[
                                html.H1("QUELS INGRÉDIENTS FONT LE SUCCÈS D'UN FILM ?", className="app-title"),
                                html.P("Une exploration des données financières, qualitatives et structurelles.", className="header-subtitle")
                            ]
                        )
                    ]
                ),
                html.Div(
                    className="main-content",
                    children=[
                        html.Div(
                            style={
                                'display': 'flex', 
                                'flexDirection': 'column', 
                                'justifyContent': 'space-between', 
                                'alignItems': 'center'
                            },
                        ),
                        html.Div(
                            style={'marginTop': '40px'},
                            children=[
                                group1_header,
                                group1_description,
                                group1_graphs,
                                html.Br(),
                                group2_header,
                                group2_description,
                                group2_graphs,
                                html.Br(),
                                group3_header,
                                group3_description,
                                group3_graphs,
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
