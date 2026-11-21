import requests
import re

url = "https://icpmconference.org/2019/icpm-2019/contests-challenges/bpi-challenge-2019/"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

try:
    r = requests.get(url, headers=headers, timeout=15)
    print("Status:", r.status_code)
    links = re.findall(r'href=[\'"](.*?)[\'"]', r.text)
    for l in set(links):
        if any(k in l.lower() for k in ['bpi', 'csv', 'download', '4tu', 'xes', 'data', 'challenge']):
            print("Link:", l)
except Exception as e:
    print("Error:", e)
