import requests
import json

url = "https://pamoback-nexuspamo.up.railway.app/master_price/products/"

payload = json.dumps({
  "process": 5
})
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)