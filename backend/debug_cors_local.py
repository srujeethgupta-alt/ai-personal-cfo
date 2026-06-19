import json
import urllib.request
import urllib.error

for path in ['/api/expense-chart', '/api/ai-insights', '/api/auth/login']:
    url = 'http://localhost:8000' + path
    print('\n=== OPTIONS', path, '===')
    req = urllib.request.Request(url, method='OPTIONS')
    req.add_header('Origin', 'http://localhost:5173')
    req.add_header('Access-Control-Request-Method', 'GET' if path != '/api/auth/login' else 'POST')
    try:
        with urllib.request.urlopen(req) as resp:
            print('OPTIONS status', resp.status)
            for k, v in resp.getheaders():
                if k.lower().startswith('access-control-'):
                    print(f'{k}: {v}')
    except urllib.error.HTTPError as e:
        print('OPTIONS status', e.code)
        body = e.read().decode('utf-8')
        print(body)
        for k, v in e.headers.items():
            if k.lower().startswith('access-control-'):
                print(f'{k}: {v}')
    except Exception as e:
        print('OPTIONS error', e)

print('\n=== LOGIN POST ===')
url = 'http://localhost:8000/api/auth/login'
req = urllib.request.Request(url, data=json.dumps({'email': 'admin@example.com', 'password': 'Admin@123'}).encode('utf-8'), method='POST')
req.add_header('Content-Type', 'application/json')
req.add_header('Origin', 'http://localhost:5173')
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
