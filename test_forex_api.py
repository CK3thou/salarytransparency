#!/usr/bin/env python
import urllib.request
import urllib.parse
import json

api_key = '1e5ce0b6f7f9b60ffeb7b5f60dcf095d'
params = {
    'api_key': api_key,
    'base': 'USD',
    'currencies': 'ZMW,ZAR,ZWL'
}
url = 'https://api.forexrateapi.com/v1/latest?' + urllib.parse.urlencode(params, safe=',')

print(f"Testing Forex API...")
print(f"URL: {url}\n")

try:
    with urllib.request.urlopen(url, timeout=5) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print("✅ SUCCESS - API is working!")
        print(json.dumps(data, indent=2))
except urllib.error.HTTPError as e:
    print(f"❌ HTTP Error {e.code}: {e.reason}")
    try:
        error_body = e.read().decode('utf-8')
        print(f"Error response: {error_body}")
    except:
        print("(No additional error details)")
except Exception as e:
    print(f"❌ Error: {e}")
