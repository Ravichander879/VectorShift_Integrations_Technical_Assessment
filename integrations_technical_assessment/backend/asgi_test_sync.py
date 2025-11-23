from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def run():
    data = {'user_id': 'TestUser', 'org_id': 'TestOrg'}
    resp_get = client.get('/')
    print('GET / status', resp_get.status_code, 'body', resp_get.text)
    resp = client.post('/integrations/hubspot/authorize', data=data)
    print('POST /integrations/hubspot/authorize status', resp.status_code)
    print('Response body:', resp.text)

if __name__ == '__main__':
    run()
