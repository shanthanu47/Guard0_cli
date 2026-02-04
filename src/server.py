from mcp.server.fastmcp import FastMCP
from src.tools.nvd import nvd_client
from src.tools.mitre import mitre_tool

mcp = FastMCP("VulnBot MCP Server")

@mcp.tool()
def get_cve(cve_id: str) -> dict:
    """
    Get details for a specific CVE.
    
    Args:
        cve_id: The CVE ID (e.g., CVE-2023-12345)
    """
    return nvd_client.get_cve(cve_id)

@mcp.tool()
def search_mitre_techniques(query: str) -> list[dict]:
    """
    Search for MITRE ATT&CK techniques by name or ID.
    
    Args:
        query: Search term (e.g., "phishing", "T1059")
    """
    return mitre_tool.search_techniques(query)

@mcp.tool()
def get_mitre_technique(mitre_id: str) -> dict:
    """
    Get full details for a specific MITRE technique.
    
    Args:
        mitre_id: The technique ID (e.g., T1059)
    """
    return mitre_tool.get_technique(mitre_id)

if __name__ == "__main__":
    mcp.run()
