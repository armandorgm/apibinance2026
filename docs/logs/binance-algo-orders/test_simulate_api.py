import requests
import json
from datetime import datetime

url = "http://localhost:8000/api/chase/simulate"
payload = {
    "current_price": 50100.0,
    "last_tick_price": 50000.0,
    "side": "buy",
    "last_update_iso": datetime.utcnow().isoformat(),
    "cooldown_seconds": 1,
    "price_threshold": 0.0005
}

try:
    response = requests.post(url, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
