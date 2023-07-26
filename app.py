import dash
from dash import Dash, html, dcc, callback, Output, Input, State
import plotly.express as px
from figure import fig # Import the df and fig from the figure module
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout with the Gantt chart
app.layout = html.Div([
    html.H1(children='Timeline', style={'textAlign':'center'}),
    dcc.Graph(id='timeline-graph', figure=fig.plot),
    dbc.Modal(
        id='pop-up',
        children=[
            dbc.ModalHeader("Task Details"),
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
    )
])

# Callback to show or close the pop-up and populate its content
@app.callback(
    [Output('pop-up', 'is_open'),
     Output('pop-up-content', 'children')],
    [Input('timeline-graph', 'clickData'),
     Input('button-cancel', 'n_clicks'),
     Input('button-completed', 'n_clicks'),
     Input('button-abort', 'n_clicks'),
     Input('button-executed', 'n_clicks')],
    prevent_initial_call=True
)
def show_or_close_pop_up(click_data, cancel_clicks, completed_clicks, aborted_clicks, executed_clicks):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'timeline-graph' and click_data:
        task = click_data['points'][0]['y']  # Access the task name from click_data
        return True, f'You clicked on Task: {task}'

    if triggered_id in ('button-cancel', 'button-completed', 'button-abort', 'button-executed'):
        return False, None

    return dash.no_update, dash.no_update

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

    return {}, {}

# Callback to update the timeline data when the buttons are clicked
@app.callback(
    Output('timeline-graph', 'figure'),
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
            # need to replace this search with a map to a configuration id
            fig.df.loc[fig.df['task_id'] == task_id, 'Status'] = 'completed'
        elif triggered_id == 'button-abort':
            fig.df.loc[fig.df['task_id'] == task_id, 'Status'] = 'aborted'
        elif triggered_id == 'button-executed':
            fig.df.loc[fig.df['task_id'] == task_id, 'Status'] = 'executing'

    x_range = [relayout_data.get('xaxis.range[0]'), relayout_data.get('xaxis.range[1]')]
    y_range = [relayout_data.get('yaxis.range[0]'), relayout_data.get('yaxis.range[1]')]
    fig.get_figure(x_range, y_range)

    return fig.plot

if __name__ == '__main__':
    app.run_server(debug=True)