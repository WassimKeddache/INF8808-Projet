from dash import html, dcc, callback
from dash.dependencies import Input, Output
from . import callbacks

def get_chart():
    """
    Génère le composant principal pour afficher les graphiques et analyses des entités (acteurs, réalisateurs, studios).
    """
    return html.Div(
        className='dashboard-card',
        children=[
            html.Div(
                className='entity-bar-content',
                children=[
                    html.Div(
                        className='entity-bar-card',
                        children=[
                            dcc.Graph(id="main-bar-chart", 
                                      className="entity-bar-container"),
                            html.Div(
                                className='main-entity-bar-pannel',
                                children=[
                                    html.Div(
                                        children=[
                                            dcc.RadioItems(
                                                id="entity-type",
                                                options=[
                                                    {
                                                        "label": "Acteurs",
                                                        "value": "actors",
                                                    },
                                                    {"label": "Réalisateurs", "value": "directors"},
                                                    {"label": "Studios", "value": "studios"},
                                                ],
                                                value="actors",
                                                inputClassName='radio-input',
                                                labelClassName='radio-label'
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        children=[
                                            dcc.RadioItems(
                                                id="success-metric",
                                                options=[
                                                    {
                                                        "label": "Revenu moyen par film",
                                                        "value": "avg_revenue",
                                                    },
                                                    {
                                                        "label": "Note moyenne",
                                                        "value": "avg_rating",
                                                    },
                                                ],
                                                value="avg_revenue",
                                                inputClassName='radio-input',
                                                labelClassName='radio-label'
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                    html.Div(
                        className='entity-bar-card',
                        children=[
                            dcc.Graph(
                                className="entity-bar-container",
                                id="mini-bar-chart", style={"height": "70vh"}),
                            html.Div(
                                className='mini-entity-bar-pannel',
                                children=[
                                    html.P(
                                        id="actor-selected",
                                        style={
                                            "display": "none",
                                        }),
                                    html.H3('Ordre', className='countries-card-label'),
                                    dcc.RadioItems(
                                        id="mini-order",
                                        options=[
                                            {
                                                "label": "Revenue",
                                                "value": "revenue",
                                            },
                                            {
                                                "label": "Date de sortie",
                                                "value": "date",
                                            },
                                        ],
                                        value="revenue",
                                        inputClassName='radio-input',
                                        labelClassName='radio-label'
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )

@callback(
    [
        Output("main-bar-chart", "figure"),
        Output("mini-bar-chart", "figure"),
        Output("actor-selected", "value"),
    ],
    [
        Input("entity-type", "value"),
        Input("success-metric", "value"),
        Input("main-bar-chart", "clickData"),
        Input("mini-order", "value"),
        Input("actor-selected", "value"),
    ],
)
def update_selection(entity_type, metric, click_data, mini_order, actor_selected):
    """
    Met à jour les graphiques et la sélection en fonction des interactions utilisateur.
    """
    figures = callbacks.update_selection(
        entity_type, metric, click_data, mini_order, actor_selected
    )
    return figures


def get_entities_chart():
    """
    Génère le composant principal pour afficher les graphiques et analyses des acteurs, réalisateurs et studios.
    """
    return html.Div(
        className='text',
        children=[
            html.H1(
                "ACTEURS, REALISATEURS ET STUDIOS",
                className='text-title'
            ),
            html.P(
                """
                On vise à explorer l’impact potentiel des acteurs, réalisateurs et studios de production sur le succès 
                d’un film, mesuré à travers le revenu moyen ou la note moyenne de leurs œuvres. Seules les entités (acteurs, réalisateurs et studios) ayant participé à au moins 10 films sont incluses
                Il est possible d'avoir plus d'informations sur la filmographie de l'entité en cliquant sur les barres du graphique.
                À première vue, on peut formuler l’hypothèse que les studios et les réalisateurs influencent 
                davantage le succès d’un film. Leur filmographie présente souvent une certaine constance dans les 
                revenus générés et les notes obtenues, contrairement aux acteurs dont l’impact semble plus variable 
                selon le projet.
                """,
                className='text-paragraph'
            ),
            get_chart(),
        ]
    )