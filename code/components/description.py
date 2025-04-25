from dash import html, dcc, callback

def get_description():
    return html.Div(
        className='text',
        children=[
            html.H1(
                "DÉFINIR LE SUCCÈS",
                className='text-title'
            ),
            html.P(
                """
                Dans le cadre de ce projet, nous cherchons à déterminer les facteurs qui influencent le succès 
                d’un film en nous basant sur une base de données issue de TMDB. Nous définissons le succès selon 
                deux dimensions complémentaires : d’une part, la performance financière mesurée par le revenu 
                net du film, et d’autre part, la réception critique représentée par la note moyenne attribuée 
                par les spectateurs. Cette double définition nous permet d’analyser à la fois l’impact commercial
                et l’appréciation du public, offrant ainsi une vision plus complète du succès cinématographique. L’objectif est d’évaluer dans quelle mesure certains éléments — tels que le budget, le genre, le pays de production, le réalisateur, les acteurs principaux ou encore le studio — peuvent être prédictifs du succès selon ces deux axes.
                """,
                className='text-paragraph'
            ),
        ]
    )