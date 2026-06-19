import urllib.request
import urllib.error


def test(path):
    url = f'http://localhost:8000{path}'
    print(f'\n=== GET {path} ===')
    req = urllib.request.Request(url, method='GET')
    req.add_header('Origin', 'http://localhost:5173')
    try:
        with urllib.request.urlopen(req) as resp:
            print('status', resp.status)
            body = resp.read().decode('utf-8')
            print('body:', body[:500])
            for k, v in resp.getheaders():
                if k.lower().startswith('access-control-'):
                    print(f'{k}: {v}')
    except urllib.error.HTTPError as e:
        print('status', e.code)
        try:
            print('body:', e.read().decode('utf-8'))
        except Exception:
            pass
        for k, v in e.headers.items():
            if k.lower().startswith('access-control-'):
                print(f'{k}: {v}')
    except Exception as e:
        print('error', e)

for path in ['/api/expense-chart', '/api/ai-insights']:
    test(path)
