import plotly.express as px
import pandas as pd
import json
from datetime import datetime as dt


class Figure():
    def __init__(self, df=pd.DataFrame()):
        self.df = pd.DataFrame({
            'Start': [],
            'Finish': [],
        })
        self.colors = {'scheduled': 'rgb(249,168,37)',  # Orange
                       "executing": "rgb(40, 167, 69)",  # Green
                       'completed': 'rgb(0,0,0)',  # Black
                       'aborted': 'rgb(255,0,0)'}  # Red
        self.plot = px.timeline(self.df, x_start="Start", x_end="Finish")

    # Loads in json file and formats into dataframe plotly can use
    def json_to_df(self, data):
        self.df = pd.DataFrame(data["data"]["tasks"])
        print(self.df)
        new_column_labels = ["lotid", "task_id", "Task", "Resource",
                             "configurationId", "Start", "Finish", "Status", "Notes"]
        self.df.columns = new_column_labels
        self.df['Start'] = self.df['Start'].apply(
            lambda x: pd.to_datetime(x[0]))
        self.df['Finish'] = self.df['Finish'].apply(
            lambda x: pd.to_datetime(x[0]))

    def update_axes(self, x_range, y_range):
        if x_range:
            self.plot.update_layout(xaxis_range=x_range)
        if y_range:
            self.plot.update_layout(yaxis_range=y_range)

    # creates plotly timeline
    def get_figure(self, x_range=[], y_range=[], json_data=None):
        if json_data:
            self.json_to_df(json_data)
        custom_order = self.df['Resource'].unique()
        self.plot = px.timeline(self.df, x_start="Start", x_end="Finish", y="Resource", color="Status",
                                custom_data=['task_id', 'Notes'], category_orders={"Resource": custom_order},
                                color_discrete_map=self.colors, hover_name="Task", text="Task", hover_data=["Start", "Finish", "Status", "Notes"])
        self.plot.update_traces(
            insidetextanchor='middle', textposition='inside', cliponaxis=True, textangle=0)
        self.update_axes(x_range, y_range)
