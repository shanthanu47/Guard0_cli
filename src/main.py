import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.spinner import Spinner
from typing import Optional
import sys

# Import core modules
from src.agent import agent
from src.build_db import build_database, download_data

app = typer.Typer()
console = Console()

@app.command()
def init():
    """
    Initializes the MITRE ATT&CK database.
    """
    console.print(Panel("Initializing Vulnerability Bot Data...", style="bold magenta"))
    try:
        download_data()
        build_database()
        console.print("[green]Initialization Complete![/green]")
    except Exception as e:
        console.print(f"[red]Error during initialization: {str(e)}[/red]")

@app.command()
def start():
    """
    Start the interactive chat session.
    """
    console.print(Panel.fit("🛡️  Vulnerability Intelligence CLI  🛡️", style="bold cyan"))
    console.print("[dim]Type 'exit' or 'quit' to end the session.[/dim]")
    
    while True:
        try:
            user_input = console.input("\n[bold green]You > [/bold green]")
            if user_input.lower() in ["exit", "quit", "q"]:
                console.print("[yellow]Goodbye![/yellow]")
                break
                
            if not user_input.strip():
                continue

            # Chat Loop
            with console.status("[bold cyan]Agent is thinking...[/bold cyan]", spinner="dots") as status:
                final_answer = None
                
                # The agent returns a generator of updates
                # We iterate through them to update the UI
                generator = agent.chat(user_input)
                
                try:
                    for event_type, content in generator:
                        if event_type == "log":
                            status.update(f"[cyan]{content}[/cyan]")
                            console.print(f"[dim]{content}[/dim]")
                        
                        elif event_type == "debug":
                            # Debug logs shown in lighter text
                            console.print(f"[dim yellow]DEBUG: {content}[/dim yellow]")

                        elif event_type == "final":
                            final_answer = content
                            
                        elif event_type == "error":
                            console.print(f"[bold red]Error: {content}[/bold red]")
                            
                except Exception as e:
                    import traceback
                    console.print(f"[bold red]Unexpected Error: {str(e)}[/bold red]")
                    console.print(f"[dim]{traceback.format_exc()}[/dim]")
                    continue

            # Print Final Answer outside the spinner
            if final_answer:
                console.print("\n[bold blue]Agent:[/bold blue]")
                console.print(Markdown(final_answer))
            else:
                 console.print("[dim](No final answer generated)[/dim]")

        except KeyboardInterrupt:
            console.print("\n[yellow]Session interrupted. Exiting...[/yellow]")
            break

if __name__ == "__main__":
    app()
