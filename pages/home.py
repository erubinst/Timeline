import dash_bootstrap_components as dbc
from dash import Dash, html
image_path = 'assets/building.jpeg'
import dash

dash.register_page(__name__, path='/')

# Define the home page layout
layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Welcome to Schedule Viewer"), className="text-center mt-4")
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([
                html.Img(src=image_path, className="img-fluid mx-auto d-block")
            ], className="text-center")
        )
    ])
])