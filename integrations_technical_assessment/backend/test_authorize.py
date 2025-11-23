import asyncio
import os
import json

from integrations.hubspot import authorize_hubspot


async def main():
    try:
        print('ENV HUBSPOT_CLIENT_ID=', os.getenv('HUBSPOT_CLIENT_ID'))
        res = await authorize_hubspot('TestUser', 'TestOrg')
        print('Result:', json.dumps(res))
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(main())
