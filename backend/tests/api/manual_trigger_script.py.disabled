import requests, json
url = 'http://127.0.0.1:8000/api/bot/manual-action'
payload = {"symbol": "1000PEPEUSDC", "action_type": "ADAPTIVE_OTO"}
headers = {'Content-Type': 'application/json'}
resp = requests.post(url, data=json.dumps(payload), headers=headers)
print('Status:', resp.status_code)
print('Response:', resp.text)
