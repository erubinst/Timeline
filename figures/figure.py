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
        task_data = data["data"]["tasks"]
        msg_type = data.get("msgType")
        # adding == None to have it continue to work for me until I get new schedule type
        if msg_type == "Schedule" or data.get("msgType") == None:
            self.df = pd.DataFrame(task_data)
        elif msg_type == "Update":
            if self.df.empty:
                print("Cannot update without initial schedule")
                return
            for task in task_data:
                # Find the index where taskId matches
                index = self.df.index[self.df['taskId'] == task["taskId"]]
                # Check if the taskId exists in the DataFrame
                if not index.empty:
                    # Update the row with the dictionary values
                    self.df.loc[index[0]] = task
                else:
                    # Handle the case where the taskId is not found
                    print(f"Task with taskId {task['taskId']} not found.")
        self.df['start_time'] = self.df['start_time'].apply(lambda x: x if isinstance(x, pd.Timestamp) else pd.to_datetime(x[0]))
        self.df['end_time'] = self.df['end_time'].apply(lambda x: x if isinstance(x, pd.Timestamp) else pd.to_datetime(x[0]))

    def update_axes(self, x_range, y_range, dragmode):
        if x_range:
            self.plot.update_layout(xaxis_range=x_range)
        if y_range:
            self.plot.update_layout(yaxis_range=y_range)
        if dragmode:
            self.plot.update_layout(dragmode=dragmode)

    def add_order_rows(self):
        self.df['lotId'] = self.df['lotId'].astype(str)
        # Group by 'orderId' and add a new row for each unique orderId
        new_rows = []
        earliest_start_time = self.df['start_time'].min()
        latest_end_time = self.df['end_time'].max()
        for order_id in self.df['orderId'].unique():
            new_row = {
                "orderId": order_id,
                "lotId": order_id,
                "taskId": None, 
                "taskName":order_id,
                "agentId": None,
                "configurationId": None,
                "start_time": earliest_start_time,
                "end_time": latest_end_time,
                "status": "order-label",
                "notes": None
            }
            new_rows.append(new_row)

        # Append the new rows to the DataFrame
        self.df = pd.concat([self.df, pd.DataFrame(new_rows)], ignore_index=True)
        sorting_order = {
            True: 0,  # Lower value for empty rows
            False: 1,  # Higher value for non-empty rows
        }
        self.df['sort_key'] = self.df['taskId'].isna()

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
            if not self.df['taskName'].isna().any():
                self.add_order_rows()
            self.df = self.df.sort_values(by=['orderId', 'lotId'])
            self.plot = px.timeline(self.df, x_start="start_time", x_end="end_time", y="lotId", color="status",
                                    color_discrete_map=self.colors, text = "taskName", category_orders={"lotId": self.df['lotId'].tolist()})
            self.plot.update_traces(    
                insidetextanchor='middle', textposition='inside', cliponaxis=True, textangle=0)

        self.update_axes(x_range, y_range, dragmode)

