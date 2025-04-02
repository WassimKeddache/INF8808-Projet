# -*- coding: utf-8 -*-

"""
File name: app.py
Author: Olivia Gélinas
Course: INF8808
Python Version: 3.8

This file is the entry point for our dash app.
"""

import json
import re

import barchar_main
import barchar_mini
import dash
import pandas as pd
import plotly.graph_objects as go
import template
from dash import callback, dcc, html
from dash.dependencies import Input, Output

import preprocess

app = dash.Dash(__name__)
app.title = "Visu 4"

# Chargement des données
df = pd.read_csv("../data/combined.csv")

# Vérification et correction des valeurs de revenus
print("Vérification des données de revenus...")
print(f"Valeur maximale de revenue avant correction: {df['revenue'].max()}")
print(f"Valeur moyenne de revenue avant correction: {df['revenue'].mean()}")

# Convertir les colonnes numériques et vérifier les valeurs aberrantes
df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce")
df["vote_average"] = pd.to_numeric(df["vote_average"], errors="coerce")
df["popularity"] = pd.to_numeric(df["popularity"], errors="coerce")

# Correction des valeurs aberrantes pour les revenus (si nécessaire)
# Si les revenus sont en centimes au lieu de dollars, diviser par 100
if df["revenue"].max() > 10_000_000_000:  # Si le max est supérieur à 10 milliards
    print("Correction des valeurs de revenus (conversion en dollars)...")
    df["revenue"] = df["revenue"] / 100
    print(f"Nouvelle valeur maximale de revenue: {df['revenue'].max()}")
    print(f"Nouvelle valeur moyenne de revenue: {df['revenue'].mean()}")


# Fonctions d'extraction améliorées pour gérer les JSON malformés
def clean_json_string(json_str):
    """Nettoie une chaîne JSON potentiellement malformée"""
    if pd.isna(json_str):
        return "[]"

    # Remplacer les doubles guillemets consécutifs par des guillemets simples
    json_str = json_str.replace('""', '"')

    # S'assurer que la chaîne commence et se termine par des crochets
    if not json_str.startswith("["):
        json_str = "[" + json_str
    if not json_str.endswith("]"):
        json_str = json_str + "]"

    # Essayer de corriger les problèmes courants
    try:
        # Tenter de parser le JSON pour voir s'il est valide
        json.loads(json_str)
        return json_str
    except json.JSONDecodeError:
        # Si le parsing échoue, retourner une liste vide
        print(f"JSON malformé, impossible à corriger: {json_str[:50]}...")
        return "[]"


def extract_cast(cast_json):
    """Extrait les 5 premiers acteurs du JSON de casting avec gestion d'erreurs améliorée"""
    try:
        if pd.isna(cast_json):
            return []

        # Utiliser une approche par expression régulière pour extraire les informations
        # Cette méthode est plus robuste face aux JSON malformés
        actors = []

        # Nettoyer la chaîne JSON
        cleaned_json = clean_json_string(cast_json)

        try:
            # Essayer de parser le JSON nettoyé
            cast_list = json.loads(cleaned_json)

            # Extraire les informations des acteurs (seulement les 5 premiers)
            for i, actor in enumerate(cast_list):
                if i >= 5:  # Limiter à 5 acteurs par film
                    break
                if isinstance(actor, dict) and "name" in actor and "id" in actor:
                    actors.append({"id": actor.get("id"), "name": actor.get("name")})

            return actors
        except json.JSONDecodeError:
            # Si le parsing échoue malgré le nettoyage, utiliser regex
            # Rechercher les motifs de nom et d'ID dans la chaîne
            name_pattern = r'"name":\s*"([^"]+)"'
            id_pattern = r'"id":\s*(\d+)'

            names = re.findall(name_pattern, cast_json)
            ids = re.findall(id_pattern, cast_json)

            # Associer les noms et les IDs si possible (seulement les 5 premiers)
            for i in range(min(len(names), len(ids), 5)):  # Limiter à 5 acteurs
                actors.append({"id": int(ids[i]), "name": names[i]})

            return actors
    except Exception as e:
        print(f"Erreur lors de l'extraction du cast (méthode alternative): {str(e)}")
        return []


def extract_directors(crew_json):
    """Extrait les réalisateurs du JSON d'équipe avec gestion d'erreurs améliorée"""
    try:
        if pd.isna(crew_json):
            return []

        # Nettoyer la chaîne JSON
        cleaned_json = clean_json_string(crew_json)

        try:
            # Essayer de parser le JSON nettoyé
            crew_list = json.loads(cleaned_json)

            # Filtrer pour n'obtenir que les réalisateurs
            directors = [
                {"id": member.get("id"), "name": member.get("name")}
                for member in crew_list
                if isinstance(member, dict)
                and member.get("job") == "Director"
                and "name" in member
                and "id" in member
            ]

            return directors
        except json.JSONDecodeError:
            # Si le parsing échoue malgré le nettoyage, utiliser regex
            # Rechercher les motifs de réalisateur dans la chaîne
            director_pattern = (
                r'"job":\s*"Director"[^}]*"name":\s*"([^"]+)"[^}]*"id":\s*(\d+)'
            )
            directors_matches = re.findall(director_pattern, crew_json)

            directors = []
            for name, id_str in directors_matches:
                directors.append({"id": int(id_str), "name": name})

            return directors
    except Exception as e:
        print(
            f"Erreur lors de l'extraction des réalisateurs (méthode alternative): {str(e)}"
        )
        return []


def extract_studios(companies_json):
    """Extrait les studios du JSON de compagnies avec gestion d'erreurs améliorée"""
    try:
        if pd.isna(companies_json):
            return []

        # Nettoyer la chaîne JSON
        cleaned_json = clean_json_string(companies_json)

        try:
            # Essayer de parser le JSON nettoyé
            companies_list = json.loads(cleaned_json)

            # Extraire les informations des studios
            studios = [
                {"id": company.get("id"), "name": company.get("name")}
                for company in companies_list
                if isinstance(company, dict) and "name" in company and "id" in company
            ]

            return studios
        except json.JSONDecodeError:
            # Si le parsing échoue malgré le nettoyage, utiliser regex
            # Rechercher les motifs de studio dans la chaîne
            studio_pattern = r'"name":\s*"([^"]+)"[^}]*"id":\s*(\d+)'
            studio_matches = re.findall(studio_pattern, companies_json)

            studios = []
            for name, id_str in studio_matches:
                studios.append({"id": int(id_str), "name": name})

            return studios
    except Exception as e:
        print(
            f"Erreur lors de l'extraction des studios (méthode alternative): {str(e)}"
        )
        return []


# Application des fonctions d'extraction avec gestion d'erreurs
print("Extraction des données de casting (5 premiers acteurs par film)...")
df["cast_list"] = df["cast"].apply(extract_cast)
print("Extraction des données de réalisateurs...")
df["directors_list"] = df["crew"].apply(extract_directors)
print("Extraction des données de studios...")
df["studios_list"] = df["production_companies"].apply(extract_studios)

# Explode des données pour avoir une ligne par acteur/réalisateur/studio
print("Traitement des données d'acteurs...")
actors_df = df.explode("cast_list")
actors_df = actors_df[actors_df["cast_list"].notna()]
actors_df["entity_id"] = actors_df["cast_list"].apply(
    lambda x: x.get("id") if isinstance(x, dict) else None
)
actors_df["entity_name"] = actors_df["cast_list"].apply(
    lambda x: x.get("name") if isinstance(x, dict) else None
)
actors_df = actors_df[actors_df["entity_name"].notna()]

print("Traitement des données de réalisateurs...")
directors_df = df.explode("directors_list")
directors_df = directors_df[directors_df["directors_list"].notna()]
directors_df["entity_id"] = directors_df["directors_list"].apply(
    lambda x: x.get("id") if isinstance(x, dict) else None
)
directors_df["entity_name"] = directors_df["directors_list"].apply(
    lambda x: x.get("name") if isinstance(x, dict) else None
)
directors_df = directors_df[directors_df["entity_name"].notna()]

print("Traitement des données de studios...")
studios_df = df.explode("studios_list")
studios_df = studios_df[studios_df["studios_list"].notna()]
studios_df["entity_id"] = studios_df["studios_list"].apply(
    lambda x: x.get("id") if isinstance(x, dict) else None
)
studios_df["entity_name"] = studios_df["studios_list"].apply(
    lambda x: x.get("name") if isinstance(x, dict) else None
)
studios_df = studios_df[studios_df["entity_name"].notna()]


# Agrégation des données pour calculer les métriques moyennes par entité
def aggregate_data(entity_df):
    """Agrège les données par entité et calcule les métriques moyennes"""
    # S'assurer que les colonnes numériques sont du bon type
    for col in ["revenue", "vote_average", "popularity"]:
        entity_df[col] = pd.to_numeric(entity_df[col], errors="coerce")

    # Grouper par entité et calculer les métriques moyennes
    agg_df = (
        entity_df.groupby(["entity_id", "entity_name"])
        .agg(
            {
                "revenue": "mean",  # Revenu moyen par film
                "vote_average": "mean",  # Note moyenne
                "popularity": "mean",  # Popularité moyenne
                "title": "count",  # Nombre de films
            }
        )
        .reset_index()
    )

    # Renommer les colonnes pour plus de clarté
    agg_df.rename(
        columns={
            "revenue": "avg_revenue",
            "vote_average": "avg_rating",
            "popularity": "avg_popularity",
            "title": "film_count",
        },
        inplace=True,
    )

    return agg_df


# Agréger les données pour chaque type d'entité
print("Agrégation des données d'acteurs...")
actors_agg = aggregate_data(actors_df)
print("Agrégation des données de réalisateurs...")
directors_agg = aggregate_data(directors_df)
print("Agrégation des données de studios...")
studios_agg = aggregate_data(studios_df)

# Filtrer pour ne garder que les entités ayant participé à au moins 10 films
min_films = 10
actors_agg = actors_agg[actors_agg["film_count"] >= min_films]
directors_agg = directors_agg[directors_agg["film_count"] >= min_films]
studios_agg = studios_agg[studios_agg["film_count"] >= min_films]

print(f"Nombre d'acteurs après filtrage (min {min_films} films): {len(actors_agg)}")
print(
    f"Nombre de réalisateurs après filtrage (min {min_films} films): {len(directors_agg)}"
)
print(f"Nombre de studios après filtrage (min {min_films} films): {len(studios_agg)}")

# Vérification des valeurs moyennes de revenus
print(
    f"Revenu moyen max pour les acteurs: ${actors_agg['avg_revenue'].max()/1000000:.2f}M"
)
print(
    f"Revenu moyen max pour les réalisateurs: ${directors_agg['avg_revenue'].max()/1000000:.2f}M"
)
print(
    f"Revenu moyen max pour les studios: ${studios_agg['avg_revenue'].max()/1000000:.2f}M"
)


app.layout = html.Div(
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
                            id="chart-info",
                            style={"margin-top": "20px", "text-align": "center"},
                        ),
                    ],
                ),
                # Zone mini vis
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
                        dcc.Graph(id="mini-bar-chart", style={"height": "70vh"}),
                        html.Div(
                            id="mini-chart-info",
                            style={"margin-top": "20px", "text-align": "center"},
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
        Output("chart-info", "children"),
        Output("data-info", "children"),
    ],
    [
        Input("entity-type", "value"),
        Input("success-metric", "value"),
        Input("main-bar-chart", "clickData"),
    ],
)
def update_selection(entity_type, metric, click_data):
    # Use callback_context to determine which input triggered the callback
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None

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
        count = 150
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
                hovertext=["TEST"],
                marker_color=colors[i],
                textposition="outside",
                textfont_size=10,
                width=0.8,
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

    if trigger_id == "main-bar-chart" and click_data is not None:
        mini_fig = go.Figure()

        entity_name = click_data["points"][0]["label"]
        # entity_id FIND ENTITY ID FROM ACTOR

        print(f"Entity name : {entity_name}\nEntity ID : {entity_id}")

        actor_movies = actors_df[actors_df["entity_id"] == entity_id].sort_values(
            by="vote_average", ascending=False
        )

        movie_titles = actor_movies["title"].tolist()
        movie_revenues = actor_movies["revenue"].tolist()

        for j, (title, revenue) in enumerate(zip(movie_titles, movie_revenues)):
            mini_fig.add_trace(
                go.Bar(
                    x=[title],
                    y=[revenue],
                    text=[row["formatted_value"]],
                    hoverinfo="text",
                    hovertext=[f"<b> Revenu total :<b> {revenue}"],
                    marker_color=colors[i],
                    textposition="outside",
                    textfont_size=10,
                    width=0.8,
                    name=entity_name,
                )
            )
        # Update mini chart layout
        mini_title = f"Liste de revenu pour l'acteur : {entity_name}"
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
        mini_fig = barchar_mini.get_empty_figure()

    return (fig, mini_fig, chart_info, data_info)


if __name__ == "__main__":
    app.run(debug=True)
