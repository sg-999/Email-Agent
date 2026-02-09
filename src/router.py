import json
import os
import re

from groq import Groq

# Load .env from project root if python-dotenv is installed
try:
    from dotenv import load_dotenv
    _project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(os.path.join(_project_root, ".env"))
except ImportError:
    pass  # Use env vars directly if dotenv not installed


class LLMRouter:
    """
    Router that uses Groq LLM to classify user intent and extract search parameters
    from natural language email management queries.
    """

    def __init__(self, api_key=None, model="llama-3.3-70b-versatile"):
        """
        Initialize the LLM router.

        Args:
            api_key: Groq API key. If None, uses GROQ_API_KEY env var.
            model: Groq model ID. Default: llama-3.3-70b-versatile
        """
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Groq API key not found. Set GROQ_API_KEY in your environment "
                "or pass api_key to LLMRouter(). See README for setup instructions."
            )
        self.client = Groq(api_key=self.api_key)
        self.model = model

    def classify_and_extract(self, user_query):
        """
        Use Groq LLM to classify intent and extract search parameters in one call.

        Returns:
            tuple: (action, params)
                - action: 'READ' | 'DELETE' | 'COMPOSE'
                - params: dict with optional keys: status, sender, time, subject
        """
        system_prompt = """You are an intent classifier for an email management assistant.
Given a user's message, determine:
1. The ACTION: one of READ, DELETE, or COMPOSE
   - READ: user wants to view, search, list, find, check, or see emails
   - DELETE: user wants to delete, remove, trash, or clear emails
   - COMPOSE: user wants to send, write, compose, draft, reply to, or email someone

2. Search parameters (for READ and DELETE only; leave empty for COMPOSE):
   - status: "is:unread" if user mentions unread, else null
   - sender: email address or domain if user says "from X" (format as "from:value" for Gmail)
   - time: Gmail time filter - "newer_than:1d" (today), "newer_than:2d" (yesterday), "newer_than:7d" (week), "newer_than:30d" (month), or null
   - subject: keywords for subject search (format as "subject:value" for Gmail), or null
   - max_results: integer 1-50 when user specifies a count (e.g. "top 2", "show 3 emails", "first 5", "last 10"). Use null if not specified.

Respond with ONLY a valid JSON object, no markdown or extra text. Format:
{"action": "READ|DELETE|COMPOSE", "params": {"status": "..." or null, "sender": "..." or null, "time": "..." or null, "subject": "..." or null, "max_results": number or null}}

Use null for any param not present in the user's message."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query},
                ],
            )
            content = response.choices[0].message.content.strip()

            # Extract JSON from response (handle markdown code blocks if present)
            json_match = re.search(r"\{[\s\S]*\}", content)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(content)

            action = data.get("action", "READ").upper()
            if action not in ("READ", "DELETE", "COMPOSE"):
                action = "READ"

            params = data.get("params", {})
            if not isinstance(params, dict):
                params = {}

            # Filter out null values
            params = {k: v for k, v in params.items() if v is not None and v != ""}

            return action, params

        except (json.JSONDecodeError, KeyError, IndexError) as e:
            # Fallback to READ with empty params on parse errors
            return "READ", {}

    def build_gmail_query(self, params):
        """
        Convert extracted params into Gmail query string.

        Args:
            params: dict with optional keys: status, sender, time, subject
        """
        query_parts = []

        for key in ("status", "sender", "time", "subject"):
            if key in params and params[key]:
                value = params[key]
                # Ensure sender/subject have proper Gmail prefix if not already present
                if key == "sender" and not value.startswith("from:"):
                    value = f"from:{value}"
                elif key == "subject" and not value.startswith("subject:"):
                    value = f"subject:{value}"
                query_parts.append(value)

        return " ".join(query_parts) if query_parts else ""

    def get_max_results(self, params):
        """Extract and validate max_results from params. Default 5 if missing or invalid."""
        value = params.get("max_results")
        if value is None:
            return 5
        try:
            n = int(value) if not isinstance(value, int) else value
            if 1 <= n <= 50:
                return n
        except (TypeError, ValueError):
            pass
        return 5
