# slack.py
import json
import secrets
import base64
import urllib.parse
import asyncio

from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse
import httpx

from redis_client import add_key_value_redis, get_value_redis, delete_key_redis
from integrations.integration_item import IntegrationItem


CLIENT_ID = 'beb9915a-0bab-4792-b9c6-a8f9334a04a3'
CLIENT_SECRET = '9d905949-d06b-4731-a59c-730d33ba22ef'
REDIRECT_URI = 'http://localhost:8000/integrations/hubspot/oauth2callback'
HUBSPOT_AUTH_URL = 'https://app.hubspot.com/oauth/authorize'
HUBSPOT_TOKEN_URL = 'https://api.hubapi.com/oauth/v1/token'
# pick scopes appropriate for listing CRM objects; adjust as needed
SCOPE = 'crm.objects.companies.read crm.objects.contacts.read crm.objects.contacts.write crm.objects.deals.read oauth timeline'

from fastapi import Request

async def authorize_hubspot(user_id, org_id):
    """
    Build HubSpot authorization URL, save state in Redis, and return the URL.
    """
    state_data = {
        'state': secrets.token_urlsafe(32),
        'user_id': user_id,
        'org_id': org_id,
    }
    encoded_state = base64.urlsafe_b64encode(json.dumps(state_data).encode('utf-8')).decode('utf-8')

    params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPE,
        'state': encoded_state,
    }
    # ensure proper encoding
    auth_url = f'{HUBSPOT_AUTH_URL}?{urllib.parse.urlencode(params)}'

    # persist state so callback can validate
    await add_key_value_redis(f'hubspot_state:{org_id}:{user_id}', json.dumps(state_data), expire=600)

    return auth_url
async def oauth2callback_hubspot(request: Request):
    """
    Handle HubSpot OAuth callback: validate state, exchange code for tokens,
    store credentials in Redis, and return a small HTML to close the popup.
    """
    if request.query_params.get('error'):
        raise HTTPException(status_code=400, detail=request.query_params.get('error_description') or request.query_params.get('error'))

    code = request.query_params.get('code')
    encoded_state = request.query_params.get('state')
    if not code or not encoded_state:
        raise HTTPException(status_code=400, detail='Missing code or state in callback.')

    try:
        state_data = json.loads(base64.urlsafe_b64decode(encoded_state).decode('utf-8'))
    except Exception:
        raise HTTPException(status_code=400, detail='Invalid state encoding.')

    original_state = state_data.get('state')
    user_id = state_data.get('user_id')
    org_id = state_data.get('org_id')

    saved_state = await get_value_redis(f'hubspot_state:{org_id}:{user_id}')
    if not saved_state or original_state != json.loads(saved_state).get('state'):
        raise HTTPException(status_code=400, detail='State does not match.')

    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            HUBSPOT_TOKEN_URL,
            data={
                'grant_type': 'authorization_code',
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'redirect_uri': REDIRECT_URI,
                'code': code,
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30.0,
        )
    if token_resp.status_code != 200:
        # clean up stored state regardless
        await delete_key_redis(f'hubspot_state:{org_id}:{user_id}')
        raise HTTPException(status_code=token_resp.status_code, detail=f'Failed to fetch tokens: {token_resp.text}')

    # store credentials (token response) for short-term retrieval by frontend
    await add_key_value_redis(f'hubspot_credentials:{org_id}:{user_id}', json.dumps(token_resp.json()), expire=600)

    # remove the saved state
    await delete_key_redis(f'hubspot_state:{org_id}:{user_id}')

    close_window_script = """
    <html>
        <script>
            window.close();
        </script>
    </html>
    """
    return HTMLResponse(content=close_window_script)

async def get_hubspot_credentials(user_id, org_id):
    """
    Retrieve stored HubSpot credentials from Redis and delete the key.
    """
    credentials = await get_value_redis(f'hubspot_credentials:{org_id}:{user_id}')
    if not credentials:
        raise HTTPException(status_code=400, detail='No credentials found.')
    credentials = json.loads(credentials)
    await delete_key_redis(f'hubspot_credentials:{org_id}:{user_id}')
    return credentials


async def create_integration_item_metadata_object(response_json):
    integration_items = []

    for obj in response_json.get("results", []):
        integration_items.append(
            IntegrationItem(
                id=obj.get("id"),
                name=obj.get("properties", {}).get("firstname", "") + " " + obj.get("properties", {}).get("lastname", ""),
                type="Contact",
                parent_id=None,
                parent_path_or_name=None,
            )
        )

    return integration_items

async def get_items_hubspot(credentials):
    # credentials is passed in as a JSON string from the form endpoint; parse it
    credentials = json.loads(credentials)
    access_token = credentials.get("access_token")
    headers = {"Authorization": f"Bearer {access_token}"}

    url = "https://api.hubapi.com/crm/v3/objects/contacts?limit=10"

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=f"Failed to fetch contacts: {resp.text}")

    response_json = resp.json()
    return await create_integration_item_metadata_object(response_json)

