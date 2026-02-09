from .base import BaseHandler


class ReadHandler(BaseHandler):
    """Handler for READ queries - search and display emails."""

    def execute(self, params):
        print("📧 Executing READ action...")

        gmail_query = self.router.build_gmail_query(params)
        max_results = self.router.get_max_results(params)

        print(f"🔎 Gmail query: '{gmail_query if gmail_query else 'all emails'}'")
        print(f"   Max results: {max_results}")

        emails = self.client.search_emails(gmail_query, max_results=max_results)

        if not emails:
            return "📭 No emails found matching your criteria"

        result = f"📬 Found {len(emails)} email(s):\n\n"
        for i, email in enumerate(emails, 1):
            result += f"{i}. Subject: {email['subject']}\n"
            result += f"   From: {email['from']}\n"
            result += f"   Date: {email['date']}\n"
            result += f"   Snippet: {email['snippet'][:100]}...\n"
            result += f"   ID: {email['id']}\n"
            result += "-" * 50 + "\n"

        return result
