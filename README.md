# Email Agent

A chat-based agent that helps manage your Gmail via natural language. Read, delete, and compose emails through conversational commands.

## Prerequisites

1. **Gmail** – You need a Google account with Gmail
2. **Groq API Key** – For LLM-based intent routing (free tier available)

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Groq API Key (Required)

The agent uses Groq's LLM to understand your natural language queries.

**How to get your Groq API key:**

1. Go to [https://console.groq.com/keys](https://console.groq.com/keys)
2. Sign up or log in (free account available)
3. Click **Create API Key**
4. Copy the key and store it securely

**Configure the API key** (choose one method):

**Option A: Environment variable**

```bash
export GROQ_API_KEY=your-api-key-here
```

**Option B: `.env` file (recommended)**

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```
2. Edit `.env` and add your key:
   ```
   GROQ_API_KEY=your-api-key-here
   ```
3. The `.env` file is gitignored – your key stays local and secure

### 3. Gmail OAuth

1. Create a project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the Gmail API
3. Create OAuth 2.0 credentials (Desktop application)
4. Download the credentials JSON and save as `config/credentials.json`
5. On first run, the agent will open a browser to authorize access

## Run

From the project root:

```bash
python main.py
```

## Example Commands

- *"Show my unread emails"*
- *"Find emails from john@example.com"*
- *"List emails from this week"*
- *"Delete spam emails from newsletter@example.com"*
- *"Send an email to mom"*

## Architecture

- **Agent** (`agent.py`): Orchestrates routing and delegates to handlers
- **Router** (`router.py`): Groq LLM classifies intent (READ/DELETE/COMPOSE) and extracts search params from natural language
- **Handlers** (`handlers/`): Action-specific logic
  - `read.py` – Search and display emails
  - `delete.py` – Trash emails with confirmation
  - `compose.py` – Compose and send emails
- **Email Client** (`email_client.py`): Gmail API integration
