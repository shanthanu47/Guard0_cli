import typer
import json
import os
import re
import time
import random
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich import box
from typing import List, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI

# Import the SAME tools the MCP server uses
from src.tools.nvd import nvd_client
from src.tools.mitre import mitre_tool
from src.build_db import download_data, build_database

load_dotenv()

app = typer.Typer()
console = Console()

# Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-001")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# Tool Definitions
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
You are Guard0, an elite Cybersecurity Intelligence AI.
You have access to the following tools:
{json.dumps(TOOLS_SCHEMA, indent=2)}

## Instructions
1. Answer the user's question accurately using the provided tools.
2. You operate in a **Reason + Act** loop.
3. For EVERY step, output your thought process, followed by one of two actions:
    a) **Execute Tool**: Output a JSON block to call a tool.
    b) **Final Answer**: Output the final response to the user.

## Format
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

def type_text(text: str, style: str = "white", speed: float = 0.005):
    """Simulates typing effect."""
    for char in text:
        console.print(char, style=style, end="")
        time.sleep(speed)
    console.print() # Newline

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
            # 1. Get LLM Response
            with console.status("[bold cyan]Guard0 AI is processing...[/bold cyan]", spinner="dots2"):
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    temperature=0.1
                )
            
            if not response or not response.choices:
                 console.print("[red]Error: Empty response from Neural Core.[/red]")
                 return

            content = response.choices[0].message.content
            messages.append({"role": "assistant", "content": content})
            
            # 2. Parse Action
            action_data = parse_json_action(content)
            
            if not action_data:
                # Assume final answer if no JSON found
                console.print(Panel(Markdown(content), title="[bold green]Guard0[/bold green]", border_style="green", box=box.ROUNDED))
                return 

            action_type = action_data.get("action")
            
            if action_type == "final_answer":
                final_content = action_data.get("content", "")
                
                # Typing effect for final answer
                console.print() # Spacer
                panel = Panel(Markdown(final_content), title="[bold green]Guard0[/bold green]", border_style="green", box=box.ROUNDED)
                console.print(panel)
                return
            
            elif action_type == "execute_tool":
                tool_name = action_data.get("tool_name")
                args = action_data.get("arguments", {})
                
                console.print(f"[dim cyan]⚡ Executing Protocol: {tool_name}[/dim cyan]")
                
                with console.status(f"[bold dim]Running {tool_name}...[/bold dim]", spinner="line"):
                    result = execute_tool(tool_name, args)
                    time.sleep(0.5) # Fake delay for 'feel'
                
                # Truncate long results for display
                result_str = json.dumps(result)
                
                # Feed back to LLM
                messages.append({"role": "user", "content": f"Observation: {result_str}"})
                step_count += 1
            
            else:
                 console.print(f"[red]Unknown directive: {action_type}[/red]")
                 return

        except Exception as e:
            console.print(f"[red]System Error: {str(e)}[/red]")
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
    console.print(Panel("Initializing Guard0 Knowledge Base...", style="bold magenta", box=box.ROUNDED))
    download_data()
    build_database()
    console.print("[green]Initialization Complete.[/green]")

@app.command()
def start():
    """Start the CLI Chatbot."""
    
    # Mac Terminal Style Header
    header = Panel(
        Text("Guard0 Intelligence Terminal v3.0", justify="center", style="bold white"),
        title="🔴 🟡 🟢  guard0-cli — -zsh — 80x24",
        border_style="white",
        box=box.ROUNDED,
        padding=(1, 2)
    )
    console.print(header)
    console.print()
    
    # Init history with system prompt
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    type_text("Initializing secure connection...", speed=0.02)
    time.sleep(0.3)
    type_text("Connected to Guard0 Core.", speed=0.02, style="green")
    console.print()
    
    while True:
        try:
            # Custom prompt style
            text = console.input("[bold cyan]➜  ~ [/bold cyan]")
            
            if text.lower() in ["exit", "quit", "q"]:
                console.print("[yellow]Terminating session...[/yellow]")
                break
            
            chat_loop(text, messages)
            
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    app()
