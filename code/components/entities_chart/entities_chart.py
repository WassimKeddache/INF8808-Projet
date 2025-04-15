import dash
from dash import html, dcc, callback
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from .barchar_mini import get_empty_figure
from .barchar_mini import get_graph_info
from .entities_chart_data import data_instance

def get_chart():
    return html.Div(
        className='dashboard-card',
        children=[
            # En-tête
            html.Div(
                className='entity-bar-content',
                children=[
                    # Panneau de contrôle
                    # Zone de visualisation
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
                    # Zone mini vis
                    html.Div(
                        className='entity-bar-card',
                        children=[
                            dcc.Graph(
                                className="entity-bar-container",
                                id="mini-bar-chart", style={"height": "70vh"}),
                            # Selection de l'ordre
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
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None
    min_films = 10

    data = data_instance.get_data()

    actors_agg = data["actors_agg"]
    directors_agg = data["directors_agg"]
    studios_agg = data["studios_agg"]

    actors_df = data["actors_df"]
    directors_df = data["directors_df"]
    studios_df = data["studios_df"]

    if entity_type == "actors":
        df_to_use = actors_agg
        entity_type_display = "Acteurs"
        note_text = ""
        # Montrer les top 150 acteurs
        count = 150
    elif entity_type == "directors":
        df_to_use = directors_agg
        entity_type_display = "Réalisateurs"
        note_text = ""
        count = 30
    else:  # studios
        df_to_use = studios_agg
        entity_type_display = "Studios"
        note_text = ""
        count = 150

    # Trier les données par la métrique sélectionnée (en ordre décroissant)
    sorted_df = df_to_use.sort_values(by=metric, ascending=False)

    # Prendre les N premières entités
    top_entities = sorted_df.head(count)

    # Formatage des valeurs pour l'affichage
    if metric == "avg_revenue":
        y_title = "Revenu moyen par film ($)"
        top_entities["formatted_value"] = top_entities[metric].apply(
            lambda x: f"${x/1000000:.2f}M"
        )
        hover_template = "%{y:$.2f}"
        metric_display = "revenu moyen"
    else:  # avg_rating
        y_title = "Note moyenne (/10)"
        top_entities["formatted_value"] = top_entities[metric].apply(
            lambda x: f"{x:.1f}/10"
        )
        hover_template = "%{y:.1f}/10"
        metric_display = "note moyenne"

    # Créer le graphique à barres
    title = f"Top {count} {entity_type_display} {note_text} par {metric_display} (min. {min_films} films)"

    # Génération d'une palette de couleurs dégradée

    # Créer le graphique à barres
    fig = go.Figure()

    for i, (_, row) in enumerate(top_entities.iterrows()):
        entity_id = row["entity_id"]
        entity_name = row["entity_name"]

        fig.add_trace(
            go.Bar(
                x=[entity_name],
                y=[row[metric]],
                hoverinfo="text",
                hovertext=[f"<b>{entity_name}<b>"],
                marker_color='#006084',
                textposition=None,
                textfont_size=10,
                width=1,
                name=entity_name,
            )
        )

    fig.update_layout(
        title={
            "text": title,
            "y": 0.95,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
            'font': {
                'color': '#006084',
            },
        },
        xaxis={
            "title": f"{entity_type_display}",
            "tickangle": -45,
            "showticklabels": False,
            "categoryorder": "total descending",
        },
        yaxis={
            "title": y_title,
            "zeroline": True,
            "zerolinewidth": 1,
            "zerolinecolor": "lightgray",
            "gridcolor": "lightgray",
        },
        plot_bgcolor="white",
        hoverlabel = dict(
            bgcolor="#ECE9E1",
            font_size=14,
            font_family="system-ui",
            font_color="#006084",
            bordercolor="#006084",
        ),
        uniformtext_minsize=8,
        uniformtext_mode="hide",
        height=600,
        showlegend=False,
        hovermode="closest",
    )


    if trigger_id == "success-metric":
        entity_name = None

    if (trigger_id == "main-bar-chart" and click_data is not None) or (
        trigger_id == "mini-order" and actor_selected != None
    ):
        mini_fig = go.Figure()

        if trigger_id == "main-bar-chart":
            entity_name = click_data["points"][0]["label"]
        else:
            entity_name = actor_selected

        actor_selected = entity_name

        if entity_type == "actors":
            df_to_use = actors_df
            mini_title = f"Liste de revenu pour l'acteur : {entity_name}"
        elif entity_type == "directors":
            df_to_use = directors_df
            mini_title = f"Liste de revenu pour le directeur : {entity_name}"
        else:  # studios
            df_to_use = studios_df
            mini_title = f"Liste de revenu pour le studio : {entity_name}"

        elems = get_graph_info(df_to_use, mini_order, entity_name)

        movie_titles = elems["title"].tolist()
        movie_revenues = elems["revenue"].tolist()
        movie_release_date = elems["release_date"].tolist()

        for j, (title, revenue, release_date) in enumerate(
            zip(movie_titles, movie_revenues, movie_release_date)
        ):
            annee = int(release_date.split("-")[0])

            info_to_show = (
                "{display_revenue:.2f}M".format(display_revenue=revenue / 1000000)
                if mini_order == "revenue"
                else annee
            )

            mini_fig.add_trace(
                go.Bar(
                    x=[title],
                    y=[revenue],
                    text=[info_to_show],
                    hoverinfo="text",
                    hovertext=[
                        " <b> {display_title} <b> <br>".format(display_title=title)
                        + "<b> Revenu total :</b> {display_revenue:.2f} M <br>".format(
                            display_revenue=revenue / 1000000
                        )
                        + "<b> Année :</b> {year} <br>".format(year=annee)
                    ],
                    hoverlabel = dict(
                        bgcolor="#ECE9E1",
                        font_size=14,
                        font_family="system-ui",
                        font_color="#006084",
                        bordercolor="#006084",
                    ),
                    marker_color='#006084',
                    textposition="outside",
                    textfont_size=10,
                    width=0.8,
                    name=entity_name,
                )
            )
        # Update mini chart layout
        mini_fig.update_layout(
            title={
                "text": mini_title,
                "y": 0.95,
                "x": 0.5,
                "xanchor": "center",
                "yanchor": "top",
                'font': {
                    'color': '#006084',
                },  
            },
            xaxis={
                "title": "",
                "tickangle": -45,
                "tickfont": {"size": 10},
            },
            yaxis={
                "title": "Revenu ($)",
                "zeroline": True,
                "zerolinewidth": 1,
                "zerolinecolor": "lightgray",
                "gridcolor": "lightgray",
            },
            plot_bgcolor="white",
            height=600,
            showlegend=False,
        )

    else:
        mini_fig = get_empty_figure()

    fig.update_xaxes(title_font_family="system-ui")
    fig.update_yaxes(title_font_family="system-ui")
    mini_fig.update_xaxes(title_font_family="system-ui")
    mini_fig.update_yaxes(title_font_family="system-ui")

    return (fig, mini_fig, actor_selected)


def get_entities_chart():
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