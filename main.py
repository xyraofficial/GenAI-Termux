import os
import sys
import time
import requests
import json
import subprocess
import re
import datetime
import locale

# --- AUTO INSTALL DEPS ---
try:
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
    # Library Google Search Ringan
    from googlesearch import search as gsearch
except ImportError:
    print("Installing dependencies (googlesearch-python)...")
    os.system("pip install rich requests googlesearch-python")
    print("Dependencies installed. Please restart script.")
    sys.exit()

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

# --- ENGINE: TIME & SEARCH ---

def get_realtime_info():
    """Mengambil data Waktu & Tanggal dari System HP"""
    now = datetime.datetime.now()
    # Format: Senin, 12 Januari 2026 - 14:30:00
    days = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
    day_name = days[now.weekday()]
    time_str = now.strftime("%d %B %Y - %H:%M:%S")
    return f"Waktu Sistem Saat Ini: {day_name}, {time_str} (WIB/WITA/WIT)"

def google_search_tool(query):
    """Mencari di Google menggunakan library googlesearch-python"""
    console.print(Rule(style="dim blue"))
    console.print(f"[bold blue]🌍 GOOGLING:[/bold blue] [dim]{query}[/dim]")
    
    try:
        results = []
        # Mengambil 3 hasil teratas, advanced=True untuk dapat judul & deskripsi
        for res in gsearch(query, num_results=3, advanced=True):
            results.append(f"TITLE: {res.title}\nDESC: {res.description}\nLINK: {res.url}")
            
        if not results:
            return "Google Search selesai, tapi tidak ada hasil yang relevan."
            
        return "HASIL PENCARIAN GOOGLE TERBARU:\n\n" + "\n\n".join(results)

    except Exception as e:
        return f"Gagal akses Google: {str(e)}. Coba cek koneksi internet."

# --- ENGINE: FILE INSPECTOR ---

def scan_for_interactivity(command):
    parts = command.split()
    filename = None
    if len(parts) >= 2 and parts[0] in ["python", "python3", "bash", "sh", "node"]:
        filename = parts[1]

    if filename and os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            danger_patterns = ["input(", "raw_input(", "read ", "read -p", "Prompt.ask", "Confirm.ask"]
            for pattern in danger_patterns:
                if pattern in content:
                    return True, filename, pattern
        except: pass
    return False, None, None

# --- ENGINE: FILE MAKER ---

def create_file_animated(filename, content):
    console.print()
    try:
        with Progress(
            SpinnerColumn(style="bold yellow"),
            TextColumn("[bold cyan]{task.description}"),
            BarColumn(bar_width=30, style="dim white", complete_style="green"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            task = progress.add_task(f"Allocating {filename}...", total=100)
            time.sleep(0.3)
            progress.update(task, advance=50, description=f"Writing...")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            time.sleep(0.2)
            progress.update(task, advance=50, description=f"Done!")

        abs_path = os.path.abspath(filename)
        size_bytes = len(content.encode('utf-8'))
        size_str = f"{size_bytes/1024:.2f} KB" if size_bytes > 1024 else f"{size_bytes} Bytes"

        grid = Table.grid(expand=True)
        grid.add_column(style="bold cyan", width=12)
        grid.add_column(style="white")
        grid.add_row("📄 NAME", f": [bold white]{filename}[/bold white]")
        grid.add_row("💾 SIZE", f": [green]{size_str}[/green]")
        grid.add_row("📍 LOCATION", f": [dim]{abs_path}[/dim]")

        console.print(Panel(grid, title="[bold white]✅ FILE CREATED[/bold white]", border_style="green", box=box.ROUNDED))
        return f"File '{filename}' created at {abs_path}."
    except Exception as e:
        return f"Error: {e}"

# --- ENGINE: TERMINAL ---

def run_terminal_live(command):
    # Cek apakah command mencoba menjalankan script (python, node, bash, dll)
    script_executors = ["python", "python3", "node", "bash", "sh", "zsh", "php", "perl", "ruby"]
    is_script = any(command.startswith(executor + " ") for executor in script_executors) or command.endswith(".sh") or command.endswith(".py") or command.endswith(".js")

    if is_script:
        msg = f"\n[bold red]⚠ KEBIJAKAN KEAMANAN:[/bold red]\n"
        msg += f"Saya tidak diizinkan untuk menjalankan script secara otomatis.\n\n"
        msg += f"[bold yellow]Cara menjalankan manual:[/bold yellow]\n"
        msg += f"1. Buka session baru di Termux (Swipe kiri > New Session).\n"
        msg += f"2. Ketik perintah berikut:\n"
        msg += f"   [bold cyan]{command}[/bold cyan]\n"
        return f"###MANUAL_RUN_REQUIRED###\n{msg}"

    if command.startswith("source") or command.startswith("cd ") or command.startswith(". "):
        return f"[SYSTEM]: Perintah '{command}' harus dijalankan manual di terminal."

    is_interactive, fname, trigger = scan_for_interactivity(command)
    if is_interactive:
        return f"###INTERACTIVE_STOP### File '{fname}' terdeteksi memiliki input ('{trigger}'). Silakan jalankan secara manual di session baru."

    console.print(Rule(style="dim cyan"))
    console.print(f"[bold yellow]⚡ EXEC:[/bold yellow] [on black] {command} [/on black]")
    
    # Hanya izinkan perintah dasar yang benar-benar aman
    safe_cmds = ["ls", "echo", "whoami", "pwd", "date", "neofetch", "clear", "cat", "grep", "git", "python", "node", "rm", "mkdir", "touch", "pkg", "apt"]
    is_safe = any(command.startswith(cmd) for cmd in safe_cmds)
    
    if not is_safe:
        if not Confirm.ask(f"[bold red]Allow execution?[/bold red]"):
            return "User denied permission."

    full_output = []
    current_loc = os.getcwd().replace("/data/data/com.termux/files/home", "~")
    
    try:
        executable = "/data/data/com.termux/files/usr/bin/bash"
        if not os.path.exists(executable): executable = None 

        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, executable=executable)

        with Live(refresh_per_second=12, auto_refresh=True) as live:
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None: break
                if line:
                    full_output.append(line.strip())
                    log_text = "\n".join(full_output[-20:])
                    panel = Panel(Text(log_text, style="green"), title=f"[bold white]CONSOLE[/bold white] [dim]({current_loc})[/dim]", subtitle="[blink yellow]RUNNING[/blink yellow]", border_style="green", box=box.ROUNDED)
                    live.update(panel)

        stderr = process.stderr.read()
        if stderr: full_output.append(f"STDERR: {stderr}")
        return "\n".join(full_output) if full_output else "[Success]"

    except Exception as e:
        return f"Error: {str(e)}"

# --- ENGINE: CHOICE ---
def ask_choice(question, choices):
    console.print()
    console.print(f"[bold magenta]❓ AI ASKS:[/bold magenta] {question}")
    for i, choice in enumerate(choices, 1):
        console.print(f"  [bold cyan]{i}.[/bold cyan] {choice}")
    while True:
        try:
            selection = Prompt.ask(f"\n[bold white]Select Option (1-{len(choices)})[/bold white]", default="1")
            idx = int(selection) - 1
            if 0 <= idx < len(choices): return f"User selected: '{choices[idx]}'."
        except: console.print("[red]Invalid selection.[/red]")

# --- UTILS & PROMPT ---

def get_system_prompt():
    return """
You are NEXUS V19, created by **Kz.tutorial & XyraOfficial**.

TOOLS & RULES:
1. **Time/Date**: Jika user tanya waktu, gunakan `get_time_info`.
2. **Internet Search**: Jika user tanya berita atau fakta, gunakan `google_search`.
3. **Identity**: Jawaban pencipta: "Kz.tutorial & XyraOfficial".
4. **Security**: Anda DILARANG menjalankan script (Python, Bash, JS, dll) secara langsung. 
   Jika Anda perlu menjalankan perintah yang diblokir oleh tool `run_terminal`, jelaskan kepada user bahwa mereka harus menjalankannya secara MANUAL di session Termux baru. Berikan perintahnya dengan jelas di bagian `copy_text`.
5. **Format Response**: Harus JSON sesuai schema.

RESPONSE FORMAT (JSON ONLY):
{ "action": "reply", "content": "Penjelasan Anda di sini.", "copy_text": "Perintah untuk dijalankan manual jika ada" }
Atau untuk tool:
{ "action": "tool", "tool_name": "...", "args": "..." }
"""

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f: state["api_key"] = json.load(f).get("api_key", "")
        except: pass

def save_config():
    with open(CONFIG_FILE, 'w') as f: json.dump({"api_key": state["api_key"]}, f)

def setup():
    console.clear()
    if not state["api_key"]:
        console.print(Panel("NEXUS SETUP", style="bold white on blue"))
        state["api_key"] = Prompt.ask("Paste API Key")
        save_config()

def clean_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```json\s*", "", text)
        text = re.sub(r"^```\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text

def print_manual_copy(text):
    if text and text.strip():
        console.print()
        console.print(Panel(f"{text}", title="⚠ RUN MANUALLY", border_style="yellow", box=box.DOUBLE))

def query_ai(user_input, tool_output=None):
    headers = {"Authorization": f"Bearer {state['api_key']}", "Content-Type": "application/json"}
    messages = [{"role": "system", "content": get_system_prompt()}]
    messages.extend(state["history"][-8:])
    
    if tool_output:
        messages.append({"role": "user", "content": f"Tool Output:\n{tool_output}\n\nProceed."})
    else:
        messages.append({"role": "user", "content": user_input})

    payload = {"model": CURRENT_MODEL, "messages": messages, "temperature": 0.3, "response_format": {"type": "json_object"}}

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        if response.status_code != 200: return {"action": "reply", "content": f"API Error: {response.text}"}
        raw = response.json()['choices'][0]['message']['content']
        return json.loads(clean_json(raw))
    except Exception as e:
        return {"action": "reply", "content": f"Error: {e}"}

# --- MAIN LOOP ---
def main():
    load_config()
    setup()
    
    grid = Table.grid(expand=True)
    grid.add_column(justify="left"); grid.add_column(justify="right")
    grid.add_row("[bold cyan]NEXUS AGENT v19[/bold cyan]", "[dim]Google Edition[/dim]")
    console.print(Panel(grid, style="cyan", box=box.ROUNDED))
    
    while True:
        console.print()
        console.print(f"[bold cyan]USER ❯[/bold cyan]", end=" ")
        user_input = input()
        
        if user_input.lower() in ["exit", "quit"]: break
        if not user_input.strip(): continue
        
        state["history"].append({"role": "user", "content": user_input})

        with console.status("[bold yellow]Thinking...[/bold yellow]", spinner="aesthetic"):
            response = query_ai(user_input)
        
        # HANDLE TOOLS
        if response.get("action") == "tool":
            tool = response.get("tool_name")
            output = ""
            
            if tool == "run_terminal": output = run_terminal_live(response.get("args"))
            elif tool == "create_file": output = create_file_animated(response.get("filename"), response.get("content"))
            elif tool == "ask_choice": output = ask_choice(response.get("question"), response.get("choices"))
            elif tool == "google_search": output = google_search_tool(response.get("args")) 
            elif tool == "get_time_info": output = get_realtime_info() # NEW TOOL

            state["history"].append({"role": "assistant", "content": json.dumps(response)})
            
            with console.status("[bold green]Processing...[/bold green]", spinner="dots"):
                final = query_ai(user_input, tool_output=output)
            
            # NESTED TOOL
            if final.get("action") == "tool":
                tool_2 = final.get("tool_name")
                if tool_2 == "run_terminal": output_2 = run_terminal_live(final.get("args"))
                elif tool_2 == "create_file": create_file_animated(final.get("filename"), final.get("content"))
                state["history"].append({"role": "assistant", "content": json.dumps(final)})
            
            elif "content" in final:
                console.print(Panel(Markdown(final["content"]), title="NEXUS", border_style="cyan"))
                if "copy_text" in final: print_manual_copy(final["copy_text"])
                state["history"].append({"role": "assistant", "content": json.dumps(final)})
            
        else:
            if "content" in response:
                console.print(Panel(Markdown(response["content"]), title="NEXUS", border_style="cyan"))
            if "copy_text" in response: print_manual_copy(response["copy_text"])
            state["history"].append({"role": "assistant", "content": json.dumps(response)})

if __name__ == "__main__":
    main()
