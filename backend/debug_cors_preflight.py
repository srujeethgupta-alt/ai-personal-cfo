import urllib.request
import urllib.error

for path in ['/api/expense-chart', '/api/ai-insights']:
    url = 'http://localhost:8000' + path
    print(f'\n=== PRELIGHT OPTIONS {path} ===')
    req = urllib.request.Request(url, method='OPTIONS')
    req.add_header('Origin', 'http://localhost:5173')
    req.add_header('Access-Control-Request-Method', 'GET')
    req.add_header('Access-Control-Request-Headers', 'authorization,content-type')
    try:
        with urllib.request.urlopen(req) as resp:
            print('status', resp.status)
            for k, v in resp.getheaders():
                if k.lower().startswith('access-control-'):
                    print(f'{k}: {v}')
    except urllib.error.HTTPError as e:
        print('status', e.code)
        body = e.read().decode('utf-8', errors='ignore')
        if body:
            print('body', body)
        for k, v in e.headers.items():
            if k.lower().startswith('access-control-'):
                print(f'{k}: {v}')
    except Exception as e:
        print('error', e)
