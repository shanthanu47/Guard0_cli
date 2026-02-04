import subprocess
import json
import sys
import os
from rich.console import Console
from rich.panel import Panel

console = Console()

def send_json(process, data):
    try:
        json_str = json.dumps(data)
        process.stdin.write(json_str + "\n")
        process.stdin.flush()
    except Exception as e:
        console.print(f"[red]❌ Error sending data: {e}[/red]")

def read_json(process):
    try:
        line = process.stdout.readline()
        if not line:
            return None
        return json.loads(line)
    except Exception as e:
        console.print(f"[red]❌ Error reading data: {e}[/red]")
        return None

def main():
    console.print(Panel("🛡️  Version 2: Manual MCP Client  🛡️", style="bold purple"))
    console.print("[dim]This client connects to the headless 'src.server' via stdio.[/dim]")
    console.print("Type 'exit' to quit.\n")
    
    # Start the server
    process = subprocess.Popen(
        [sys.executable, "-m", "src.server"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0 
    )

    try:
        # Initialize Handshake
        init_req = {
            "jsonrpc": "2.0", 
            "method": "initialize", 
            "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "manual-client", "version": "1.0"}}, 
            "id": 1
        }
        send_json(process, init_req)
        read_json(process) # Ack
        
        notify_init = {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}
        send_json(process, notify_init)
        console.print("[green]✓ Server Connected & Initialized[/green]\n")

        req_id = 2
        
        while True:
            try:
                console.print("\n[bold purple]Select Tool:[/bold purple]")
                console.print("1. get_cve")
                console.print("2. search_mitre_techniques")
                console.print("3. get_mitre_technique")
                
                choice = console.input("[bold purple]V2 Client > [/bold purple]")
                
                if choice.lower() in ["exit", "q", "quit"]:
                    break
                    
                method = "tools/call"
                params = {}
                
                if choice == "1":
                    cve = console.input("Enter CVE ID (e.g. CVE-2021-44228): ")
                    params = {"name": "get_cve", "arguments": {"cve_id": cve}}
                elif choice == "2":
                    q = console.input("Enter search query (e.g. phishing): ")
                    params = {"name": "search_mitre_techniques", "arguments": {"query": q}}
                elif choice == "3":
                    mid = console.input("Enter MITRE ID (e.g. T1566): ")
                    params = {"name": "get_mitre_technique", "arguments": {"mitre_id": mid}}
                else:
                    console.print("[yellow]Invalid selection[/yellow]")
                    continue

                # Construct Request
                req = {
                    "jsonrpc": "2.0",
                    "method": method,
                    "params": params,
                    "id": req_id
                }
                req_id += 1
                
                send_json(process, req)
                
                with console.status("Waiting for server...", spinner="dots"):
                    resp = read_json(process)
                
                if resp and "result" in resp:
                    # FastMCP returns text content in a nested structure
                    content = resp["result"]["content"][0]["text"]
                    try:
                        # Try to parse inner JSON if applicable
                        data = json.loads(content)
                        console.print(Panel(json.dumps(data, indent=2), title="Tool Output", border_style="green"))
                    except:
                        console.print(Panel(content, title="Tool Output", border_style="green"))
                elif resp and "error" in resp:
                    console.print(f"[red]Server Error: {resp['error']['message']}[/red]")
                else:
                    console.print(f"[red]Unknown Response: {resp}[/red]")

            except KeyboardInterrupt:
                break
                
    finally:
        process.terminate()
        console.print("\n[yellow]Server Disconnected.[/yellow]")

if __name__ == "__main__":
    main()
