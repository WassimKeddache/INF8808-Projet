import dash
from dash import html, dcc, callback
from dash.dependencies import Input, Output, State
from . import callbacks

@callback(
    [Output('budget-heatmap', 'figure'),
     Output('metric-heatmap', 'figure')],
    [Input('metric-selector', 'value')]
)
def update_heatmaps(selected_metric):
    """
    Met à jour les heatmaps du budget et de la métrique sélectionnée.
    """
    budget_fig, metric_fig = callbacks.update_heatmaps(selected_metric)
    return budget_fig, metric_fig

@callback(
    [Output('hover-info', 'children')],
    [Input('budget-heatmap', 'hoverData'),
     Input('metric-heatmap', 'hoverData')],
    [State('metric-selector', 'value')]
)
def update_hover_info(budget_hover_data, metric_hover_data, selected_metric):
    """
    Met à jour les informations affichées lors du survol des heatmaps.
    """
    hover_info = callbacks.update_hover_info(budget_hover_data, metric_hover_data, selected_metric)
    return hover_info

def get_chart():
    """
    Génère le composant principal contenant les heatmaps et les contrôles associés.
    """
    return html.Div(className='content', children=[
        html.Div(className='dashboard-card', children=[
            html.Div(className='card-content', children=[
                html.Div(className='heatmaps-container', children=[
                    dcc.Graph(
                        id='budget-heatmap',
                        config={'displayModeBar': False},
                        className='heatmap-graph'
                    ),
                    
                    dcc.Graph(
                        id='metric-heatmap',
                        config={'displayModeBar': False},
                        className='heatmap-graph'
                    )
                ]),
                html.Div(
                    className='heatmap-legend',
                    children=[
                        html.Div(style={
                            'width': '15px',
                            'height': '15px',
                            'backgroundColor': '#f2f2f2',
                            'marginRight': '6px',
                            'border': '1px solid #aaa'
                        }),
                        html.Span("= Aucune donnée")
                    ]
                ),
                html.Div(className='controls-and-info-row', children=[
                    html.Div(id='hover-info'),
                    html.Div(className='metric-selector-container', children=[
                        dcc.RadioItems(
                            id='metric-selector',
                            options=[
                                {'label': 'Revenu moyen', 'value': 'revenue'},
                                {'label': 'Vote moyen', 'value': 'vote_average'}
                            ],
                            value='revenue',
                            className='radio-group',
                            inputClassName='radio-input',
                            labelClassName='radio-label'
                        )
                    ]),
                ]),
            ]),
        ]),
        
        dcc.Store(id='heatmap-data-store')
    ])


def get_heatmap_budget():
    """
    Génère le composant principal pour la visualisation des heatmaps de budget et métriques,
    accompagné d'une description textuelle et des contrôles interactifs.
    """
    return html.Div(
        className='text',
        children=[
            html.H1(
                "GENRE ET BUDGET",
                className='text-title'
            ),
            html.P(
                """
                On cherche à comprendre si le genre d’un film ainsi que son budget jouent un rôle central dans son succès. 
                Cette visualisation explore leur évolution dans le temps et leur lien avec les performances critiques et financières.
                """,
                className='text-paragraph'
            ),
            get_chart(),
            html.P(
                """
                On observe une tendance générale à allouer des budgets plus importants aux films au fil des décennies. 
                Les genres comme l’aventure, l’action, la famille, la science-fiction et le fantastique bénéficient d’une croissance marquée de leur budget, 
                accompagnée d’une évolution positive de leurs revenus moyens, ce qui suggère un lien entre investissement financier et succès commercial. 
                Toutefois, certains films réussissent à générer des revenus élevés malgré un budget réduit, notamment dans les genres horreur (1973, 1975), 
                thriller (1975), famille (1982), et animation (1992, 1994, 1995). En revanche, les votes moyens restent relativement stables à travers les genres et les années, 
                indiquant une appréciation critique plus uniforme.
                """,
                className='text-paragraph'
            ),
        ]
    )
