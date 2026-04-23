import requests
import json
import sys

def test_manual_action():
    url = "http://localhost:8000/api/bot/manual-action"
    
    # Try with a common symbol, or one that might fail to trigger an error
    payload = {
        "symbol": "BTC/USDT",
        "action_type": "ADAPTIVE_OTO"
    }
    
    print(f"Triggering {payload['action_type']} for {payload['symbol']}...")
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        
        try:
            data = response.json()
            if response.status_code != 200:
                print("\n❌ ERROR RECEIVED (DETAIL):")
                print(data.get('detail', 'No detail provided'))
            else:
                print("\n✅ SUCCESS:")
                print(json.dumps(data, indent=2))
        except:
            print(f"Raw Response: {response.text}")
            
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    test_manual_action()
