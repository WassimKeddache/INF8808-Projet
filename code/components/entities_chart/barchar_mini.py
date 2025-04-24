import plotly.express as px


def get_empty_figure():
    """
    Crée un graphique vide avec un message indiquant qu'aucune donnée n'est disponible.
    """
    fig = px.line()
    fig.update_layout(dragmode=False, xaxis_visible=False, yaxis_visible=False)
    fig.add_annotation(
        text="Aucune donnée à afficher. Cliquez sur une barre dans le graphique pour plus d'informations.",
        showarrow=False,
        xref="paper",
        yref="paper",
    )
    return fig

def get_graph_info(data, metric, entity_name):
    """
    Récupère les informations du graphique en fonction de la métrique et de l'entité sélectionnée.
    """
    if metric == "revenue":
        return data[data["entity_name"] == entity_name].sort_values(
            by="revenue", ascending=False
        )
    else:
        return data[data["entity_name"] == entity_name].sort_values(
            by="release_date", ascending=True
        )
