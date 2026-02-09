"""Base handler with shared dependencies."""


class BaseHandler:
    """Base class for action handlers. Provides client and router access."""

    def __init__(self, client, router=None):
        self.client = client
        self.router = router
