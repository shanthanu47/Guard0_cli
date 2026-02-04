from rich.console import Console
from rich.panel import Panel
from src.agent import agent
import sys

# Minimal V1 Runner to demonstrate the old "Monolithic" architecture
# This strictly uses the src.agent module which was V1's core.

console = Console()

def main():
    console.print(Panel("🛡️  Version 1: Monolithic Agent (Legacy)  🛡️", style="bold red"))
    
    query = "What is CVE-2021-44228?"
    print(f"\nUser Query: {query}\n")
    
    print("--- Agent Execution Trace ---")
    try:
        generator = agent.chat(query)
        for event_type, content in generator:
            if event_type == "final":
                print(f"\n[FINAL ANSWER]\n{content}")
            elif event_type in ["log", "debug"]:
                print(f"[{event_type.upper()}] {content}")
            elif event_type == "error":
                print(f"[ERROR] {content}")
                
    except Exception as e:
        print(f"Error running V1: {e}")

if __name__ == "__main__":
    main()
