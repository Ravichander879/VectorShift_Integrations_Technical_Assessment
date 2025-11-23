import asyncio
import httpx

from main import app


async def run_test():
    async with httpx.AsyncClient(app=app, base_url='http://testserver') as client:
        # Send form-encoded POST similar to the frontend
        data = {'user_id': 'TestUser', 'org_id': 'TestOrg'}
        try:
            resp = await client.post('/integrations/hubspot/authorize', data=data)
            print('Status:', resp.status_code)
            print('Response headers:', resp.headers)
            print('Body:', resp.text)
        except Exception as e:
            print('Request failed:', e)

if __name__ == '__main__':
    asyncio.run(run_test())
