import dash
from dash import html, dcc, callback, Output, Input, State, dash_table
from figures.figure import Figure
import dash_bootstrap_components as dbc
import config

import pandas as pd

dash.register_page(__name__)

# Order ID, name of the structure being built, percentage completed, name of current task, resources used on the task.
# initialize table
# Store the received message - should be initialized by requesting from scheduler
initial_post = True

# App layout
layout = html.Div([
    dash_table.DataTable(
        id='my-datatable',
        columns=[{'name': col, 'id': col} for col in config.table_df.columns],
        data=config.table_df.to_dict('records'),
        editable=True
                )
])

def grab_relevant_data(latest_received_message):
    data = latest_received_message["data"]["tasks"]
    columns_to_keep = ['orderId']
    new_df = pd.DataFrame(data)
    return new_df[columns_to_keep]

# Callback to update the table at regular intervals (every second in this case)
@callback(
    Output('my-datatable', 'data'),
    [Input('update-messages-interval', 'n_intervals'), Input('my-datatable', 'data')]
)
def update_table(n_intervals, current_data): 
    if config.latest_received_message is not None:
        data = grab_relevant_data(config.latest_received_message)
        if current_data == data.to_dict('records'):
            print("THEY ARE EQUAL")
        if (config.latest_received_message != config.table_latest_received_message) or (current_data != data.to_dict('records')):
        # need to parse df into correct columns for table\
            config.table_latest_received_message = config.latest_received_message
            return data.to_dict('records')
    # elif initial_post:
    #     return table_df
    return dash.no_update