# VulnBot - Cybersecurity Intelligence Chatbot

A Multi-Architecture AI Assistant for Vulnerability Research

VulnBot is an intelligent CLI chatbot that helps security researchers query CVE vulnerabilities and MITRE ATT&CK techniques. This project demonstrates three different architectural approaches: Monolithic Agent, Pure MCP Server, and Hybrid.

## Table of Contents

- [Features](#features)
- [Architecture Versions](#architecture-versions)
- [API Integrations](#api-integrations)
- [Installation](#installation)
- [Usage](#usage)
- [Architecture Comparison](#architecture-comparison)
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

### Option A: Hybrid CLI (Recommended)

```bash
python -m src.main start
```

Example conversation:
```
You > What is CVE-2021-44228?
Bot > [Fetches from NVD and explains Log4Shell]
You > What's the CVSS score?
Bot > [Remembers context, extracts score]
```

### Option B: Pure MCP Server

```bash
python -m src.server
```

Then connect from Claude Desktop or other MCP clients.

## Architecture Comparison

| Feature | Monolithic | Pure MCP | Hybrid |
|---------|-----------|----------|--------|
| CLI Interface | Yes | No | Yes |
| MCP Compatibility | No | Yes | Yes |
| Reusable Tools | No | Yes | Yes |
| Context Retention | Yes | Client-dependent | Yes |
| Ease of Development | High | Medium | Medium |
| Production Ready | Medium | Medium | High |
| Best For | Prototyping | Integration | End Users |

### Detailed Comparison

#### Version 1: Monolithic Agent

**Pros**:
- Simple architecture
- Fast execution
- Easy to understand

**Cons**:
- Tools locked into one application
- Cannot integrate with external clients
- Poor separation of concerns

**Use Case**: Quick prototypes, learning projects

#### Version 2: Pure MCP Server

**Pros**:
- Universal MCP client compatibility
- Clean tool abstraction
- Industry-standard protocol

**Cons**:
- No built-in user interface
- Requires external client for interaction
- More complex debugging

**Use Case**: Tool libraries, enterprise integrations

#### Version 3: Hybrid Approach

**Pros**:
- Best of both worlds
- Production-ready chatbot
- MCP-compatible for extensibility
- Simplified architecture

**Cons**:
- Requires understanding of ReAct pattern
- Multiple deployment modes to maintain

**Use Case**: This project's chosen architecture - provides both a usable CLI and demonstrates MCP compatibility.

## Project Structure

```
Guard0_cli/
├── src/
│   ├── main.py              # Hybrid CLI client
│   ├── server.py            # MCP server
│   ├── db.py                # Database utilities
│   ├── build_db.py          # MITRE database builder
│   └── tools/
│       ├── nvd.py           # NVD API client
│       └── mitre.py         # MITRE ATT&CK queries
├── tests/
│   └── test_mcp_integration.py
├── data/
│   └── mitre.db             # SQLite database
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

## Assignment Context

This project demonstrates:

1. MCP Architecture Understanding: src/server.py implements Model Context Protocol
2. Tool Integration: Both NVD REST API and MITRE database queries
3. Production Quality: Includes error handling, caching, and testing
4. Architectural Evolution: Shows progression from monolithic to MCP to hybrid

The Hybrid Approach was chosen because it:
- Meets the CLI Chatbot requirement
- Demonstrates MCP architecture capability
- Provides a deployable end product
- Shows understanding of appropriate pattern selection

## License

MIT License

## Acknowledgments

- Anthropic MCP - Protocol specification
- NVD API - Vulnerability data
- MITRE ATT&CK - Threat intelligence framework
