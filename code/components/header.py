import dash
import dash_html_components as html

def get_header():
    return html.Div(
        className='app-header',
        children=[
            html.Div(
                className='header-content',
                children=[
                    html.H1(
                        "LE SUCCÈS AU CINÉMA",
                        className='app-title'
                    ),
                    html.Div(
                        className='header-subtitle',
                        children=[
                            "Exploration des tendances cinématographiques"
                        ]
                    )
                ]
            )
        ]
    )