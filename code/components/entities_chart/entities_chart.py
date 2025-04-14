import dash
from dash import html, dcc, callback
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from .barchar_mini import get_empty_figure
from .barchar_mini import get_graph_info
from .entities_chart_data import data_instance

def get_entities_chart():
    return html.Div(
        style={"font-family": "Arial, sans-serif", "margin": "0", "padding": "0"},
        children=[
            # En-tête
            html.Header(
                style={
                    "background-color": "#2c3e50",
                    "color": "white",
                    "padding": "20px",
                    "text-align": "center",
                },
                children=[
                    html.H1(
                        "Impact des Acteurs, Réalisateurs et Studios sur le Succès des Films",
                        style={"margin": "0"},
                    ),
                    html.P(
                        "Analyse comparative des performances basée sur différentes métriques",
                        style={"margin-top": "10px"},
                    ),
                ],
            ),
            # Conteneur principal
            html.Div(
                style={"display": "flex", "flex-wrap": "wrap", "padding": "20px"},
                children=[
                    # Panneau de contrôle
                    html.Div(
                        style={
                            "width": "300px",
                            "padding": "20px",
                            "background-color": "#f8f9fa",
                            "border-radius": "5px",
                            "box-shadow": "0 2px 4px rgba(0,0,0,0.1)",
                            "margin-right": "20px",
                        },
                        children=[
                            html.H3("Paramètres de Visualisation"),
                            # Sélection du type d'entité
                            html.Div(
                                style={"margin-bottom": "20px"},
                                children=[
                                    html.Label("Type d'entité:"),
                                    dcc.RadioItems(
                                        id="entity-type",
                                        options=[
                                            {
                                                "label": "Acteurs (5 premiers par film)",
                                                "value": "actors",
                                            },
                                            {"label": "Réalisateurs", "value": "directors"},
                                            {"label": "Studios", "value": "studios"},
                                        ],
                                        value="actors",
                                        labelStyle={"display": "block", "margin": "10px 0"},
                                    ),
                                ],
                            ),
                            # Sélection de la métrique
                            html.Div(
                                style={"margin-bottom": "20px"},
                                children=[
                                    html.Label("Métrique de succès:"),
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
                                        labelStyle={"display": "block", "margin": "10px 0"},
                                    ),
                                ],
                            ),
                            # Informations sur les données
                            html.Div(
                                id="data-info",
                                style={"margin-top": "20px", "font-size": "14px"},
                            ),
                        ],
                    ),
                    # Zone de visualisation
                    html.Div(
                        style={
                            "flex": "1",
                            "min-width": "600px",
                            "background-color": "white",
                            "border-radius": "5px",
                            "box-shadow": "0 2px 4px rgba(0,0,0,0.1)",
                            "padding": "20px",
                        },
                        children=[
                            dcc.Graph(id="main-bar-chart", style={"height": "70vh"}),
                            html.Div(
                                id="entities-chart-info",
                                style={"margin-top": "20px", "text-align": "center"},
                            ),
                        ],
                    ),
                    # Zone mini vis
                    html.Div(
                        style={"display": "flex", "flex-wrap": "wrap", "padding": "20px"},
                        children=[
                            html.Div(
                                style={
                                    "flex": "1",
                                    "min-width": "600px",
                                    "background-color": "white",
                                    "border-radius": "5px",
                                    "box-shadow": "0 2px 4px rgba(0,0,0,0.1)",
                                    "padding": "20px",
                                },
                                children=[
                                    dcc.Graph(
                                        id="mini-bar-chart", style={"height": "70vh"}
                                    ),
                                    html.Div(
                                        id="mini-chart-info",
                                        style={
                                            "margin-top": "20px",
                                            "text-align": "center",
                                        },
                                    ),
                                ],
                            ),
                            # Selection de l'ordre
                            html.Div(
                                style={"margin-bottom": "20px"},
                                children=[
                                    html.Textarea(
                                        id="actor-selected",
                                        style={"text-align": "center"},
                                    ),
                                    html.Label("Ordre des films:"),
                                    dcc.RadioItems(
                                        id="mini-order",
                                        options=[
                                            {
                                                "label": "Revenus",
                                                "value": "revenue",
                                            },
                                            {
                                                "label": "Date de sortie",
                                                "value": "date",
                                            },
                                        ],
                                        value="revenue",
                                        labelStyle={"display": "block", "margin": "10px 0"},
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            # Graphique caché pour histogramme des films d'un acteur
            html.Div(id="actor-movies-container", style={"display": "none"}),
        ],
    )

@callback(
    [
        Output("main-bar-chart", "figure"),
        Output("mini-bar-chart", "figure"),
        Output("entities-chart-info", "children"),
        Output("data-info", "children"),
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
        note_text = "(5 premiers par film)"
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

    # Décider si on affiche les noms sur l'axe X
    show_tick_labels = count <= 30

    # Génération d'une palette de couleurs dégradée
    colors = [f"rgba(66, 133, 244, {1 - (i/count)*0.7})" for i in range(count)]

    # Créer le graphique à barres
    fig = go.Figure()

    for i, (_, row) in enumerate(top_entities.iterrows()):
        entity_id = row["entity_id"]
        entity_name = row["entity_name"]

        fig.add_trace(
            go.Bar(
                x=[entity_name],
                y=[row[metric]],
                text=[row["formatted_value"]],
                hoverinfo="text",
                hovertext=[f"<b>{entity_name}<b>"],
                marker_color=colors[i],
                textposition="outside",
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
        },
        xaxis={
            "title": "",
            "tickangle": -45,
            "showticklabels": show_tick_labels,
            "tickfont": {"size": 10},
            "categoryorder": "total descending",
        },
        yaxis={
            "title": y_title,
            "zeroline": True,
            "zerolinewidth": 1,
            "zerolinecolor": "lightgray",
            "gridcolor": "lightgray",
        },
        margin={"l": 50, "r": 20, "b": 100 if show_tick_labels else 50, "t": 100},
        plot_bgcolor="white",
        hoverlabel={
            "bgcolor": "white",
            "font_size": 12,
        },
        uniformtext_minsize=8,
        uniformtext_mode="hide",
        height=600,
        showlegend=False,
        hovermode="closest",
    )

    # Si plus de 30 entités, cacher les noms mais garder l'effet visuel
    if not show_tick_labels:
        fig.add_annotation(
            text="Plus de 30 entités affichées : les noms sont masqués pour éviter l'encombrement",
            xref="paper",
            yref="paper",
            x=0.5,
            y=-0.15,
            showarrow=False,
            font=dict(size=12, color="gray"),
        )

    # Informations sur le graphique
    chart_info = html.Div(
        [
            html.P(
                f"Ce graphique montre les {count} {entity_type_display.lower()} avec le {metric_display} le plus élevé"
            ),
            html.P(
                f"Seules les entités ayant participé à au moins {min_films} films sont incluses"
            ),
        ]
    )

    # Informations sur les données
    data_info = html.Div(
        [
            html.P(
                f"Total {entity_type_display.lower()} avec ≥{min_films} films: {len(df_to_use)}"
            ),
            html.P(f"Valeur maximale: {sorted_df[metric].max():.2f}"),
            html.P(f"Valeur minimale: {sorted_df[metric].min():.2f}"),
            html.P(f"Valeur moyenne: {sorted_df[metric].mean():.2f}"),
        ]
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
                        + "<b> Year :</b> {year} <br>".format(year=annee)
                    ],
                    marker_color=colors[i],
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
            margin={"l": 50, "r": 20, "b": 150, "t": 100},
            plot_bgcolor="white",
            height=600,
            showlegend=False,
        )

    else:
        mini_fig = get_empty_figure()

    return (fig, mini_fig, chart_info, data_info, actor_selected)