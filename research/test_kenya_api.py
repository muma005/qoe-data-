import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*'
}
endpoints = ['active-tenders', 'contracts', 'awarded-tenders']

for ep in endpoints:
    url = f'https://tenders.go.ke/api/{ep}'
    try:
        r = requests.get(url, headers=headers, timeout=15)
        print(f"Endpoint: {ep} -> Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            items = data.get('data', [])
            print(f"   Items returned: {len(items)}")
            if items:
                print(f"   Keys: {list(items[0].keys())}")
                print(f"   Sample title: {items[0].get('title') or items[0].get('tender_title')}")
    except Exception as e:
        print(f"Endpoint {ep} error: {e}")
