#to implement python pretty_print_events.py (this code directly seraches job.log in obj-b folder if no argument is given if argument is given it searches that file)
import sys
from collections import defaultdict
from rich.console import Console
from rich.panel import Panel
from rich.columns import Columns
from rich.theme import Theme
from pathlib import Path

# Color theme similar to dslogs view
theme = Theme({
    "arrive": "green",
    "enter": "cyan",
    "task": "yellow",
    "exit": "blue",
    "error": "bold red",
    "depart": "bright_black",
    "time": "bold white",
    "header": "bold magenta",
})
console = Console(theme=theme)

def parse_event(line):
    parts = line.strip().split()
    if len(parts) < 5:
        return None
    t, job, _, qsid = parts[:4]
    ev = " ".join(parts[4:])
    return int(t), job, qsid, ev

def colorize(ev):
    e = ev.lower()
    if "arrive" in e:  return f"[arrive]{ev}[/arrive]"
    if "enter"  in e:  return f"[enter]{ev}[/enter]"
    if "task"   in e:  return f"[task]{ev}[/task]"
    if "exit"   in e:  return f"[exit]{ev}[/exit]"
    if "error"  in e:  return f"[error]{ev}[/error]"
    if "depart" in e:  return f"[depart]{ev}[/depart]"
    return ev

def pretty_print(logfile: Path):
    events = defaultdict(list)
    queues = set()

    if not logfile.exists():
        console.print(f"[bold red]Error:[/] {logfile} not found!")
        return
    # Read and parse the log file
    with open(logfile) as f:
        for line in f:
            p = parse_event(line)
            if p:
                t, job, qsid, ev = p
                queues.add(qsid)
                events[qsid].append((t, f"T{t:<5} {job}: {colorize(ev)}"))

    if not queues:
        console.print("[yellow]No queues detected in log file.[/yellow]")
        return

    panels = []
    for q in sorted(queues):
        lines = [f"[header]{q}[/header]\n"]
        for _, txt in sorted(events[q], key=lambda x: x[0]):
            lines.append(txt)
        panels.append(
            Panel("\n".join(lines), title=q, border_style="bright_black", padding=(0,1))
        )

    console.width = max(100, len(panels) * 40)
    console.print(Columns(panels, equal=True, expand=True, align="left"))

if __name__ == "__main__":
    # Automatically look for job.log if not specified on command line
    if len(sys.argv) == 2:
        logfile = Path(sys.argv[1])
    else:
        logfile = Path(__file__).parent.parent / "obj-b" / "job.log"
        console.print(f"[cyan]No file specified. Using default:[/] {logfile}")

    pretty_print(logfile)
