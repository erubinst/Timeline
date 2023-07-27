import requests

url = "http://127.0.0.1:8050/update"  # Replace with the correct address if needed
message = "Hello, Dash! Can you see me?????"

response = requests.post(url, data={"message": message})
print(response.text)