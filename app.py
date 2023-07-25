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
                    dbc.Button("Mark as Completed", id="button-Completed", color="success", className="mr-2"),
                    dbc.Button("Mark as Scheduled", id="button-not-started", color="warning", className="mr-2", style={'display': 'none'}),
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
     Input('button-Completed', 'n_clicks'),
     Input('button-not-started', 'n_clicks')],
    prevent_initial_call=True
)
def show_or_close_pop_up(click_data, cancel_clicks, Completed_clicks, not_started_clicks):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'timeline-graph' and click_data:
        task = click_data['points'][0]['y']  # Access the task name from click_data
        return True, f'You clicked on Task: {task}'

    if triggered_id in ('button-cancel', 'button-Completed', 'button-not-started'):
        return False, None

    return dash.no_update, dash.no_update

# Callback to update the visibility of the "Mark as Completed" and "Mark as Scheduled" buttons based on the resource status
@app.callback(
    [Output('button-Completed', 'style'),
     Output('button-not-started', 'style')],
    Input('timeline-graph', 'clickData'),
    prevent_initial_call=True
)
def update_button_visibility(click_data):
    if click_data:
        resource = click_data['points'][0]['y']  # Access the task name from click_data
        task = click_data['points'][0]['customdata'][0]
        print(click_data)
        # need to replace search with mapping to a configuration id
        status = fig.df.loc[(fig.df['Task'] == task) & (fig.df['Resource'] == resource), 'Status'].values[0]
        # Set the visibility of the "Mark as Completed" button based on the resource status
        Completed_button_style = {'display': 'none'} if status == 'Completed' else {}
        
        # Set the visibility of the "Mark as Scheduled" button based on the resource status
        not_started_button_style = {'display': 'none'} if status == 'Scheduled' else {}

        return Completed_button_style, not_started_button_style

    return {}, {}

# Callback to update the timeline data when the "Mark as Completed" or "Mark as Scheduled" button is clicked
@app.callback(
    Output('timeline-graph', 'figure'),
    [Input('button-Completed', 'n_clicks'),
     Input('button-not-started', 'n_clicks')],
    State('timeline-graph', 'figure'),
    State('timeline-graph', 'clickData'),
    prevent_initial_call=True
)
def update_timeline(Completed_clicks, not_started_clicks, figure, click_data):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id in ('button-Completed', 'button-not-started') and click_data:
        resource = click_data['points'][0]['y']  # Access the task name from click_data
        print(click_data)
        task = click_data['points'][0]['customdata'][0]
        if triggered_id == 'button-Completed':
            # need to replace this search with a map to a configuration id
            fig.df.loc[(fig.df['Task'] == task) & (fig.df['Resource'] == resource), 'Status'] = 'Completed'
        elif triggered_id == 'button-not-started':
            fig.df.loc[(fig.df['Task'] == task) & (fig.df['Resource'] == resource), 'Status'] = 'Scheduled'

    fig.get_figure()
    return fig.plot

if __name__ == '__main__':
    app.run_server(debug=True)