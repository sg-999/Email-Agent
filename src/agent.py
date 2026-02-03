from email_client import EmailClient
from router import SimpleRouter

class EmailAgent:
    def __init__(self):
        self.client = EmailClient()
        self.router = SimpleRouter()
        print("✅ Email Agent initialized successfully!")
    
    def process_query(self, user_query):
        """
        Main processing pipeline:
        1. Classify intent
        2. Route to appropriate handler
        3. Execute action
        4. Return result
        """
        print(f"\n🔍 Processing: '{user_query}'")
        print("-" * 60)
        
        # Step 1: Classify intent
        action, confidence = self.router.classify_intent(user_query)
        print(f"📋 Detected action: {action} (confidence: {confidence})")
        
        # Step 2: Route to handler
        if action == 'READ':
            return self._handle_read(user_query)
        elif action == 'DELETE':
            return self._handle_delete(user_query)
        elif action == 'COMPOSE':
            return self._handle_compose(user_query)
        else:
            return "❌ Could not determine action type"
    
    def _handle_read(self, user_query):
        """Handle READ queries - search and display emails"""
        print("📧 Executing READ action...")
        
        # Extract search parameters
        params = self.router.extract_search_params(user_query)
        gmail_query = self.router.build_gmail_query(params)
        
        print(f"🔎 Gmail query: '{gmail_query if gmail_query else 'all emails'}'")
        
        # Search emails
        emails = self.client.search_emails(gmail_query, max_results=5)
        
        if not emails:
            return "📭 No emails found matching your criteria"
        
        # Format results
        result = f"📬 Found {len(emails)} email(s):\n\n"
        
        for i, email in enumerate(emails, 1):
            result += f"{i}. Subject: {email['subject']}\n"
            result += f"   From: {email['from']}\n"
            result += f"   Date: {email['date']}\n"
            result += f"   Snippet: {email['snippet'][:100]}...\n"
            result += f"   ID: {email['id']}\n"
            result += "-" * 50 + "\n"
        
        return result
    
    def _handle_delete(self, user_query):
        """Handle DELETE queries - trash emails"""
        print("🗑️  Executing DELETE action...")
        
        # Extract search parameters to find emails to delete
        params = self.router.extract_search_params(user_query)
        gmail_query = self.router.build_gmail_query(params)
        
        print(f"🔎 Finding emails to delete with query: '{gmail_query if gmail_query else 'all emails'}'")
        
        # Search emails
        emails = self.client.search_emails(gmail_query, max_results=5)
        
        if not emails:
            return "📭 No emails found to delete"
        
        # Show emails and ask for confirmation
        print(f"\n⚠️  Found {len(emails)} email(s) to delete:")
        for i, email in enumerate(emails, 1):
            print(f"{i}. {email['subject']} (from {email['from']})")
        
        confirm = input("\n⚠️  Type 'yes' to confirm deletion: ")
        
        if confirm.lower() != 'yes':
            return "❌ Deletion cancelled"
        
        # Delete emails
        deleted_count = 0
        for email in emails:
            if self.client.trash_email(email['id']):
                deleted_count += 1
        
        return f"✅ Successfully moved {deleted_count} email(s) to trash"
    
    def _handle_compose(self, user_query):
        """Handle COMPOSE queries - draft/send emails"""
        print("✍️  Executing COMPOSE action...")
        
        # For now, we'll use manual input
        # In next step, LLM will generate this automatically
        
        print("\n📝 Email composition (LLM generation coming in next step)")
        
        to = input("To: ")
        subject = input("Subject: ")
        print("Body (press Enter twice when done):")
        
        body_lines = []
        while True:
            line = input()
            if line == "" and body_lines and body_lines[-1] == "":
                break
            body_lines.append(line)
        
        body = "\n".join(body_lines[:-1])  # Remove last empty line
        
        # Show preview
        print("\n" + "=" * 60)
        print("📧 EMAIL PREVIEW")
        print("=" * 60)
        print(f"To: {to}")
        print(f"Subject: {subject}")
        print(f"Body:\n{body}")
        print("=" * 60)
        
        send = input("\n📤 Send this email? (yes/no): ")
        
        if send.lower() == 'yes':
            message_id = self.client.send_email(to, subject, body)
            if message_id:
                return f"✅ Email sent successfully! Message ID: {message_id}"
            else:
                return "❌ Failed to send email"
        else:
            return "❌ Email not sent"