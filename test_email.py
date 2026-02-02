from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os.path

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def authenticate():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'config/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds)

def get_recent_emails(service, max_results=5):
    results = service.users().messages().list(
        userId='me', maxResults=max_results).execute()
    messages = results.get('messages', [])
    
    for msg in messages:
        message = service.users().messages().get(
            userId='me', id=msg['id']).execute()
        
        # Get subject
        headers = message['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        
        print(f"Subject: {subject}")
        print(f"ID: {msg['id']}")
        print("-" * 50)

if __name__ == "__main__":
    service = authenticate()
    print("Successfully authenticated!")
    get_recent_emails(service)