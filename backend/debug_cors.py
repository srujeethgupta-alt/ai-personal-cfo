import json
import urllib.request
import urllib.error

url = 'http://10.10.234.152:8000/api/auth/login'

print('=== OPTIONS ===')
req = urllib.request.Request(url, method='OPTIONS')
req.add_header('Origin', 'http://10.10.234.152:5173')
req.add_header('Access-Control-Request-Method', 'POST')
try:
    with urllib.request.urlopen(req) as resp:
        print('OPTIONS status', resp.status)
        for k, v in resp.getheaders():
            if k.lower().startswith('access-control-'):
                print(f'{k}: {v}')
except urllib.error.HTTPError as e:
    print('OPTIONS status', e.code)
    print(e.read().decode('utf-8'))
    for k, v in e.headers.items():
        if k.lower().startswith('access-control-'):
            print(f'{k}: {v}')
except Exception as e:
    print('OPTIONS error', e)

print('\n=== LOGIN ===')
data = json.dumps({'email': 'admin@example.com', 'password': 'password123'}).encode('utf-8')
req = urllib.request.Request(url, data=data, method='POST')
req.add_header('Content-Type', 'application/json')
req.add_header('Origin', 'http://10.10.234.152:5173')
try:
    with urllib.request.urlopen(req) as resp:
        print('LOGIN status', resp.status)
        print(resp.read().decode('utf-8'))
        for k, v in resp.getheaders():
            if k.lower().startswith('access-control-'):
                print(f'{k}: {v}')
except urllib.error.HTTPError as e:
    print('LOGIN status', e.code)
    print(e.read().decode('utf-8'))
    for k, v in e.headers.items():
        if k.lower().startswith('access-control-'):
            print(f'{k}: {v}')
except Exception as e:
    print('LOGIN error', e)
