import pandas as pd
latest_received_message = None
agent_latest_received_message = None
table_latest_received_message = None
order_latest_received_message = None
initial_data = {'orderId': [],
                'productId': [],
                # start time of earliest task
                'start_time': [],
                'end_time': [],
                # if all scheduled, scheduled, if any executed, executing, if all completed, completed, if any aborted, aborted
                'status': [],
                'current_executing_task': []
                }

table_df = pd.DataFrame(initial_data)