# app.py
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Output, Input, State
from dash.dependencies import Input, Output
from pages import agent

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
image_path = 'assets/building.jpeg'

# Define the home page layout
home_layout = dbc.Container([
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

# Set up the app layout
app.layout = html.Div([
    dcc.Location(id="url"),
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Home", href="/")),
            dbc.NavItem(dbc.NavLink("Agent", href="/agent")),
        ],
        # brand="Schedules",
        # brand_href="/",
        color="primary",
        dark=True,
    ),
    html.Div(id="page-content", children=home_layout)  # Set the default layout to home_layout
])

# Callback to render page content based on the URL
@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def render_page_content(pathname):
    if pathname == "/agent":
        return agent.layout
    else:
        return home_layout  # Return home layout for the base URL and any other unknown paths

if __name__ == '__main__':
    app.run_server(debug=True)