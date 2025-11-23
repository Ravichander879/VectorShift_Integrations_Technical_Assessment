// hubspot.js

import { useState, useEffect } from 'react';
import {
    Box,
    Button,
    CircularProgress
} from '@mui/material';
import axios from 'axios';

export const HubSpotIntegration = ({ user, org, integrationParams, setIntegrationParams }) => {
    const [isConnected, setIsConnected] = useState(false);
    const [isConnecting, setIsConnecting] = useState(false);

    // Function to open OAuth in a new window
    const handleConnectClick = async () => {
        try {
            setIsConnecting(true);
            const formData = new FormData();
            formData.append('user_id', user);
            formData.append('org_id', org);
            // Use relative path; `proxy` in package.json forwards to the backend during dev
            const response = await axios.post(`/integrations/hubspot/authorize`, formData);

            // Backend now returns { url: '...' } — support both shapes for backward compatibility
            const authURL = response?.data?.url ?? response?.data;

            if (!authURL) {
                setIsConnecting(false);
                console.error('No authorization URL returned from backend:', response?.data);
                alert('Failed to get authorization URL from backend. Check backend logs.');
                return;
            }

            const newWindow = window.open(authURL, 'HubSpot Authorization', 'width=600, height=600');

            if (!newWindow) {
                // Popup blocked or failed to open
                setIsConnecting(false);
                alert('Unable to open authorization window — check popup blockers.');
                return;
            }

            // Polling for the window to close
            const pollTimer = window.setInterval(() => {
                if (newWindow?.closed !== false) { 
                    window.clearInterval(pollTimer);
                    handleWindowClosed();
                }
            }, 200);
        } catch (e) {
            setIsConnecting(false);
            // Show a helpful message whether the error is HTTP or network
            const serverMsg = e?.response?.data?.detail ?? e?.message ?? 'Unknown error';
            console.error('Authorize error', e);
            alert(serverMsg);
        }
    }

    // Function to handle logic when the OAuth window closes
    const handleWindowClosed = async () => {
        try {
            const formData = new FormData();
            formData.append('user_id', user);
            formData.append('org_id', org);
            const response = await axios.post(`/integrations/hubspot/credentials`, formData);
            const credentials = response?.data;
            if (!credentials) {
                alert('No credentials returned from backend.');
                setIsConnecting(false);
                return;
            }

            setIsConnecting(false);
            setIsConnected(true);
            setIntegrationParams(prev => ({ ...prev, credentials: credentials, type: 'HubSpot' }));
        } catch (e) {
            setIsConnecting(false);
            const serverMsg = e?.response?.data?.detail ?? e?.message ?? 'Unknown error';
            console.error('Credentials error', e);
            alert(serverMsg);
        }
    }

    useEffect(() => {
        setIsConnected(integrationParams?.credentials ? true : false)
    }, []);

    return (
        <>
        <Box sx={{mt: 2}}>
            Parameters
            <Box display='flex' alignItems='center' justifyContent='center' sx={{mt: 2}}>
                <Button 
                    variant='contained' 
                    onClick={isConnected ? () => {} :handleConnectClick}
                    color={isConnected ? 'success' : 'primary'}
                    disabled={isConnecting}
                    style={{
                        pointerEvents: isConnected ? 'none' : 'auto',
                        cursor: isConnected ? 'default' : 'pointer',
                        opacity: isConnected ? 1 : undefined
                    }}
                >
                    {isConnected ? 'HubSpot Connected' : isConnecting ? <CircularProgress size={20} /> : 'Connect to HubSpot'}
                </Button>
            </Box>
        </Box>
      </>
    );
}

