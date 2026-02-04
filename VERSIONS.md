# Version History

## Version 1: ReAct Agent Pattern
- **Architecture:** Separate agent module (`agent.py`) that handles LLM interaction
- **Tools:** NVD and MITRE tools exposed to agent
- **Pattern:** Agent orchestrates tool calls via ReAct prompting

## Version 2: Standard MCP Implementation
- **Architecture:** FastMCP server exposing tools via JSON-RPC protocol
- **Server:** `src/server.py` implements MCP protocol
- **Pattern:** Standard client-server architecture following MCP spec
- **Testing:** Integration tests in `tests/test_mcp_integration.py`

## Version 3: Hybrid Approach
- **Architecture:** Direct tool calling within main CLI (no separate agent layer)
- **Pattern:** ReAct loop implemented directly in `main.py`
- **Tools:** Same tool functions reused from Version 1
- **Benefits:** Simpler deployment, reduced abstraction layers
