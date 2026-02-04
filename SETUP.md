# Setup Guide

## Prerequisites

- Python 3.10 or higher
- pip package manager
- Git
- Internet connection for API access

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/shanthanu47/Guard0_cli.git
cd Guard0_cli
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Or using pyproject.toml:

```bash
pip install -e .
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and add your OpenRouter API key:

```
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=arcee-ai/trinity-large-preview:free
```

To get an API key:
1. Visit https://openrouter.ai
2. Sign up for an account
3. Generate an API key from the dashboard

### 5. Initialize MITRE Database

```bash
python -m src.main init
```

This will:
- Download the MITRE ATT&CK dataset
- Build a local SQLite database
- Set up caching directories

Expected output:
```
Downloading MITRE ATT&CK data...
Building database...
Done!
```

### 6. Verify Installation

Test the CLI:

```bash
python -m src.main start
```

Test the MCP server:

```bash
python -m src.server
```

## Troubleshooting

### Issue: "ModuleNotFoundError"

**Solution**: Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: "OPENROUTER_API_KEY not found"

**Solution**: Check that `.env` file exists and contains the API key.

### Issue: "Database not initialized"

**Solution**: Run the initialization command:
```bash
python -m src.main init
```

### Issue: "NVD API rate limit exceeded"

**Solution**: Wait a few minutes. The NVD API has rate limits. Cached results will be used for repeated queries.

## Usage Examples

### CLI Mode

```bash
python -m src.main start
```

Example queries:
```
You > Show me details for CVE-2021-44228
You > What are attack patterns for phishing?
You > Tell me about technique T1059
```

### MCP Server Mode

1. Start the server:
```bash
python -m src.server
```

2. Configure your MCP client (Claude Desktop, VS Code, etc.)

3. Use the exposed tools:
   - get_cve
   - search_mitre_techniques
   - get_mitre_technique

## Development Setup

For development work:

```bash
# Install in editable mode
pip install -e .

# Run tests
python tests/test_mcp_integration.py
```

## Next Steps

- See README.md for architecture details
- See VERSIONS.md for implementation approaches
- Check the examples in the Usage section

## Support

For issues or questions:
- Check the GitHub Issues page
- Review the documentation in README.md
- Verify your environment setup matches the prerequisites
