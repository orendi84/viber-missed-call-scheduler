#!/usr/bin/env python3
"""
Google API Authentication System
Handles OAuth2 authentication for Gmail and Calendar APIs
"""

import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

class GoogleAPIAuth:
    def __init__(self, credentials_file="credentials.json"):
        self.credentials_file = credentials_file
        self.token_file = "token.pickle"
        
        # Define scopes for Gmail and Calendar access
        self.SCOPES = [
            'https://www.googleapis.com/auth/gmail.readonly',      # Read Gmail
            'https://www.googleapis.com/auth/gmail.send',          # Send Gmail  
            'https://www.googleapis.com/auth/gmail.compose',       # Compose Gmail
            'https://www.googleapis.com/auth/calendar.readonly',   # Read Calendar
            'https://www.googleapis.com/auth/calendar.events'      # Manage Calendar events
        ]
        
    def authenticate(self):
        """
        Authenticate and return credentials
        """
        creds = None
        
        # Check if token file exists (saved credentials)
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # If there are no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("Refreshing expired credentials...")
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    print(f"❌ Error: {self.credentials_file} not found!")
                    print("Please download your OAuth2 credentials JSON file from Google Cloud Console")
                    print("and save it as 'credentials.json' in the current directory.")
                    return None
                
                print("🔐 Starting OAuth2 authentication...")
                print("Your browser will open for Google authentication.")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
            
            print("✅ Authentication successful!")
        
        return creds
    
    def get_gmail_service(self):
        """Get Gmail API service"""
        creds = self.authenticate()
        if creds:
            return build('gmail', 'v1', credentials=creds)
        return None
    
    def get_calendar_service(self):
        """Get Calendar API service"""
        creds = self.authenticate()
        if creds:
            return build('calendar', 'v3', credentials=creds)
        return None
    
    def test_connection(self):
        """Test if authentication works"""
        print("🧪 Testing Google API connections...")
        
        # Test Gmail
        try:
            gmail_service = self.get_gmail_service()
            if gmail_service:
                profile = gmail_service.users().getProfile(userId='me').execute()
                print(f"✅ Gmail: Connected as {profile['emailAddress']}")
                print(f"   Total messages: {profile.get('messagesTotal', 0)}")
            else:
                print("❌ Gmail: Connection failed")
        except Exception as e:
            print(f"❌ Gmail error: {e}")
        
        # Test Calendar
        try:
            calendar_service = self.get_calendar_service()
            if calendar_service:
                calendar_list = calendar_service.calendarList().list().execute()
                calendars = calendar_list.get('items', [])
                print(f"✅ Calendar: Connected")
                print(f"   Available calendars: {len(calendars)}")
                for cal in calendars[:3]:  # Show first 3
                    print(f"   - {cal['summary']}")
                if len(calendars) > 3:
                    print(f"   ... and {len(calendars) - 3} more")
            else:
                print("❌ Calendar: Connection failed")
        except Exception as e:
            print(f"❌ Calendar error: {e}")

if __name__ == "__main__":
    auth = GoogleAPIAuth()
    auth.test_connection()