import dash
from dash import html, dcc, callback, Output, Input, State
from figures.figure import Figure
import dash_bootstrap_components as dbc
import config

#dash.register_page(__name__)

fig = Figure(figType = 'order')
initial_post = True

layout = html.Div([
    html.H1(children='Order View', style={'textAlign': 'center'}),
    html.Div(id='order-timeline-graph-container', style={'display': 'none'}, children=[
        dcc.Graph(id='order-timeline-graph', figure=fig.plot),
    ]),
    dcc.Store(id='order-relayout-data-store', data=[[], [], None])
])

@callback(
    Output('order-relayout-data-store', 'data'),
    Input('order-timeline-graph', 'relayoutData'),
    State('order-relayout-data-store', 'data')
)
def update_relayout_data(relayout_data, prev_relayout_data):
    if relayout_data:
        x_range = [relayout_data.get(
            'xaxis.range[0]'), relayout_data.get('xaxis.range[1]')]
        y_range = [relayout_data.get(
            'yaxis.range[0]'), relayout_data.get('yaxis.range[1]')]
        dragmode = relayout_data.get('dragmode')
        if prev_relayout_data == [[], [], None]:
            return [x_range, y_range, dragmode]
        else:
            if relayout_data.get('autosize') or relayout_data.get('xaxis.autorange'):
                return [[], [], dragmode]
            else:
                x_range = [x_range[0] or prev_relayout_data[0]
                           [0], x_range[1] or prev_relayout_data[0][1]]
                y_range = [y_range[0] or prev_relayout_data[1]
                           [0], y_range[1] or prev_relayout_data[1][1]]
                dragmode = dragmode or prev_relayout_data[2]
                return [x_range, y_range, dragmode]
    else:
        return [[], [], None]
    
# Callback to update the UI with the latest received message
# Allow this to run on initial booting of the app so that latest data from scheduler is displayed
@callback(
    [Output('order-timeline-graph', 'figure'),
     Output('order-timeline-graph-container', 'style')],
    [Input("update-messages-interval", "n_intervals"),
     Input('order-relayout-data-store', 'data')]
)
def update_output(n_intervals, relayout_data):
    global initial_post
    x_range, y_range = [], []
    if relayout_data:
        x_range = relayout_data[0]
        y_range = relayout_data[1]
        dragmode = relayout_data[2]
    if config.order_latest_received_message != config.latest_received_message:
        fig.get_figure(x_range, y_range, dragmode,
                       json_data=config.latest_received_message)
        initial_post = False
        config.order_latest_received_message = config.latest_received_message
        return fig.plot, {'display': 'block'}
    elif initial_post:
        return {'data': [], 'layout': {}}, {'display': 'none'}
    return dash.no_update, {'display': 'block'}