from .base import BaseHandler


class ComposeHandler(BaseHandler):
    """Handler for COMPOSE queries - draft/send emails."""

    def execute(self, user_query):
        print("✍️  Executing COMPOSE action...")

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

        body = "\n".join(body_lines[:-1]) if body_lines else ""

        print("\n" + "=" * 60)
        print("📧 EMAIL PREVIEW")
        print("=" * 60)
        print(f"To: {to}")
        print(f"Subject: {subject}")
        print(f"Body:\n{body}")
        print("=" * 60)

        send = input("\n📤 Send this email? (yes/no): ")

        if send.lower() == "yes":
            message_id = self.client.send_email(to, subject, body)
            if message_id:
                return f"✅ Email sent successfully! Message ID: {message_id}"
            return "❌ Failed to send email"
        return "❌ Email not sent"
