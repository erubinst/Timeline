import dash
from dash import html, dcc, callback, Output, Input, State, dash_table
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import requests
import json

import pandas as pd

dash.register_page(__name__, name='New Order', order=2)

# Order ID, name of the structure being built, percentage completed, name of current task, resources used on the task.
# initialize table
# Store the received message - should be initialized by requesting from scheduler

# App layout
layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Place a New Order", style={'textAlign': 'center', 'margin-bottom': '30px'}), className="text-center mt-4"),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.Dropdown(['pagoda', 'staircase'], id='demo-dropdown', placeholder="Select an order type"),
            width={'size': 4},
            style={'margin-bottom': '20px'}
        ),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.Input(id='range', type='number', min=0, step=1, style={'width': '15%', 'margin-bottom': '20px'}, placeholder="Quantity"),
        ),
    ]),
    dbc.Row([
        dbc.Col(
            dbc.Button("Submit", id='submit-button', color="primary", className="me-1", style={'textAlign': 'center', 'margin-bottom': '30px'}),
        )
    ]),
    dbc.Row([
        dbc.Col(
            html.Div(id='output-div', style={'color': 'red'}),
        )
    ])
])


# Callback to handle button click and send POST message
@callback(
    [Output('output-div', 'children'),
     Output('demo-dropdown', 'value'),
     Output('range', 'value')],
    Input('submit-button', 'n_clicks'),
    State('demo-dropdown', 'value'),
    State('range', 'value')
)
def send_post_message(n_clicks, dropdown_value, quantity_value):
    if n_clicks is None:
        raise PreventUpdate

    # Validate dropdown and quantity inputs
    if not dropdown_value or not quantity_value:
        return "Invalid inputs. Please provide a valid order type and quantity.", dropdown_value, quantity_value

    # Continue with your logic to send the POST message
    input_data = {"structureType": dropdown_value, "quantity": quantity_value}
    response = requests.post('http://localhost:8050/new-order', json=input_data)
    print(response.text)
    
    # Clear the values after sending the POST message
    return f"POST message sent for Order: {dropdown_value}, Quantity: {quantity_value}", None, None
