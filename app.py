import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from flask import request, jsonify
import config

app = dash.Dash(__name__, use_pages=True, external_stylesheets=[
                dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server


app.layout = html.Div([
    dcc.Location(id="url"),
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(
                dbc.NavLink(
                    f"{page['name']}", href=page["relative_path"]
                )
            )
            for page in dash.page_registry.values()
        ],
        # brand="Schedules",
        # brand_href="/",
        color="primary",
        dark=True,
    ),
    dash.page_container,
    # Add an interval component to trigger a callback every 5 seconds
    dcc.Interval(id="update-messages-interval", interval=1000, n_intervals=0)
])

def update_messages():
    message = request.get_json()
    if message:
        config.latest_received_message = message
    return jsonify(success=True)


server.add_url_rule('/update', view_func=update_messages, methods=['POST'])

if __name__ == '__main__':
    app.run_server(debug=True, host = "0.0.0.0")
