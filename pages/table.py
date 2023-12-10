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
    html.H1(children='Table', style={'textAlign': 'center'}),
    dash_table.DataTable(
        id='my-datatable',
        columns=[{'name': col, 'id': col} for col in config.table_df.columns],
        data=config.table_df.to_dict('records'),
        editable=True,
        filter_action="native",
        sort_action='native'
                )
])

def process_group(group):
    # Perform your calculations here
    orderId = group['orderId'].iloc[0]
    productId = group['productId'].iloc[0]
    start_time = group['start_time'].min()
    end_time = group['end_time'].max()
    # if all scheduled, scheduled, if any executed, executing, if all completed, completed, if any aborted, aborted
    executing_status = any(group['status'] == 'executing')
    aborted_status = any(group['status'] == 'aborted')
    completed_status = all(group['status'] == 'completed')
    scheduled_status = all(group['status'] == 'scheduled')
    current_executing_task = None
    status = None
    if executing_status:
        status = 'executing'
        current_executing_task = group[group['status'] == 'executing']['taskName'].iloc[0]
    elif aborted_status:
        status = 'aborted'
    elif completed_status:
        status = 'completed'
    elif scheduled_status: 
        status = 'scheduled'
    
    # Return a DataFrame with the unique 'orderId' and the calculated results
    return pd.DataFrame({'orderId': [orderId], 'productId': [productId], 'start_time': [start_time], 'end_time': [end_time], 'status': [status], 'current_executing_task': [current_executing_task]})


def grab_relevant_data(latest_received_message):
    data = latest_received_message["data"]["tasks"]
    new_df = pd.DataFrame(data)
    new_df['start_time'] = new_df['start_time'].apply(lambda x: x if isinstance(x, pd.Timestamp) else pd.to_datetime(x[0]))
    new_df['end_time'] = new_df['end_time'].apply(lambda x: x if isinstance(x, pd.Timestamp) else pd.to_datetime(x[0]))
    # Apply the function to each group of 'orderId'
    result_df = new_df.groupby('orderId').apply(process_group)
    return result_df

# Callback to update the table at regular intervals (every second in this case)
@callback(
    Output('my-datatable', 'data'),
    [Input('update-messages-interval', 'n_intervals'), Input('my-datatable', 'data')]
)
def update_table(n_intervals, current_data): 
    if config.latest_received_message is not None:
        data = grab_relevant_data(config.latest_received_message)
        if (config.latest_received_message != config.table_latest_received_message) or (current_data != data.to_dict('records')):
        # need to parse df into correct columns for table\
            config.table_latest_received_message = config.latest_received_message
            return data.to_dict('records')
    # elif initial_post:
    #     return table_df
    return dash.no_update