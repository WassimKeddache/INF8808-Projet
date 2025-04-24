import pandas as pd
import plotly.express as px
from .countries_chart_data import data_instance

def update_bar_chart(criteria, selected_genre):
    """
    Met à jour le graphique à barres horizontal en fonction du critère de succès et du genre sélectionné.

    Cette fonction génère un graphique interactif montrant les 10 pays ayant le plus grand nombre de films
    répondant à un critère de succès (revenu ou note moyenne). Si un genre est sélectionné, le graphique
    affiche également une répartition des films par genre.

    Args:
        criteria (str): Le critère de succès utilisé pour filtrer les films.
            - 'revenue' : Filtre les films avec un revenu supérieur à 10M$.
            - 'vote_average' : Filtre les films avec une note moyenne supérieure à 7.
        selected_genre (str or None): Le genre de film sélectionné pour filtrer les données.
            - Si None, aucun filtre par genre n'est appliqué.
            - Si un genre est spécifié, seuls les films appartenant à ce genre sont pris en compte.

    Returns:
        list: Une liste contenant un objet `plotly.graph_objects.Figure` représentant le graphique à barres.

    Notes:
        - Les données sont agrégées par pays pour calculer le nombre total de films et le nombre de films
          répondant au critère de succès.
        - Si un genre est sélectionné, une répartition des films par genre est affichée dans un graphique empilé.
        - Les infobulles (hover) sont personnalisées pour afficher des informations détaillées.
    """
    if criteria == 'revenue':
        threshold = 10 * 1000000
        threshold_text = "10M$"
    else:
        threshold = 7
        threshold_text = "7"
    
    # Data filtering pour le critère de succès
    filtered_df = data_instance.get_data()['df']
    filtered_df['meets_threshold'] = filtered_df[criteria] >= threshold
    
    agg_df = filtered_df.groupby('countries').agg({'meets_threshold': 'sum', 'title': 'count' }).reset_index()
    
    agg_df.rename(columns={'meets_threshold': 'successful_films', 'title': 'total_films'}, inplace=True)
    
    top_countries = agg_df.sort_values('successful_films', ascending=False).head(10)
    
    countries = top_countries['countries'].tolist()
    successful_films = top_countries['successful_films'].tolist()
    
    genre_data = [0] * len(countries)
    ratio_data = [0] * len(countries)
    
    if selected_genre:
        genre_filtered_df = filtered_df[filtered_df['genres_list'].apply(lambda x: selected_genre in x if isinstance(x, list) else False)]
        
        genre_agg_df = genre_filtered_df.groupby('countries').agg({'meets_threshold': 'sum'}).reset_index()
        
        genre_agg_df.rename(columns={'meets_threshold': 'genre_successful_films'}, inplace=True)
        
        genre_top_countries = pd.merge(top_countries[['countries', 'successful_films']], genre_agg_df, on='countries', how='left').fillna(0)
        
        genre_data = genre_top_countries['genre_successful_films'].tolist()
        ratio_data = [g/t*100 if t > 0 else 0 for g, t in zip(genre_data, successful_films)]
        successful_films = [sf - gd for sf, gd in zip(successful_films, genre_data)]
    
    chart_df = pd.DataFrame({
        'country': countries,
        'total': successful_films,
        'genre': genre_data,
        'ratio': ratio_data
    })
    
    chart_df = chart_df.sort_values('total', ascending=True)
    
    if selected_genre:
        fig = px.bar(
            chart_df,
            y='country',
            x=['genre', 'total'],
            orientation='h',
            barmode='relative',
            color_discrete_sequence=['#008466', '#006084'],
            labels={
                'country': 'Pays',
                'value': 'Nombre de Films',
                'variable': ''
            },
            title=f"Top 10 Pays par Nombre de Films avec{'un Revenue' if criteria == 'revenue' else 'une Note'} > {threshold_text}"
        )

        fig.data[0].name = selected_genre
        fig.data[1].name = 'Total'
        
        for i, trace in enumerate(fig.data):
            if i == 0:
                trace.hovertemplate = '<b>%{y}</b><br>' + f'{selected_genre}: ' + '%{x}<br><extra></extra>'
                trace.hoverlabel = dict(
                    bgcolor="#ECE9E1",
                    font_size=14,
                    font_family="system-ui",
                    font_color="#008466", 
                    bordercolor="#008466",
                )
            else:
                trace.hovertemplate = '<b>%{y}</b><br>Total: %{customdata}<br>Ratio: %{text}<extra></extra>'
                trace.customdata = chart_df['total'].tolist()
                trace.text = [f"{r:.1f}%" for r in chart_df['ratio'].tolist()]
                trace.hoverlabel = dict(
                    bgcolor="#ECE9E1",
                    font_size=14,
                    font_family="system-ui",
                    font_color="#006084",
                    bordercolor="#006084",
                )
    else:
        fig = px.bar(
            chart_df,
            y='country',
            x='total',
            orientation='h',
            color_discrete_sequence=['#006084'],
            labels={
                'country': 'Pays',
                'total': 'Nombre de Films'
            },
        )
        
        fig.data[0].name = f'Films avec {criteria} > {threshold_text}'
        fig.data[0].hovertemplate = '<b>%{y}</b><br>Films: %{x}<extra></extra>'
        fig.data[0].hoverlabel = dict(
            bgcolor="#ECE9E1",
            font_size=14,
            font_family="system-ui",
            font_color="#006084",
            bordercolor="#006084",
        )

    fig.update_layout(
        title ={
            'text': f"Top 10 Pays par Nombre de Films avec {'un Revenue' if criteria == 'revenue' else 'une Note'} > {threshold_text}",
            'font': {
                'color': '#006084',
                'family': 'system-ui',
            },
        },
        font_family="system-ui",
        xaxis_title="Nombre de Films",
        yaxis_title="Pays",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=20, r=20, t=60, b=20),
        height=600
    )

    fig.update_xaxes(title_font_family="system-ui")
    fig.update_yaxes(title_font_family="system-ui")
    
    return [fig]