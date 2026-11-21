import urllib.request
import re
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
url = 'https://data.open-contracting.org/en/publication/147'
headers = {'User-Agent': 'Mozilla/5.0'}
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode('utf-8')
        links = re.findall(r'href=[\"\']([^\"\']+)[\"\']', html)
        print(f"Total links found: {len(links)}")
        for l in sorted(set(links)):
            if any(k in l.lower() for k in ['download', '.csv', '.tar', '.gz', '.xlsx', '.json']):
                print("Download candidate:", l)
except Exception as e:
    print('Error:', e)
