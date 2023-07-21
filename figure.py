import plotly.express as px
import pandas as pd

df = pd.DataFrame([
    dict(Task="Job A", Start='2023-01-01 00:00', Finish='2023-01-01 01:00', Resource="Complete"),
    dict(Task="Job B", Start='2023-01-01 04:05', Finish='2023-01-01 05:35', Resource="Not Started"),
    dict(Task="Job C", Start='2023-01-01 00:40', Finish='2023-01-01 04:10', Resource="Not Started"),
    dict(Task="Job D", Start='2023-01-01 00:30', Finish='2023-01-01 02:10', Resource="Complete"),
    dict(Task="Job E", Start='2023-01-01 03:00', Finish='2023-01-01 06:10', Resource="Not Started"),
    dict(Task="Job F", Start='2023-01-01 01:05', Finish='2023-01-01 02:35', Resource="Complete")
])

# Define the colors with RGB values corresponding to Bootstrap's "warning" and "success" colors
colors = {'Not Started': 'rgb(255, 193, 7)',  # Yellow (Bootstrap warning color)
          'Complete': 'rgb(40, 167, 69)'}    # Green (Bootstrap success color)

custom_order = df['Task'].unique()
fig = px.timeline(df, x_start="Start", x_end="Finish", y="Task", color="Resource",
                  custom_data=['Task'], category_orders={"Task": custom_order},
                  color_discrete_map=colors)