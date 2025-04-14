# app.py
import dash
import dash_html_components as html
import dash_core_components as dcc
from components.footer import get_footer
from components.description import get_description
from components.header import get_header
from components.heatmap_budget.heatmap_budget import get_heatmap_budget
from components.countries_chart.countries_chart import get_countries_chart
from components.matrix_diagram.matrix_diagram import get_matrix_diagram
from components.entities_chart.entities_chart import get_entities_chart

# Créer l'application Dash
app = dash.Dash(__name__)
app.title = 'Projet | INF8808'

# Définir la disposition de l'application
app.layout = html.Div(
    className='app-container',
    children=[
        html.Header(
            className='main-header',
            children=[get_header()]
        ),
        html.Main(
            className='main-content',
            children=[
                get_description(),
                get_entities_chart(),
                get_matrix_diagram(),
                get_heatmap_budget(),
                get_countries_chart(),
            ]
        ),
        get_footer(),
    ]
)

# Exposer l'instance du serveur Flask
server = app.server  # Expose le serveur Flask sous-jacent

if __name__ == "__main__":
    app.run_server(debug=True)
