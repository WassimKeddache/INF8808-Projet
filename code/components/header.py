import dash
import dash_html_components as html

def get_header():
    return html.Div(
            className='Title',
            style={
                'justifyContent': 'center',
                'alignItems': 'center'
            },
            children=[
                html.H1(
                    "Titre de l'Application",
                    style={'fontSize': '32px', 'textAlign': 'center'}
                )
            ]
        )