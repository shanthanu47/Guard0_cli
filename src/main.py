import typer
import json
import os
import re
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from typing import List, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI

from src.tools.nvd import nvd_client
from src.tools.mitre import mitre_tool
from src.build_db import download_data, build_database

load_dotenv()

app = typer.Typer()
console = Console()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-r1:free")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

TOOLS_SCHEMA = [
    {
        "name": "get_cve",
        "description": "Fetch details for a specific CVE ID. Returns descriptions.",
        "parameters": {
            "type": "object",
            "properties": {
                "cve_id": {"type": "string", "description": "The CVE ID (e.g. CVE-2021-44228)."}
            },
            "required": ["cve_id"]
        }
    },
    {
        "name": "search_mitre_techniques",
        "description": "Search for MITRE ATT&CK Techniques by keyword. Returns a list of matching techniques with IDs.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search keyword (e.g. 'phishing')."}
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_mitre_technique",
        "description": "Get full details for a specific MITRE Technique ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "mitre_id": {"type": "string", "description": "The technique ID (e.g. T1059)."}
            },
            "required": ["mitre_id"]
        }
    }
]

SYSTEM_PROMPT = f"""
You are a Cyber Security Analyst Assistant CLI.
You have access to the following tools:
{json.dumps(TOOLS_SCHEMA, indent=2)}

1. Answer the user's question accurately using the provided tools.
2. You operate in a **Reason + Act** loop.
3. For EVERY step, output your thought process, followed by one of two actions:
    a) **Execute Tool**: Output a JSON block to call a tool.
    b) **Final Answer**: Output the final response to the user.

To call a tool, use this EXACT format (markdown code block):
```json
{{
  "action": "execute_tool",
  "tool_name": "get_cve",
  "arguments": {{ "cve_id": "CVE-2021-44228" }}
}}
```

To provide the answer, use this format:
```json
{{
  "action": "final_answer",
  "content": "The Log4j vulnerability..."
}}
```
"""

def execute_tool(tool_name: str, args: dict):
    """Executes the tool locally (Hybrid Pattern)."""
    try:
        if tool_name == "get_cve":
            return nvd_client.get_cve(args.get("cve_id"))
        elif tool_name == "search_mitre_techniques":
            return mitre_tool.search_techniques(args.get("query"))
        elif tool_name == "get_mitre_technique":
            return mitre_tool.get_technique(args.get("mitre_id"))
        else:
            return {"error": f"Tool '{tool_name}' not found."}
    except Exception as e:
        return {"error": str(e)}

def chat_loop(user_input: str, messages: List[Dict]):
    """Handles the reasoning loop."""
    messages.append({"role": "user", "content": user_input})
    
    step_count = 0
    MAX_STEPS = 5
    
    while step_count < MAX_STEPS:
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=0.1
            )
            
            if not response or not response.choices:
                 console.print("[red]Error: Empty response from LLM.[/red]")
                 return

            content = response.choices[0].message.content
            messages.append({"role": "assistant", "content": content})
            

            action_data = parse_json_action(content)
            
            if not action_data:
                console.print(Markdown(content))
                return 

            action_type = action_data.get("action")
            
            if action_type == "final_answer":
                console.print(Markdown(action_data.get("content", "")))
                return
            
            elif action_type == "execute_tool":
                tool_name = action_data.get("tool_name")
                args = action_data.get("arguments", {})
                
                console.print(f"[bold cyan]🛠️  Using Tool: {tool_name}[/bold cyan] [dim]{json.dumps(args)}[/dim]")
                
                result = execute_tool(tool_name, args)
                
                result_str = json.dumps(result)
                display_str = (result_str[:200] + '...') if len(result_str) > 200 else result_str
                console.print(f"[dim]Result: {display_str}[/dim]")
                
                messages.append({"role": "user", "content": f"Observation: {result_str}"})
                step_count += 1
            
            else:
                 console.print(f"[red]Unknown action: {action_type}[/red]")
                 return

        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            return

def parse_json_action(text: str):
    """Robust JSON extractor."""
    try:
        match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        match = re.search(r"(\{.*\})$", text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
    except:
        pass
    return None

@app.command()
def init():
    """Initializes the database."""
    console.print(Panel("Initializing Data...", style="bold magenta"))
    download_data()
    build_database()
    console.print("[green]Done![/green]")

@app.command()
def start():
    """Start the CLI Chatbot."""
    console.print(Panel.fit("🛡️  VulnBot Hybrid Client  🛡️", style="bold cyan"))
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    while True:
        try:
            text = console.input("\n[bold green]You > [/bold green]")
            if text.lower() in ["exit", "quit", "q"]:
                console.print("[yellow]Goodbye![/yellow]")
                break
            
            chat_loop(text, messages)
            
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    app()
