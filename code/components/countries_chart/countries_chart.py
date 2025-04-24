from dash import html, dcc, callback
from dash.dependencies import Input, Output
from .countries_chart_data import data_instance
from . import callbacks


def get_chart():
    """
    Génère le composant principal du graphique des pays avec filtres et critères.
    """
    return html.Div(className='content', children=[
        html.Div(className='dashboard-card', children=[
            html.Div(className='countries-card-content', children=[
                html.Div( className='countries-card-pannel', children=[
                        
                        html.Div(children=[
                            html.H3('Critères de Succès', className='countries-card-label'),
                            dcc.RadioItems(
                                id='success-criteria',
                                options=[
                                    {'label': 'Revenu > 10M$', 'value': 'revenue'},
                                    {'label': 'Note > 7', 'value': 'vote_average'}
                                ],
                                value='revenue',
                                inputClassName='radio-input',
                                labelClassName='radio-label'
                            )
                        ]),
                        html.Div(children=[
                            html.Label('Filtrer par genre', className='countries-card-label'),
                            dcc.Dropdown(
                                id='genre-filter',
                                options=[{'label': genre, 'value': genre} for genre in data_instance.get_data()['all_genres']],
                                value=None,
                                placeholder='Tous les genres'
                            )
                        ]),
                        
                    ]
                ),
                html.Div(
                    className='countries-chart-container',
                    children=[
                        dcc.Graph(
                            id='bar-chart',
                            style={'height': '70vh'},
                            config={'displayModeBar': True}
                        ),
                    ]
                )
            ])
        ])
    ])

@callback(
    [Output('bar-chart', 'figure')],
    [Input('success-criteria', 'value'),
     Input('genre-filter', 'value')]
)
def update_bar_chart(criteria, selected_genre):
    """
    Met à jour le graphique à barres en fonction du critère de succès et du genre sélectionné.
    """
    fig = callbacks.update_bar_chart(criteria, selected_genre)
    return fig

def get_countries_chart():
    """
    Génère le composant complet pour la visualisation des films par pays, 
    incluant les filtres, critères et explications.
    """
    return html.Div(
        className='text',
        children=[
            html.H1(
                "ORIGINE",
                className='text-title'
            ),
            html.P(
                """
                Cette visualisation présente un diagramme à barres horizontales permettant d'analyser le nombre de films par pays répondant à deux critères : 
                un revenu minimum de 10 millions et une note minimum de 7. L'utilisateur peut également filtrer par genre pour observer la répartition des films par pays 
                en fonction de leur genre spécifique. Le total des genres n'est pas complémentaire, car plusieurs films peuvent avoir plusieurs genres.
                """,
                className='text-paragraph'
            ),
            get_chart(),
            html.P(
                """
                Cette visualisation permet de mettre en évidence l'impact potentiel de l'origine d'un film sur son succès. 
                En effet, la grande majorité des films répondant aux critères sont américains, ce qui souligne la domination des États-Unis dans l'industrie cinématographique. 
                Viennent ensuite les films britanniques et allemands. Une observation intéressante est que les films américains qui respectent ces critères sont majoritairement des comédies, 
                avec un nombre nettement plus élevé de films de comédie générant des revenus supérieurs à 10 millions par rapport aux films d'action, même lorsque l'on prend en compte la note. 
                Cela suggère que le genre d'un film, ainsi que son pays d'origine, peuvent avoir une influence considérable sur son succès.
                """,
                className='text-paragraph'
            ),
        ]
    )
