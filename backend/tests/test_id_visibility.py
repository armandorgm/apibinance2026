
import urllib.request
import json
import traceback

def test_id_visibility():
    url = "http://localhost:8000/api/trades/history?symbol=1000PEPE/USDC:USDC&logic=atomic_fifo"
    try:
        with urllib.request.urlopen(url) as response:
            if response.status != 200:
                print(f"Error: {response.status}")
                return

            data = response.read().decode('utf-8')
            trades = json.loads(data)
            ids = [t['id'] for t in trades]
            
            # Check for unique IDs
            unique_ids = set(ids)
            if len(ids) != len(unique_ids):
                print(f"FAIL: Duplicate IDs found. Total: {len(ids)}, Unique: {len(unique_ids)}")
                # Find duplicates
                seen = set()
                dupes = [x for x in ids if x in seen or seen.add(x)]
                print(f"Duplicates: {dupes[:10]}")
            else:
                print(f"PASS: All {len(ids)} trade IDs are unique.")

            # Check for common ID problems
            double_prefixes = 0
            correct_prefixes = 0
            no_prefixes = 0
            zeros = 0
            
            for t in trades:
                entry_id = t.get('entry_order_id')
                if entry_id:
                    # Check for double letters (CC or BB)
                    if len(entry_id) >= 2 and entry_id[:2] in ['BB', 'CC']:
                        double_prefixes += 1
                        print(f"ERROR: Double prefix in {entry_id}")
                    elif entry_id[0] in ['B', 'C']:
                        correct_prefixes += 1
                    else:
                        no_prefixes += 1
                
                if t.get('is_pending') or t.get('exit_side') == '':
                    if t['id'] == 0:
                        zeros += 1

            print(f"--- Results ---")
            print(f"Correct Prefixes: {correct_prefixes}")
            print(f"Double Prefixes: {double_prefixes}")
            print(f"No Prefixes: {no_prefixes}")
            print(f"Zeros (id=0): {zeros}")
            
            if double_prefixes == 0 and zeros == 0:
                print("FINAL STATUS: PASS")
            else:
                print("FINAL STATUS: FAIL")

    except Exception as e:
        print(f"Error connecting to API: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_id_visibility()
