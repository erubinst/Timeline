import dash
from dash import Dash, html, dcc, callback, Output, Input, State
import plotly.express as px
from figure import fig, df, colors  # Import the df and fig from the figure module
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout with the Gantt chart
app.layout = html.Div([
    html.H1(children='Timeline', style={'textAlign':'center'}),
    dcc.Graph(id='timeline-graph', figure=fig),
    dbc.Modal(
        id='pop-up',
        children=[
            dbc.ModalHeader("Task Details"),
            dbc.ModalBody(id='pop-up-content'),
            dbc.ModalFooter(
                [
                    dbc.Button("Mark as Complete", id="button-complete", color="success", className="mr-2"),
                    dbc.Button("Mark as Not Started", id="button-not-started", color="warning", className="mr-2", style={'display': 'none'}),
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
     Input('button-complete', 'n_clicks'),
     Input('button-not-started', 'n_clicks')],
    prevent_initial_call=True
)
def show_or_close_pop_up(click_data, cancel_clicks, complete_clicks, not_started_clicks):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'timeline-graph' and click_data:
        task = click_data['points'][0]['y']  # Access the task name from click_data
        return True, f'You clicked on Task: {task}'

    if triggered_id in ('button-cancel', 'button-complete', 'button-not-started'):
        return False, None

    return dash.no_update, dash.no_update

# Callback to update the visibility of the "Mark as Complete" and "Mark as Not Started" buttons based on the resource status
@app.callback(
    [Output('button-complete', 'style'),
     Output('button-not-started', 'style')],
    Input('timeline-graph', 'clickData'),
    prevent_initial_call=True
)
def update_button_visibility(click_data):
    if click_data:
        task = click_data['points'][0]['y']  # Access the task name from click_data
        resource_status = df.loc[df['Task'] == task, 'Resource'].values[0]

        # Set the visibility of the "Mark as Complete" button based on the resource status
        complete_button_style = {'display': 'none'} if resource_status == 'Complete' else {}
        
        # Set the visibility of the "Mark as Not Started" button based on the resource status
        not_started_button_style = {'display': 'none'} if resource_status == 'Not Started' else {}

        return complete_button_style, not_started_button_style

    return {}, {}

# Callback to update the timeline data when the "Mark as Complete" or "Mark as Not Started" button is clicked
@app.callback(
    Output('timeline-graph', 'figure'),
    [Input('button-complete', 'n_clicks'),
     Input('button-not-started', 'n_clicks')],
    State('timeline-graph', 'figure'),
    State('timeline-graph', 'clickData'),
    prevent_initial_call=True
)
def update_timeline(complete_clicks, not_started_clicks, figure, click_data):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id in ('button-complete', 'button-not-started') and click_data:
        task = click_data['points'][0]['y']  # Access the task name from click_data
        if triggered_id == 'button-complete':
            df.loc[df['Task'] == task, 'Resource'] = 'Complete'
        elif triggered_id == 'button-not-started':
            df.loc[df['Task'] == task, 'Resource'] = 'Not Started'

    # Get the unique tasks and use them to set the category_orders dynamically
    custom_order = df['Task'].unique()
    updated_fig = px.timeline(data_frame=df, x_start='Start', x_end='Finish', y='Task', color='Resource',
                              custom_data=['Task'], category_orders={"Task": custom_order}, color_discrete_map=colors)
    return updated_fig

if __name__ == '__main__':
    app.run_server(debug=True)