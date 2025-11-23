# Quick Start Guide

## Prerequisites
- Python 3.10+ (tested with 3.13.0.beta.4)
- Node.js 16+ with npm (tested with 11.6.2)
- HubSpot API credentials (optional for development testing)

## Installation & Setup

### 1. Install Backend Dependencies
```bash
cd integrations_technical_assessment/backend
python -m pip install fastapi uvicorn httpx redis requests python-multipart fakeredis kombu
```

### 2. Install Frontend Dependencies
```bash
cd integrations_technical_assessment/frontend
npm install
```

## Running the Application

### Terminal 1: Start Backend Server
```bash
cd integrations_technical_assessment/backend
python run_server.py
# or: python -m uvicorn main:app --reload
```
Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
Using fakeredis for development (no real Redis server needed)
```

### Terminal 2: Start Frontend Server
```bash
cd integrations_technical_assessment/frontend
npm start
```
Expected output:
```
Compiled successfully!
You can now view frontend in the browser.
Local:            http://localhost:3000
```

## Testing the HubSpot Integration

### Step 1: Open Application
Navigate to `http://localhost:3000` in your browser

### Step 2: Configure Integration
1. Enter User ID: `TestUser` (default)
2. Enter Organization ID: `TestOrg` (default)
3. Select Integration Type: **HubSpot**

### Step 3: Authenticate
1. Click **"Connect to HubSpot"** button
2. Complete HubSpot OAuth authorization in popup window
3. Wait for popup to close automatically

### Step 4: Load Data
1. Click **"Load Data"** button
2. Check browser console (F12 → Console tab)
3. Verify IntegrationItem list is displayed with structure:
```javascript
Loaded IntegrationItem list: [
  {
    id: "123456_Contact",
    name: "John Doe",
    type: "Contact",
    directory: false,
    parent_id: null,
    ...
  },
  // More items...
]
```

## API Endpoints

### Authorization
```bash
# Start OAuth flow
POST http://localhost:8000/integrations/hubspot/authorize
Form data:
  user_id: TestUser
  org_id: TestOrg

# Handle callback (automatic)
GET http://localhost:8000/integrations/hubspot/oauth2callback?code=...&state=...
```

### Data Management
```bash
# Get credentials after OAuth
POST http://localhost:8000/integrations/hubspot/credentials
Form data:
  user_id: TestUser
  org_id: TestOrg

# Fetch and return items
POST http://localhost:8000/integrations/hubspot/load
Form data:
  credentials: {access_token: "...", ...}
```

## Environment Configuration

### Using Real Redis
If you have Redis installed, remove the fakeredis fallback in `redis_client.py`:
```python
redis_client = redis.Redis(host='localhost', port=6379, db=0)
```

### Using Custom HubSpot Credentials
Update credentials in `/backend/integrations/hubspot.py`:
```python
CLIENT_ID = 'your-client-id'
CLIENT_SECRET = 'your-client-secret'
REDIRECT_URI = 'http://localhost:8000/integrations/hubspot/oauth2callback'
```

## Troubleshooting

### Port Already in Use
**Issue**: "Address already in use: ('0.0.0.0', 8000)"
**Solution**: 
```bash
# Find process using port 8000
netstat -ano | findstr :8000
# Kill process (Windows)
taskkill /PID <PID> /F
```

### ModuleNotFoundError
**Issue**: "No module named 'fastapi'"
**Solution**: Re-install dependencies with full pip output
```bash
python -m pip install -r requirements.txt --verbose
```

### CORS Errors in Console
**Issue**: "Access to XMLHttpRequest blocked by CORS"
**Solution**: Ensure backend is running with CORS middleware enabled (already configured in main.py)

### Credentials Not Found
**Issue**: "No credentials found" error after OAuth
**Solution**: 
1. Check Redis is running (or fakeredis is loaded)
2. Verify OAuth callback completed successfully
3. Check browser console for any errors

## Verifying IntegrationItem Output

### In Browser Console
```javascript
// Should see this when you click "Load Data"
Loaded IntegrationItem list: Array(n)
0: {id: "...", type: "Contact", name: "...", ...}
1: {id: "...", type: "Company", name: "...", ...}
...
```

### In Backend Terminal
```
list_of_integration_item_metadata: [<IntegrationItem object at 0x...>, ...]
Returning X IntegrationItem objects
```

## Development Features

- Hot reload enabled (both frontend and backend)
- FakeRedis for development (no external dependencies)
- CORS middleware for localhost:3000
- Material-UI components for clean UI
- Async/await for efficient API calls

## Supported HubSpot Object Types

The integration fetches:
- **Contacts**: First name, Last name, Email
- **Companies**: Company name
- **Deals**: Deal name
- **Tickets**: Ticket subject

Each object is limited to 100 items per type by default.

## Next Steps

1. Test with your HubSpot sandbox account
2. Add more object types (Workflows, Contacts Lists, etc.)
3. Implement pagination for large datasets
4. Add filtering and search capabilities
5. Store more comprehensive item metadata

## Support

For issues with the HubSpot integration:
1. Check backend console for error messages
2. Verify HubSpot API credentials are valid
3. Check CORS configuration in main.py
4. Ensure fakeredis/Redis connection is working
5. Review IntegrationItem class definition in integration_item.py
