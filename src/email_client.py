from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import os.path
import base64
from email.mime.text import MIMEText

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

class EmailClient:
    def __init__(self):
        # Define paths relative to this file (src/email_client.py)
        # Go up two levels: src/ -> Email-Agent/
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.credentials_path = os.path.join(self.base_dir, 'config', 'credentials.json')
        self.token_path = os.path.join(self.base_dir, 'token.json')
        self.service = self._authenticate()
    
    def _authenticate(self):
        """Handle Gmail authentication"""
        creds = None
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        
        return build('gmail', 'v1', credentials=creds)
    
    def search_emails(self, query, max_results=10):
        """
        Search emails using Gmail query syntax
        Examples:
        - "from:example@gmail.com"
        - "subject:meeting"
        - "is:unread"
        - "after:2024/01/01"
        """
        try:
            results = self.service.users().messages().list(
                userId='me', 
                q=query, 
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                return []
            
            email_list = []
            for msg in messages:
                email_data = self._get_email_details(msg['id'])
                email_list.append(email_data)
            
            return email_list
        
        except Exception as e:
            print(f"Error searching emails: {e}")
            return []
    
    def _get_email_details(self, message_id):
        """Get detailed information about a specific email"""
        try:
            message = self.service.users().messages().get(
                userId='me', 
                id=message_id,
                format='full'
            ).execute()
            
            headers = message['payload']['headers']
            
            # Extract key information
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
            
            # Get email body
            body = self._get_email_body(message['payload'])
            
            return {
                'id': message_id,
                'subject': subject,
                'from': sender,
                'date': date,
                'snippet': message.get('snippet', ''),
                'body': body
            }
        
        except Exception as e:
            print(f"Error getting email details: {e}")
            return None
    
    def _get_email_body(self, payload):
        """Extract email body from payload"""
        try:
            if 'parts' in payload:
                # Multipart email
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        data = part['body'].get('data', '')
                        if data:
                            return base64.urlsafe_b64decode(data).decode('utf-8')
            else:
                # Simple email
                data = payload['body'].get('data', '')
                if data:
                    return base64.urlsafe_b64decode(data).decode('utf-8')
            
            return "No body content"
        
        except Exception as e:
            return f"Error decoding body: {e}"
    
    def send_email(self, to, subject, body):
        """Send an email"""
        try:
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            send_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            print(f"Email sent! Message ID: {send_message['id']}")
            return send_message['id']
        
        except Exception as e:
            print(f"Error sending email: {e}")
            return None
    
    def delete_email(self, message_id):
        """Delete an email permanently"""
        try:
            self.service.users().messages().delete(
                userId='me',
                id=message_id
            ).execute()
            
            print(f"Email {message_id} deleted successfully!")
            return True
        
        except Exception as e:
            print(f"Error deleting email: {e}")
            return False
    
    def trash_email(self, message_id):
        """Move email to trash (safer than delete)"""
        try:
            self.service.users().messages().trash(
                userId='me',
                id=message_id
            ).execute()
            
            print(f"Email {message_id} moved to trash!")
            return True
        
        except Exception as e:
            print(f"Error trashing email: {e}")
            return False