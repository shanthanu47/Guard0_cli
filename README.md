# Vulnerability Intelligence CLI

A CLI chatbot that queries vulnerability databases (NVD) and threat intelligence (MITRE ATT&CK) using an AI Agent.

## Setup

1.  **Install Dependencies:**
    ```bash
    pip install .
    ```

2.  **Environment Variables:**
    Copy `.env.example` to `.env` and add your OpenRouter API Key.
    ```bash
    cp .env.example .env
    ```

3.  **Initialize Data:**
    This will download the MITRE ATT&CK data and build the local SQLite database.
    ```bash
    python src/build_db.py
    ```
    *(Note: This step is required before running the bot)*

## Usage

```bash
# Start the chat
python src/main.py start
```

## Architecture
- **Brain:** DeepSeek R1 (via OpenRouter) using ReAct prompting.
- **Data:**
    - NVD API (cached locally via `diskcache`)
    - MITRE ATT&CK (ETL to SQLite via `mitreattack-python`)
- **UI:** Typer + Rich
