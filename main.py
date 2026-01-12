import os
import sys
import time
import requests
import json
import subprocess
import re
import datetime
import shutil
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.live import Live
from rich.text import Text
from rich import box
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.syntax import Syntax
from rich.rule import Rule
from rich.align import Align
from googlesearch import search as gsearch

# --- KONFIGURASI ---
CONFIG_FILE = "nexus_config.json"
API_URL = "https://api.groq.com/openai/v1/chat/completions"
CURRENT_MODEL = "llama-3.3-70b-versatile" 

console = Console()

# --- STATE ---
state = {
    "api_key": "",
    "history": [],
    "theme": "cyan"
}

# --- UI UTILS ---
def get_terminal_size():
    size = shutil.get_terminal_size()
    return size.columns, size.lines

def banner():
    cols, _ = get_terminal_size()
    banner_text = Text()
    banner_text.append(" ███▄    █ ▓█████ ▒██   ██▒ █    ██   ██████ \n", style="bold cyan")
    banner_text.append(" ██ ▀█   █ ▓█   ▀ ▒▒ █ █ ▒░ ██  ▓██▒▒██    ▒ \n", style="bold cyan")
    banner_text.append("▓██  ▀█ ██▒▒███    ░  █   ░▓██  ▒██░░ ▓██▄   \n", style="bold cyan")
    banner_text.append("▓██▒  ▐▌██▒▒▓█  ▄   ░ █ █ ▒▓▓█  ░██░  ▒   ██▒\n", style="bold cyan")
    banner_text.append("▒██░   ▓██░░▒████▒▒██▒ ▒██▒▒▒█████▓ ▒██████▒▒\n", style="bold cyan")
    banner_text.append("░ ▒░   ▒ ▒ ░░ ▒░ ░▒▒ ░ ░▓ ░░▒▓▒ ▒ ▒ ▒ ▒▓▒ ▒ ░\n", style="dim cyan")
    
    info_table = Table.grid(padding=1)
    info_table.add_column(style="bold white")
    info_table.add_column(style="cyan")
    info_table.add_row("Version", "v19.0.1")
    info_table.add_row("Author", "Kz.tutorial & XyraOfficial")
    info_table.add_row("Platform", "Termux Optimized")

    panel = Panel(
        Align.center(banner_text + "\n" + Text.from_markup("[dim]Advanced Generative AI Agent[/dim]")),
        subtitle="[bold white]Welcome to the Future[/bold white]",
        subtitle_align="right",
        box=box.DOUBLE_EDGE,
        border_style="bright_blue",
        padding=(1, 2)
    )
    console.print(panel)
    console.print(Align.center(info_table))
    console.print(Rule(style="dim blue"))

# --- ENGINE: TIME & SEARCH ---
def get_realtime_info():
    now = datetime.datetime.now()
    days = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
    day_name = days[now.weekday()]
    time_str = now.strftime("%d %B %Y - %H:%M:%S")
    return f"Waktu Sistem Saat Ini: {day_name}, {time_str} (WIB/WITA/WIT)"

def google_search_tool(query):
    console.print(Rule(title="[bold blue]Searching Google[/bold blue]", style="dim blue"))
    try:
        results = []
        for res in gsearch(query, num_results=3, advanced=True):
            results.append(f"TITLE: {res.title}\nDESC: {res.description}\nLINK: {res.url}")
        if not results: return "Tidak ada hasil relevan."
        return "HASIL PENCARIAN GOOGLE:\n\n" + "\n\n".join(results)
    except Exception as e:
        return f"Gagal akses Google: {str(e)}"

# --- ENGINE: FILE MAKER ---
def create_file_animated(filename, content):
    cols, _ = get_terminal_size()
    width = min(cols - 10, 50)
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=width),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console
    ) as progress:
        task = progress.add_task(f"[cyan]Creating {filename}...", total=100)
        time.sleep(0.5)
        progress.update(task, advance=40, description="[yellow]Writing content...")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        time.sleep(0.5)
        progress.update(task, advance=60, description="[green]Success!")
    
    console.print(Panel(f"File [bold green]{filename}[/bold green] saved successfully.", border_style="green", box=box.ROUNDED))
    return f"File '{filename}' created."

# --- ENGINE: TERMINAL ---
def run_terminal_live(command):
    console.print(f"\n[bold yellow]❱[/bold yellow] [dim]Executing:[/dim] [italic cyan]{command}[/italic cyan]")
    full_output = []
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
        with Live(refresh_per_second=10) as live:
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None: break
                if line:
                    full_output.append(line.strip())
                    live.update(Panel(Text("\n".join(full_output[-10:]), style="dim green"), title="Terminal Output", border_style="blue"))
        
        stderr = process.stderr.read()
        if stderr: full_output.append(f"ERROR: {stderr}")
        return "\n".join(full_output) if full_output else "Success"
    except Exception as e:
        return f"Error: {e}"

# --- CORE LOGIC ---
def get_system_prompt():
    return """You are NEXUS V19 by Kz.tutorial & XyraOfficial. Always reply in JSON format.
Actions: tool (run_terminal, create_file, google_search, get_time_info), reply (content, copy_text)."""

def query_ai(user_input, tool_output=None):
    headers = {"Authorization": f"Bearer {state['api_key']}", "Content-Type": "application/json"}
    messages = [{"role": "system", "content": get_system_prompt()}]
    messages.extend(state["history"][-6:])
    
    if tool_output:
        messages.append({"role": "user", "content": f"RESULT:\n{tool_output}\nContinue."})
    else:
        messages.append({"role": "user", "content": user_input})

    try:
        response = requests.post(API_URL, headers=headers, json={"model": CURRENT_MODEL, "messages": messages, "response_format": {"type": "json_object"}}, timeout=30)
        return json.loads(response.json()['choices'][0]['message']['content'])
    except Exception as e:
        return {"action": "reply", "content": f"AI Error: {e}"}

def main():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f: state["api_key"] = json.load(f).get("api_key", "")
    
    console.clear()
    if not state["api_key"]:
        console.print(Panel("NEXUS INITIALIZATION", style="bold white on blue"))
        state["api_key"] = Prompt.ask("[bold cyan]Enter Groq API Key[/bold cyan]")
        with open(CONFIG_FILE, 'w') as f: json.dump({"api_key": state["api_key"]}, f)
    
    console.clear()
    banner()

    while True:
        try:
            user_input = Prompt.ask(f"\n[bold cyan]NEXUS[/bold cyan] [bold white]❯[/bold white]")
            if user_input.lower() in ["exit", "quit", "clear"]:
                if user_input.lower() == "clear":
                    console.clear()
                    banner()
                    continue
                break
            
            state["history"].append({"role": "user", "content": user_input})
            
            with console.status("[bold blue]Processing...", spinner="bouncingBar"):
                response = query_ai(user_input)
            
            if response.get("action") == "tool":
                tool = response.get("tool_name")
                args = response.get("args", "")
                
                output = ""
                if tool == "run_terminal": output = run_terminal_live(args)
                elif tool == "create_file": output = create_file_animated(response.get("filename"), response.get("content"))
                elif tool == "google_search": output = google_search_tool(args)
                elif tool == "get_time_info": output = get_realtime_info()
                
                with console.status("[bold green]Finalizing...", spinner="point"):
                    final = query_ai(user_input, tool_output=output)
                
                if "content" in final:
                    console.print(Panel(Markdown(final["content"]), title="[bold cyan]NEXUS RESPONSE[/bold cyan]", border_style="bright_blue", padding=(1, 2)))
                state["history"].append({"role": "assistant", "content": json.dumps(final)})
            else:
                console.print(Panel(Markdown(response.get("content", "")), title="[bold cyan]NEXUS RESPONSE[/bold cyan]", border_style="bright_blue", padding=(1, 2)))
                state["history"].append({"role": "assistant", "content": json.dumps(response)})

        except KeyboardInterrupt:
            console.print("\n[bold red]Interrupted by user. Exiting...[/bold red]")
            break

if __name__ == "__main__":
    main()
