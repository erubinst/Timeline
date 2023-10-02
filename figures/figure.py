import plotly.express as px
import pandas as pd
import json
from datetime import datetime as dt


class Figure():
    def __init__(self, figType='resource', hoverFields=["start_time", "end_time", "status", "notes"]):
        self.df = pd.DataFrame({
            'taskId': [],
            'taskName': [],
            'agentId': [],
            'configurationId': [],
            'start_time': [],
            'end_time': [],
            'status': [],
            'notes': [],
        })
        self.colors = {'scheduled': 'rgb(249,168,37)',  # Orange
                       "executing": "rgb(40, 167, 69)",  # Green
                       'completed': 'rgb(0,0,0)',  # Black
                       'aborted': 'rgb(255,0,0)',
                       'order-label': 'rgb(167, 199, 231)'} 
        self.plot = px.timeline(
            self.df, x_start="start_time", x_end="end_time")
        self.fig_type = figType
        self.hover_fields = hoverFields

    # Loads in json file and formats into dataframe plotly can use
    def json_to_df(self, data):
        self.df = pd.DataFrame(data["data"]["tasks"])
        self.df['start_time'] = self.df['start_time'].apply(
            lambda x: pd.to_datetime(x[0]))
        self.df['end_time'] = self.df['end_time'].apply(
            lambda x: pd.to_datetime(x[0]))

    def update_axes(self, x_range, y_range, dragmode):
        if x_range:
            self.plot.update_layout(xaxis_range=x_range)
        if y_range:
            self.plot.update_layout(yaxis_range=y_range)
        if dragmode:
            self.plot.update_layout(dragmode=dragmode)

    # creates plotly timeline
    def get_figure(self, x_range=[], y_range=[], dragmode='', json_data=None):
        if json_data:
            self.json_to_df(json_data)
        if self.fig_type == 'resource':
            custom_order = self.df['agentId'].unique()
            self.plot = px.timeline(self.df, x_start="start_time", x_end="end_time", y="agentId", color="status",
                                    custom_data=['taskId', 'notes'], category_orders={"agentId": custom_order},
                                    color_discrete_map=self.colors, hover_name="taskName", text="taskName", hover_data=self.hover_fields)
            self.plot.update_traces(
                insidetextanchor='middle', textposition='inside', cliponaxis=True, textangle=0)
            
        if self.fig_type == 'order':
            self.df = self.df.sort_values(by="orderId")
            self.plot = px.timeline(self.df, x_start="start_time", x_end="end_time", y="lotId", color="status", facet_row = "orderId",
                                    color_discrete_map=self.colors, text = "taskName")
            self.plot.update_traces(    
                insidetextanchor='middle', textposition='inside', cliponaxis=True, textangle=0)
            unique_order_ids = self.df['orderId'].unique()
            for i, order_id in enumerate(unique_order_ids):
                self.plot.update_yaxes(title_text=order_id, row=i+1)

        self.update_axes(x_range, y_range, dragmode)

