import requests
import re

url = 'https://data.open-contracting.org/en/publication/147'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5'
}
try:
    r = requests.get(url, headers=headers, timeout=20)
    print('Status code:', r.status_code)
    matches = re.findall(r'href=[\"\']([^\"\']*(?:download|\.csv|\.tar|\.gz|\.xlsx)[^\"\']*)[\"\']', r.text, re.I)
    print(f'Matches: {len(matches)}')
    for m in set(matches):
        print(' -', m)
except Exception as e:
    print('Error:', e)
