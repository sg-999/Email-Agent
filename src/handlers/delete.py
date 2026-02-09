from .base import BaseHandler


class DeleteHandler(BaseHandler):
    """Handler for DELETE queries - trash emails."""

    def execute(self, params):
        print("🗑️  Executing DELETE action...")

        gmail_query = self.router.build_gmail_query(params)
        max_results = self.router.get_max_results(params)

        print(f"🔎 Finding emails to delete with query: '{gmail_query if gmail_query else 'all emails'}'")

        emails = self.client.search_emails(gmail_query, max_results=max_results)

        if not emails:
            return "📭 No emails found to delete"

        print(f"\n⚠️  Found {len(emails)} email(s) to delete:")
        for i, email in enumerate(emails, 1):
            print(f"{i}. {email['subject']} (from {email['from']})")

        confirm = input("\n⚠️  Type 'yes' to confirm deletion: ")

        if confirm.lower() != "yes":
            return "❌ Deletion cancelled"

        deleted_count = 0
        for email in emails:
            if self.client.trash_email(email["id"]):
                deleted_count += 1

        return f"✅ Successfully moved {deleted_count} email(s) to trash"
