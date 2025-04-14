import dash_html_components as html

def get_footer():
    return html.Footer(
    className='main-footer',
    children=[
        html.P([
            "Données issues de ",
            html.A("TMDB via Kaggle", href="https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata", target="_blank"),
            ", basées sur les contributions de ",
            html.A("TMDB", href="https://www.themoviedb.org/", target="_blank"),
            " et initialement inspirées par ",
            html.A("IMDb", href="https://www.imdb.com/fr-ca/", target="_blank"),
            "."
        ]),
        html.P("Réalisé par : Galen Hu, Thierry Huber, Wassim Keddache, Charles-Antoine Laurin, Michael Roussel, Yannis Yahya")
    ])