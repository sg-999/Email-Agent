from .email_client import EmailClient
from .router import LLMRouter
from .handlers import ReadHandler, DeleteHandler, ComposeHandler


class EmailAgent:
    def __init__(self, groq_api_key=None):
        self.client = EmailClient()
        self.router = LLMRouter(api_key=groq_api_key)
        self._handlers = {
            "READ": ReadHandler(self.client, self.router),
            "DELETE": DeleteHandler(self.client, self.router),
            "COMPOSE": ComposeHandler(self.client),
        }
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

        action, params = self.router.classify_and_extract(user_query)
        print(f"📋 Detected action: {action}")
        if params:
            print(f"   Params: {params}")

        handler = self._handlers.get(action)
        if not handler:
            return "❌ Could not determine action type"

        if action == "COMPOSE":
            return handler.execute(user_query)
        return handler.execute(params)
