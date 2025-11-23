📘 VectorShift Integrations Technical Assessment

This project implements a full-stack integration system using React (frontend), FastAPI (backend), and Redis, with a focus on the HubSpot OAuth2 integration.

The assessment consists of:

Part 1: Implementing OAuth authentication for HubSpot

Part 2: Loading and displaying HubSpot items

Extras: Allowing customization and integration into the existing UI

🚀 Project Setup
🖥️ Frontend Setup (React + JS)

Navigate to the frontend:

cd frontend


Install dependencies:

npm install


Start the development server:

npm run start

🧩 Backend Setup (FastAPI + Python)

Navigate to backend directory:

cd backend


Install dependencies (FastAPI, Uvicorn, httpx, Redis client):

pip install -r requirements.txt


If requirements.txt doesn't exist:

pip install fastapi uvicorn httpx redis python-dotenv


Start the FastAPI server:

uvicorn main:app --reload

🗄️ Redis Setup

Run Redis locally:

If you installed Redis (Ubuntu/Mac):

redis-server


If on Windows (Memurai):

Open Memurai

Click Start Server

🔑 Environment Variables

Create a .env file in backend:

HUBSPOT_CLIENT_ID=your_client_id
HUBSPOT_CLIENT_SECRET=your_client_secret
HUBSPOT_REDIRECT_URI=http://localhost:8000/oauth/callback/hubspot
REDIS_HOST=localhost
REDIS_PORT=6379


These values are needed for the OAuth flow.

🧩 Part 1: HubSpot OAuth2 Integration

You must complete these functions in backend/integrations/hubspot.py:

authorize_hubspot()

oauth2callback_hubspot()

get_hubspot_credentials()

Use airtable.py and notion.py as reference.

Expected OAuth Flow:

Frontend → calls /authorize/hubspot

Backend → redirects user to HubSpot OAuth page

User accepts → Redirect back to your callback

Backend exchanges code → access token + refresh token

Store tokens in Redis

📂 Part 2: Loading HubSpot Items

Complete:

get_items_hubspot() in backend

This should:

Use access token to call HubSpot's API (e.g., Contacts, Companies, Deals)

Convert results into IntegrationItem objects

Return a list back to the frontend

For testing, printing the results in console is recommended

🎨 Frontend Integrations

Complete:

frontend/src/integrations/hubspot.js

Then register HubSpot in:

frontend/src/integrations/index.js

frontend/src/components/IntegrationCard.js (or similar)

Any integration selection UI

Use airtable.js and notion.js as models.

✔️ Testing the Integration
1. Create a HubSpot App

Go to: developers.hubspot.com → Apps → Create app
Enable:

OAuth

Scopes (example):

crm.objects.contacts.read

crm.objects.companies.read

crm.objects.deals.read

2. Set Redirect URL

Use:

http://localhost:8000/oauth/callback/hubspot

3. Add the client ID + secret to .env.
4. Run everything:

Redis server

Backend uvicorn

Frontend React

Click HubSpot from integration list

Authenticate

Test item loading
