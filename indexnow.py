"""Tell IndexNow search engines (Bing, Yandex, Naver, Seznam, Yep) about every URL in sitemap.txt.

Run after each push that adds or changes pages:  python3 indexnow.py
Google does not use IndexNow. The key is public by design: it is hosted at /KEY.txt so the engines can check
that we own the site. Only URLs already on the public site are sent.
"""
import json
import urllib.error
import urllib.request
from pathlib import Path

HOST = 'pourscoreapp.com'
KEY = '49b32696b35b3b37a64f8e125f927648'
urls = (Path(__file__).parent / 'sitemap.txt').read_text().split()
body = json.dumps({'host': HOST, 'key': KEY, 'keyLocation': f'https://{HOST}/{KEY}.txt', 'urlList': urls}).encode()
req = urllib.request.Request('https://api.indexnow.org/indexnow', body, {'Content-Type': 'application/json; charset=utf-8'})
try:
    print(urllib.request.urlopen(req).status, f'{len(urls)} URLs submitted')  # 200 OK or 202 Accepted (key still being checked)
except urllib.error.HTTPError as e:
    raise SystemExit(f'{e.code} {e.read().decode()}')  # 403 key not found, 422 URL not on this host, 429 too many requests
