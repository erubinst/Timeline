import dash
from dash import Dash, html, dcc, callback, Output, Input, State
import plotly.express as px
from figure import Figure
import dash_bootstrap_components as dbc
from flask import Flask, request, jsonify
import json

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server
# Store the received message - should be initialized by requesting from scheduler
latest_received_message = None
initial_post = True
fig = Figure()
with open("demo-domain-schedule.json", "r") as json_file:
            data = json.load(json_file)
fig.get_figure(json_data=data)

# Layout with the Gantt chart
app.layout = html.Div([
    html.H1(children='Timeline', style={'textAlign':'center'}),
    html.Div(id='timeline-graph-container', style={'display': 'none'}, children=[
        dcc.Graph(id='timeline-graph', figure=fig.plot),
    ]),   

    dbc.Modal(
        id='pop-up',
        children=[
            dbc.ModalHeader("Task Details", close_button=False),
            dbc.ModalBody(id='pop-up-content'),
            dbc.ModalFooter(
                [
                    dbc.Button("Execute", id="button-executed", color="success", className="mr-2"),
                    dbc.Button("Complete", id="button-completed", color="dark", className="mr-2"),
                    dbc.Button("Abort", id="button-abort", color="danger", className="mr-2", style={'display': 'none'}),
                    dbc.Button("Cancel", id="button-cancel", color="secondary")
                ]
            ),
        ],
        centered=True,
        is_open=False,
        className="modal-dialog"
    ),
    # Add an interval component to trigger a callback every 5 seconds
    dcc.Interval(id="update-messages-interval", interval=1000, n_intervals=0)
])

# Callback to show or close the popup based on clicks
@app.callback(
    [Output('pop-up', 'is_open'),
     Output('pop-up-content', 'children'),
     Output('timeline-graph', 'clickData')],
    [Input('timeline-graph', 'clickData'),
     Input('button-cancel', 'n_clicks'),
     Input('button-completed', 'n_clicks'),
     Input('button-abort', 'n_clicks'),
     Input('button-executed', 'n_clicks')],
    [State('pop-up', 'is_open'),
     State('timeline-graph', 'clickData')],
    prevent_initial_call=True
)
def show_or_close_pop_up(click_data, cancel_clicks, completed_clicks, aborted_clicks, executed_clicks, is_open, last_click_data):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'timeline-graph' and click_data:
        task = click_data['points'][0]['y']  # Access the task name from click_data
        return True, f'You clicked on Task: {task}', click_data

    if triggered_id == 'button-cancel':
        return False, None, {}  # Return an empty dictionary as clickData when pop-up is closed

    if triggered_id in ('button-completed', 'button-abort', 'button-executed'):
        return False, None, last_click_data

    return is_open, dash.no_update, dash.no_update

# Callback to update the visibility of the buttons based on resource status
@app.callback(
    [Output('button-completed', 'style'),
     Output('button-abort', 'style'),
     Output('button-executed', 'style')],
    Input('timeline-graph', 'clickData'),
    prevent_initial_call=True
)
def update_button_visibility(click_data):
    if click_data:
        task_id = click_data['points'][0]['customdata'][0]
        status = fig.df.loc[fig.df['task_id'] == task_id, 'Status'].values[0]
        completed_button_style = {'display': 'none'} if status != 'executing' and status != 'scheduled' else {}
        abort_button_style = {'display': 'none'} if status != 'executing' else {}
        executed_button_style = {'display': 'none'} if status != 'scheduled' else {}

        return completed_button_style, abort_button_style, executed_button_style

    return {}, {}, {}

# Callback to update the timeline data when the buttons are clicked
@app.callback(
    Output('timeline-graph', 'figure', allow_duplicate=True),
    [Input('button-completed', 'n_clicks'),
     Input('button-abort', 'n_clicks'),
     Input('button-executed', 'n_clicks')],
    [State('timeline-graph', 'figure'),
     State('timeline-graph', 'clickData'),
     State('timeline-graph', 'relayoutData')],  # Include the relayoutData property
    prevent_initial_call=True
)
def update_timeline(completed_clicks, aborted_clicks,executed_clicks, figure, click_data, relayout_data):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id in ('button-completed', 'button-abort', 'button-executed') and click_data:
        task_id = click_data['points'][0]['customdata'][0]
        if triggered_id == 'button-completed':
            fig.df.loc[fig.df['task_id'] == task_id, 'Status'] = 'completed'
        elif triggered_id == 'button-abort':
            fig.df.loc[fig.df['task_id'] == task_id, 'Status'] = 'aborted'
        elif triggered_id == 'button-executed':
            fig.df.loc[fig.df['task_id'] == task_id, 'Status'] = 'executing'

    x_range = [relayout_data.get('xaxis.range[0]'), relayout_data.get('xaxis.range[1]')]
    y_range = [relayout_data.get('yaxis.range[0]'), relayout_data.get('yaxis.range[1]')]
    fig.get_figure(x_range, y_range)

    return fig.plot

# Route to handle the incoming POST requests and update the latest received message
def update_messages():
    global latest_received_message
    message = request.get_json()
    if message:
        latest_received_message = message
    return jsonify(success=True)

server.add_url_rule('/update', view_func=update_messages, methods=['POST'])

# Callback to update the UI with the latest received message
# Allow this to run on initial booting of the app so that latest data from scheduler is displayed
@app.callback(
    [Output('timeline-graph', 'figure'),
     Output('timeline-graph-container', 'style')],
    [Input("update-messages-interval", "n_intervals")],
    State('timeline-graph', 'relayoutData')
)
def update_output(n_intervals, relayout_data):
    global latest_received_message
    global initial_post
    x_range, y_range = [], []
    if relayout_data:
        x_range = [relayout_data.get('xaxis.range[0]'), relayout_data.get('xaxis.range[1]')]
        y_range = [relayout_data.get('yaxis.range[0]'), relayout_data.get('yaxis.range[1]')]
        fig.update_axes(x_range, y_range)
    if latest_received_message:
        fig.get_figure(x_range, y_range, json_data = latest_received_message)
        latest_received_message = None
        initial_post = False
        return fig.plot, {'display': 'block'}
    elif initial_post:
        return {'data': [], 'layout': {}}, {'display': 'none'}
    return fig.plot, {'display': 'block'}



if __name__ == '__main__':
    app.run_server(debug=True)