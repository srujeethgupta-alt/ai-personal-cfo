import json
import urllib.request
import urllib.error

login_url = 'http://localhost:8000/api/auth/login'
req = urllib.request.Request(login_url, data=json.dumps({'email': 'admin@example.com', 'password': 'Admin@123'}).encode('utf-8'), method='POST')
req.add_header('Content-Type', 'application/json')
req.add_header('Origin', 'http://localhost:5173')
try:
    with urllib.request.urlopen(req) as resp:
        body = json.loads(resp.read().decode('utf-8'))
        token = body['data']['access_token']
        print('LOGIN OK', token[:20] + '...')
except Exception as e:
    print('LOGIN ERR', e)
    raise

for path in ['/api/expense-chart', '/api/ai-insights']:
    url = f'http://localhost:8000{path}'
    print(f'\n=== GET {path} ===')
    req = urllib.request.Request(url, method='GET')
    req.add_header('Origin', 'http://localhost:5173')
    req.add_header('Authorization', f'Bearer {token}')
    try:
        with urllib.request.urlopen(req) as resp:
            print('status', resp.status)
            print('body', resp.read().decode('utf-8')[:500])
            for k,v in resp.getheaders():
                if k.lower().startswith('access-control-'):
                    print(f'{k}: {v}')
    except urllib.error.HTTPError as e:
        print('status', e.code)
        try:
            print(e.read().decode('utf-8'))
        except Exception:
            pass
        for k,v in e.headers.items():
            if k.lower().startswith('access-control-'):
                print(f'{k}: {v}')
    except Exception as e:
        print('error', e)
