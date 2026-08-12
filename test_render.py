import requests
import sys

print("Sending tiny.csv to Render deployment...")
url = "https://retainai-backend-4yel.onrender.com/dataset/analyze"
try:
    with open('tiny.csv', 'rb') as f:
        files = {'file': ('tiny.csv', f, 'text/csv')}
        response = requests.post(url, files=files, timeout=60)
        print("Status code:", response.status_code)
        if response.status_code == 200:
            print("Success!")
        else:
            print("Response:", response.text)
except Exception as e:
    print("Request failed:", e)
