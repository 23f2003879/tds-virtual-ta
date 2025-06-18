import requests

url = "http://127.0.0.1:8000/api/"
data = {"question": "why are AI models are used in data science?", "image": ""}
response = requests.post(url, json=data)

print("Status Code:", response.status_code)
print("Response Text:", response.text)

try:
    print("JSON:", response.json())
except requests.exceptions.JSONDecodeError:
    print("⚠️ Response is not valid JSON.")
