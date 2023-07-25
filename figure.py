import plotly.express as px
import pandas as pd
import json


class Figure():
    def __init__(self, df=pd.DataFrame()):
        self.df = df
        self.colors = {'Scheduled': 'rgb(249,168,37)',  # Orange
                       "Executing": "rgb(40, 167, 69)", # Green
                       'Completed': 'rgb(0,0,0)'}   # Black
        self.plot = None

    def json_to_df(self, json_file_name):
        with open(json_file_name, "r") as json_file:
            data = json.load(json_file)
        self.df = pd.DataFrame(data["data"]["tasks"])
        new_column_labels = ["lotid", "Task", "Resource",
                             "configurationId", "Start", "Finish"]
        self.df.columns = new_column_labels
        new_column_data = ["Scheduled" for i in range(len(self.df))]
        self.df.insert(loc=2, column='Status', value=new_column_data)
        self.df['Start'] = self.df['Start'].apply(
            lambda x: pd.to_datetime(x[0]))
        self.df['Finish'] = self.df['Finish'].apply(
            lambda x: pd.to_datetime(x[0]))

    def get_figure(self):
        custom_order = self.df['Resource'].unique()
        self.plot = px.timeline(self.df, x_start="Start", x_end="Finish", y="Resource", color="Status",
                                custom_data=['Task'], category_orders={"Resource": custom_order},
                                color_discrete_map=self.colors, hover_name="Task")


fig = Figure()
fig.json_to_df("sample_inputs.json")
fig.get_figure()
