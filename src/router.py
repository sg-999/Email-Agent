class SimpleRouter:
    def __init__(self):
        # Keywords that indicate each action type
        self.read_keywords = ['show', 'find', 'search', 'get', 'list', 'read', 'check', 'see', 'display']
        self.delete_keywords = ['delete', 'remove', 'trash', 'clear', 'clean']
        self.compose_keywords = ['write', 'send', 'compose', 'draft', 'reply', 'email', 'message']
    
    def classify_intent(self, user_query):
        """
        Classify user query into READ, DELETE, or COMPOSE
        Returns: (action_type, confidence)
        """
        query_lower = user_query.lower()
        
        # Count keyword matches for each category
        read_score = sum(1 for keyword in self.read_keywords if keyword in query_lower)
        delete_score = sum(1 for keyword in self.delete_keywords if keyword in query_lower)
        compose_score = sum(1 for keyword in self.compose_keywords if keyword in query_lower)
        
        # Determine action based on highest score
        scores = {
            'READ': read_score,
            'DELETE': delete_score,
            'COMPOSE': compose_score
        }
        
        action = max(scores, key=scores.get)
        confidence = scores[action]
        
        # If no keywords match, default to READ
        if confidence == 0:
            return 'READ', 0.0
        
        return action, confidence
    
    def extract_search_params(self, user_query):
        """
        Extract search parameters from user query
        Returns dict with possible filters
        """
        query_lower = user_query.lower()
        params = {}
        
        # Check for common patterns
        if 'unread' in query_lower:
            params['status'] = 'is:unread'
        
        if 'from' in query_lower:
            # Simple extraction - will be improved with LLM
            words = user_query.split()
            if 'from' in words:
                idx = words.index('from')
                if idx + 1 < len(words):
                    params['sender'] = f"from:{words[idx + 1]}"
        
        if 'subject' in query_lower or 'about' in query_lower:
            # Extract subject keywords (simplified)
            # Will be improved with LLM
            pass
        
        if 'today' in query_lower:
            params['time'] = 'newer_than:1d'
        elif 'yesterday' in query_lower:
            params['time'] = 'newer_than:2d'
        elif 'week' in query_lower:
            params['time'] = 'newer_than:7d'
        
        return params
    
    def build_gmail_query(self, params):
        """
        Convert extracted params into Gmail query string
        """
        query_parts = []
        
        if 'status' in params:
            query_parts.append(params['status'])
        if 'sender' in params:
            query_parts.append(params['sender'])
        if 'time' in params:
            query_parts.append(params['time'])
        
        # If no specific params, return empty (gets all emails)
        return ' '.join(query_parts) if query_parts else ''