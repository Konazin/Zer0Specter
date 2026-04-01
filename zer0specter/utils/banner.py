import os
import sys
import time

try:
    from rich.console import Console
    from rich.text import Text
    from rich.progress import Progress, BarColumn, TimeElapsedColumn
    from rich.panel import Panel
    from rich.align import Align
    from rich import print as rprint
    _RICH = True
except ImportError:
    _RICH = False

from .. import __version__, __author__

console = Console() if _RICH else None

# ── ASCII art ────────────────────────────────────────────────────────────────

LOGO = r"""
 ____           ___  ___                  _            
|_  / ___  _ _ |   |/ __> ___  ___  ___ _| |_ ___  _ _ 
 / / / ._>| '_>| / |\__ \| . \/ ._>/ | ' | | / ._>| '_>
/___|\___.|_|  `___'<___/|  _/\___.\_|_. |_| \___.|_|  
                         |_|                           
"""

TAGLINE = "penetration toolkit  ·  for authorized use only"

MODULES_LIST = [
    ("zipcrack",  "Crack password-protected ZIP files"),
    ("passgen",  "Generate random secure passwords"),
    ("wifiattack",  "Perform Wi-Fi deauthentication (DoS) attacks"),
    ("iplocator",  "Geolocate an IP address"),
    ("sniffer",  "Capture and display network packets"),
    ("portscanner" , "Check open ports by bruteforce")
]

# ── Helpers de exibição ───────────────────────────────────────────────────────

def _slow_print(text: str, delay: float = 0.012) -> None:
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)

def _clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")

# ── Banner principal (rich) ───────────────────────────────────────────────────

def _print_banner_rich() -> None:
    _clear()

    # Logo em gradiente vermelho → branco
    logo_text = Text(LOGO)
    logo_text.stylize("bold red")

    console.print(Align.center(logo_text))
    console.print(Align.center(
        Text(f"  {TAGLINE}", style="dim red")
    ))
    console.print(Align.center(
        Text(f"  v{__version__}  ·  by {__author__}\n", style="dim")
    ))

def _print_banner_plain() -> None:
    _clear()
    print(LOGO)
    print(f"  {TAGLINE}")
    print(f"  v{__version__}  ·  by {__author__}\n")

# ── Barra de loading (rich) ───────────────────────────────────────────────────

def _loading_rich() -> None:
    steps = [
        ("Initializing core engine",    0.4),
        ("Loading modules",             0.5),
        ("Checking dependencies",       0.4),
        ("Configuring interfaces",      0.3),
        ("Ready",                       0.1),
    ]

    with Progress(
        "[progress.description]{task.description}",
        BarColumn(bar_width=36, style="red", complete_style="bright_red"),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeElapsedColumn(),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("[red]Booting Zer0Specter...", total=len(steps))
        for label, duration in steps:
            progress.update(task, description=f"[dim]{label}[/dim]")
            time.sleep(duration)
            progress.advance(task)

    console.print("[bold red]  [ OK ][/bold red] [dim]All systems operational.[/dim]\n")

def _loading_plain() -> None:
    phases = [
        "Initializing core engine...",
        "Loading modules...",
        "Checking dependencies...",
        "Configuring interfaces...",
        "Ready.",
    ]
    for phase in phases:
        _slow_print(f"  {phase}\n", delay=0.01)
        time.sleep(0.3)
    print()

# ── Menu de ajuda inline (exibido após o boot) ────────────────────────────────

def _print_module_table_rich() -> None:
    from rich.table import Table

    table = Table(
        show_header=True,
        header_style="bold red",
        border_style="dim",
        box=None,
        padding=(0, 2),
    )
    table.add_column("COMANDO",   style="red",  no_wrap=True)
    table.add_column("DESCRIÇÃO", style="white")

    for cmd, desc in MODULES_LIST:
        table.add_row(cmd, desc)

    table.add_row("", "")
    table.add_row("help",        "Help - show this message")
    table.add_row("clear",       "Clean terminal")
    table.add_row("quit / exit", "End program")

    console.print(
        Panel(
            Align.left(table),
            title="[bold red]módulos disponíveis[/bold red]",
            border_style="red",
            padding=(1, 3),
        )
    )
    console.print()

def _print_module_table_plain() -> None:
    print("Módulos disponíveis:")
    print("-" * 44)
    for cmd, desc in MODULES_LIST:
        print(f"  {cmd:<16} {desc}")
    print(f"  {'help':<16} lista todos os comandos")
    print(f"  {'clear':<16} limpa o terminal")
    print(f"  {'gui':<16} abre a interface gráfica")
    print(f"  {'quit / exit':<16} encerra o programa")
    print()

# ── Ponto de entrada público ──────────────────────────────────────────────────

def show_banner(with_loading: bool = True, show_modules: bool = True) -> None:
    if _RICH:
        _print_banner_rich()
        if with_loading:
            _loading_rich()
        if show_modules:
            _print_module_table_rich()
    else:
        _print_banner_plain()
        if with_loading:
            _loading_plain()
        if show_modules:
            _print_module_table_plain()