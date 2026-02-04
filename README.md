# VulnBot - Cybersecurity Intelligence Chatbot

A Multi-Architecture AI Assistant for Vulnerability Research

VulnBot is an intelligent CLI chatbot that helps security researchers query CVE vulnerabilities and MITRE ATT&CK techniques. This project demonstrates three different architectural approaches: Monolithic Agent, Pure MCP Server, and Hybrid.

## Table of Contents

- [Features](#features)
- [Architecture Versions](#architecture-versions)
- [API Integrations](#api-integrations)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Testing](#testing)

## Features

- CVE Lookup: Fetch detailed vulnerability information from the NVD API
- MITRE ATT&CK Search: Query techniques, tactics, and procedures
- Natural Language Interface: Conversational interaction with context retention
- MCP Architecture: Standards-compliant Model Context Protocol server
- Smart Caching: Disk-based caching for faster repeated queries
- Comprehensive Testing: Edge case validation and context verification

## Architecture Versions

This project evolved through three distinct architectural patterns, each demonstrating different design principles and trade-offs.

### Version 1: Monolithic Agent Pattern

**Status**: Initial implementation

**Characteristics:**
- All components in single process
- Agent-based reasoning loop
- Direct function calls between layers
- Full context retention

**Files**: `src/agent.py`, `src/main.py` (v1)

### Version 2: Pure MCP Server

**Status**: Available via `python -m src.server`

**Characteristics:**
- Standards-compliant MCP protocol
- JSON-RPC communication
- Universal compatibility with MCP clients
- No built-in UI

**Files**: `src/server.py`, `src/tools/*`

### Version 3: Hybrid Approach (Current)

**Status**: Primary implementation

**Characteristics:**
- Interactive CLI for users
- Direct tool calling without agent layer
- Shared tool implementations with MCP server
- ReAct loop implemented in main client

**Files**: `src/main.py`, `src/server.py`, `src/tools/*`

## API Integrations

### 1. NVD (National Vulnerability Database)

**Purpose**: Fetch CVE vulnerability details

**Implementation**: `src/tools/nvd.py`

**Features**:
- REST API integration via httpx
- Disk-based caching (24 hours TTL)
- Rate limit awareness
- Error handling for non-existent CVEs

**Example Query**:
```python
get_cve("CVE-2021-44228")
```

### 2. MITRE ATT&CK

**Purpose**: Search and retrieve attack techniques

**Implementation**: `src/tools/mitre.py`

**Features**:
- Local SQLite database (pre-populated)
- Full-text search on technique names/descriptions
- Technique detail lookup by ID
- JSON parsing for platform tags

**Example Queries**:
```python
search_mitre_techniques("phishing")
get_mitre_technique("T1566")
```

**Database Schema**:
```sql
CREATE TABLE techniques (
    mitre_id TEXT PRIMARY KEY,
    name TEXT,
    description TEXT,
    platforms TEXT,
    url TEXT
);
```

## Installation

### Prerequisites
- Python 3.10+
- pip
- Internet connection (for NVD API)

### Setup

```bash
# Clone repository
git clone https://github.com/shanthanu47/Guard0_cli.git
cd Guard0_cli

# Install dependencies
pip install -e .

# Configure environment
cp .env.example .env

# Initialize MITRE database
python -m src.main init
```

See SETUP.md for detailed installation instructions.

## Usage

### 1. Hybrid CLI (Version 3 - Recommended)
The default mode with Mac Terminal UI and typing animations.

```bash
python -m src.main start
```

### 2. Pure MCP Server (Version 2)
Run the server for use with MCP clients (like Claude Desktop) or integration tests.

```bash
python -m src.server
```

**Manual Interaction:**
Since V2 is a "headless" server, we included a custom client so you can manually interact with it:

```bash
python run_v2_manual.py
```

Or run the verification suite:
```bash
python tests/test_mcp_integration.py
```

### 3. Monolithic Agent (Version 1 - Legacy)
Run the legacy agent architecture for comparison.

```bash
python run_v1_demo.py
```

## Project Structure

```
Guard0_cli/
├── src/
│   ├── main.py              # Version 3: Hybrid CLI client
│   ├── server.py            # Version 2: MCP server
│   ├── agent.py             # Version 1: Legacy agent logic
│   ├── db.py                # Database utilities
│   ├── build_db.py          # MITRE database builder
│   └── tools/               # Shared Tools
│       ├── nvd.py
│       └── mitre.py
├── tests/
│   └── test_mcp_integration.py
├── run_v1_demo.py           # Script to run Version 1
├── data/
│   └── mitre.db
├── pyproject.toml
├── requirements.txt
├── .env.example
├── SETUP.md
├── VERSIONS.md
└── README.md
```

## Testing

### Run All Tests

```bash
python tests/test_mcp_integration.py
```

### Manual Testing

```bash
# Test NVD integration
python -c "from src.tools.nvd import nvd_client; print(nvd_client.get_cve('CVE-2021-44228'))"

# Test MITRE search
python -c "from src.tools.mitre import mitre_tool; print(mitre_tool.search_techniques('phishing'))"
```

