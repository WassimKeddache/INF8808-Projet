import dash
from dash import html, dcc, callback
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime
import numpy as np
from .heatmap_budget_data import data_instance

def get_chart():
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

@callback(
    [Output('budget-heatmap', 'figure'),
     Output('metric-heatmap', 'figure')],
    [Input('metric-selector', 'value')]
)
def update_heatmaps(selected_metric):
    data = data_instance.get_heatmap_data()
    
    all_genre_names = data['all_genre_names']
    budget_min_avg = data['budget_min_avg']
    budget_max_avg = data['budget_max_avg']
    metric_ranges = data['metric_ranges']
    years = data['years']

    budget_df = data['budget_df']
    revenue_df = data['revenue_df']
    vote_df = data['vote_df']

    metric_df = vote_df if selected_metric == 'vote_average' else revenue_df
    
    tick_years = [year for year in years if (year - 1970) % 5 == 0]
    
    genre_order = all_genre_names
    
    budget_mask = np.array(budget_df['budget']) == 0
    metric_mask = np.array(metric_df[selected_metric]) == 0
    
    light_gray = "#f2f2f2"  # Gris clair
    
    budget_fig = go.Figure()
    
    budget_fig.add_trace(go.Heatmap(
        z=np.where(budget_mask, 1, np.nan),
        x=budget_df['release_date'],
        y=budget_df['genre'],
        colorscale=[[0, light_gray], [1, light_gray]],
        showscale=False,
        hoverinfo='skip'
    ))
    
    budget_fig.add_trace(go.Heatmap(
        z=np.where(budget_mask, np.nan, budget_df['budget']),
        x=budget_df['release_date'],
        y=budget_df['genre'],
        colorscale = [
            [0.0, "#b3d8e0"],
            [0.2, "#66b0c0"],
            [0.4, "#3390a0"],
            [0.6, "#0f6f84"],
            [1.0, "#006084"],
        ],
        zmin=budget_min_avg,
        zmax=budget_max_avg,
        customdata=np.stack((
            budget_df['genre'],
            budget_df['release_date'],
            budget_df['budget'],
            metric_df[selected_metric]
        ), axis=-1),
        hovertemplate='<b>%{customdata[0]}</b><br>Année: %{customdata[1]}<br>Budget: $%{customdata[2]:,.0f}<extra></extra>',
        hoverlabel=dict(
            bgcolor="#ECE9E1",
            font_size=14,
            font_family="system-ui",
            font_color='#006084',
            bordercolor='#006084',
        )
    ))
    
    budget_fig.update_layout(
        title= {
            'text': 'Budget moyen par genre (depuis 1970, par année)',
            'font': {
                'color': '#006084',
            },
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis=dict(
            title='Année',
            tickmode='array',
            tickvals=tick_years,
            ticktext=[str(year) for year in tick_years],
            tickangle=90
        ),
        yaxis=dict(
            categoryorder='array',
            categoryarray=genre_order,
            showticklabels=True,

            tickmode='array',
            tickvals=list(range(len(genre_order))),
            ticktext=genre_order
        ),
        coloraxis_colorbar=dict(
            title='Budget moyen (USD)'
        ),
        margin=dict(l=150, r=50, t=80, b=100),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="system-ui",
        )
    )
    
    metric_labels = {
        'revenue': 'Revenu moyen (USD)',
        'vote_average': 'Vote moyen'
    }
    
    color_scales = {
        'revenue': [
            [0.0, "#b3e0d4"],
            [0.2, "#66c0aa"],
            [0.4, "#33a188"],
            [0.6, "#0f866f"],
            [1.0, "#008466"],
        ],
        'vote_average': [
            [0.0, "#b3bbe0"],
            [0.2, "#6679c0"],
            [0.4, "#3346a1"],
            [0.6, "#101f93"],
            [1.0, "#001e84"],
        ]
    }
    
    metric_fig = go.Figure()
    
    metric_fig.add_trace(go.Heatmap(
        z=np.where(metric_mask, 1, np.nan),
        x=metric_df['release_date'],
        y=metric_df['genre'],
        colorscale=[[0, light_gray], [1, light_gray]],
        showscale=False,
        hoverinfo='skip'
    ))
    
    title_color = '#008466' if selected_metric == 'revenue' else '#001e84'

    metric_fig.add_trace(go.Heatmap(
        z=np.where(metric_mask, np.nan, metric_df[selected_metric]),
        x=metric_df['release_date'],
        y=metric_df['genre'],
        colorscale=color_scales[selected_metric],
        zmin=metric_ranges[selected_metric][0],
        zmax=metric_ranges[selected_metric][1],
        customdata=np.stack((
            metric_df['genre'],
            metric_df['release_date'],
            budget_df['budget'],
            metric_df[selected_metric]
        ), axis=-1),
        hovertemplate='<b>%{customdata[0]}</b><br>Année: %{customdata[1]}<br>' + 
                      (f'Vote: %{{customdata[3]:.2f}}' if selected_metric == 'vote_average' else f'Revenu: $%{{customdata[3]:,.0f}}') + 
                      '<extra></extra>',
        hoverlabel=dict(
            bgcolor="#ECE9E1",
            font_size=14,
            font_family="system-ui",
            font_color=title_color,
            bordercolor=title_color,
        )
    ))
    
    
    metric_fig.update_layout(
        title={
            'text': f'{metric_labels[selected_metric]} par genre (depuis 1970, par année)',
            'font': {
                'color': title_color,
            },
            'x': 0.5,
            'xanchor': 'center'
        },
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
            categoryarray=genre_order,
            showticklabels=False
        ),
        coloraxis_colorbar=dict(
            title=metric_labels[selected_metric]
        ),
        margin=dict(l=0, r=50, t=80, b=100),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="system-ui",
        )
    )
    budget_fig.update_xaxes(title_font_family="system-ui")
    budget_fig.update_yaxes(title_font_family="system-ui")
    metric_fig.update_yaxes(title_font_family="system-ui")
    metric_fig.update_xaxes(title_font_family="system-ui")

    
    return budget_fig, metric_fig

@callback(
    [Output('hover-info', 'children')],
    [Input('budget-heatmap', 'hoverData'),
     Input('metric-heatmap', 'hoverData')],
    [State('metric-selector', 'value')]
)
def update_hover_info(budget_hover, metric_hover, selected_metric):
    ctx = dash.callback_context

    default_hover = html.Div(
        className='heatmap-hover-info',
        children=[
            html.Div(
                className="heatmap-hover-label-container",
                children=[
                    html.Span("Sélectionnez une cellule pour voir les détails.", className="heatmap-hover-label"),
                    html.Span("", className="heatmap-hover-value"),
                    html.Span("", className="heatmap-hover-label"),
                    html.Span("", className="heatmap-hover-value"),
                ]
            ),
            html.Div(className="heatmap-hover-label-container", children=[
                html.Strong("", className="heatmap-hover-label"),
                html.Span("", className="heatmap-hover-value"),
                html.Strong("", className="heatmap-hover-label"),
                html.Span("", className="heatmap-hover-value")
            ])
        ]
    )
    
    if not ctx.triggered:
        return [default_hover]
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'budget-heatmap' and budget_hover:
        hover_data = budget_hover['points'][0]
    elif trigger_id == 'metric-heatmap' and metric_hover:
        hover_data = metric_hover['points'][0]
    else:
        return [default_hover]
    
    genre = hover_data['customdata'][0]
    year = int(hover_data['customdata'][1])
    budget = hover_data['customdata'][2]
    metric_value = hover_data['customdata'][3]
    
    metric_labels = {
        'revenue': 'Revenu moyen',
        'vote_average': 'Vote moyen'
    }
    
    hover_info = html.Div(
        className= 'heatmap-hover-info',
        children=
        [
            html.Div(
                className="heatmap-hover-label-container",
                children=[
                    html.Span("Genre:", className="heatmap-hover-label"),
                    html.Span(f"{genre}", className="heatmap-hover-value"),
                    html.Span("Année:", className="heatmap-hover-label"),
                    html.Span(f"{year}", className="heatmap-hover-value"),
                ]
            ),
            html.Div(className="heatmap-hover-label-container", children= [
                    html.Strong("Budget moyen: ", className="heatmap-hover-label"),
                    html.Span(f"{budget:,.2f} USD", className="heatmap-hover-value"),
                    html.Strong(f"{metric_labels[selected_metric]}: ", className="heatmap-hover-label"),
                    html.Span(f"{metric_value:,.2f}" + (" USD" if selected_metric == 'revenue' else ""), className="heatmap-hover-value")
            ])
        ]
    )
    
    return [hover_info]

def get_heatmap_budget():
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
