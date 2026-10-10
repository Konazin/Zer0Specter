"""Full-screen terminal interface for the direct ZeroSpecter CLI."""

import asyncio
import sys
from typing import Callable, Dict, List, Optional

from rich.text import Text
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Checkbox, Footer, Header, Input, Label, ListItem
from textual.widgets import ListView, RichLog, Static

CATEGORIES = {
    "Recon": ("port-scanner", "packet-sniffer", "ip-geolocation"),
    "Web": ("zap", "sqlmap"),
    "Ofensiva": ("wifi-deauth", "zip-cracker", "sqlmap"),
    "Utilitários": ("password-generator",),
}

TOOL_CATALOG = {
    "port-scanner": {
        "label": "Port scanner",
        "enabled": True,
        "command": "port-scanner",
        "description": "Scan TCP ports on a host.",
        "fields": (
            ("target", "Alvo", "text", "-t", "", True),
            ("start", "Porta inicial", "text", "-s", "1", True),
            ("end", "Porta final", "text", "-e", "2048", True),
            ("delay", "Timeout", "text", "-d", "0.2", True),
            ("banner", "Consultar banner", "flag", "--banner", False, False),
        ),
    },
    "packet-sniffer": {
        "label": "Sniffer",
        "enabled": True,
        "command": "packet-sniffer",
        "description": "Capture packets on a selected interface.",
        "fields": (
            ("interface", "Interface", "text", "-i", "", False),
            (
                "show_interfaces",
                "Listar interfaces",
                "flag",
                "--showinterfaces",
                False,
                False,
            ),
        ),
    },
    "ip-geolocation": {
        "label": "IP geolocation",
        "enabled": True,
        "command": "ip-geolocation",
        "description": "Look up an IP address; leave blank to look up this connection.",
        "fields": (("ip", "IP (opcional)", "text", "-ip", "", False),),
    },
    "wifi-deauth": {
        "label": "Wi-Fi deauth",
        "enabled": True,
        "command": "wifi-deauth",
        "description": "Send deauthentication frames on an authorized lab network.",
        "fields": (
            ("interface", "Interface", "text", "-i", "", True),
            ("ap", "MAC do AP", "text", "-a", "", True),
            ("client", "MAC do cliente", "text", "-c", "", True),
            ("count", "Quantidade (0 = contínuo)", "text", "-n", "10", True),
            ("interval", "Intervalo", "text", "--interval", "0.1", True),
        ),
    },
    "zip-cracker": {
        "label": "ZIP cracker",
        "enabled": True,
        "command": "zip-cracker",
        "description": "Test a wordlist or a bounded character set against a ZIP file.",
        "fields": (
            ("path", "Arquivo ZIP", "text", "-p", "", True),
            ("wordlist", "Wordlist (opcional)", "text", "-w", "", False),
            ("size", "Tamanho (modo charset)", "text", "-s", "", False),
            ("letters", "Letras", "choice", "-l", False, False),
            ("numbers", "Números", "choice", "-n", False, False),
            ("special", "Caracteres especiais", "choice", "-sc", False, False),
            (
                "output_dir",
                "Pasta de saída (opcional)",
                "text",
                "--output-dir",
                "",
                False,
            ),
        ),
    },
    "password-generator": {
        "label": "Gerador de senhas",
        "enabled": True,
        "command": "password-generator",
        "description": "Generate a password with the selected character sets.",
        "fields": (
            ("prefix", "Prefixo (opcional)", "text", "--prefix", "", False),
            ("length", "Tamanho", "text", "--numberchar", "12", True),
            ("punctuation", "Pontuação", "choice", "--punctuation", False, False),
            ("numbers", "Números", "choice", "--numbers", False, False),
            ("uppercase", "Maiúsculas", "choice", "--uppercase", False, False),
        ),
    },
    "zap": {
        "label": "OWASP ZAP · planejado para M3",
        "enabled": False,
        "command": "zap",
        "description": "ZAP will be available after its M3 integration is implemented.",
        "fields": (),
    },
    "sqlmap": {
        "label": "sqlmap · planejado para M3",
        "enabled": False,
        "command": "sqlmap",
        "description": "sqlmap will be available after its M3 integration is implemented.",
        "fields": (),
    },
}

CLI_RUNNER = "from zer0specter.cli import main; raise SystemExit(main())"


def build_command(tool_id: str, values: Dict[str, object]) -> List[str]:
    """Build the existing CLI command from one tool form."""
    tool = TOOL_CATALOG.get(tool_id)
    if tool is None:
        raise ValueError("Unknown tool")
    if not tool["enabled"]:
        raise ValueError("This tool is planned for M3 and is not available yet")
    if (
        tool_id == "packet-sniffer"
        and not values.get("show_interfaces")
        and not values.get("interface")
    ):
        raise ValueError("Required field is empty: interface")

    command = [str(tool["command"])]
    for name, _label, kind, flag, _default, required in tool["fields"]:
        value = values.get(name)
        if kind == "flag":
            if value:
                command.append(flag)
            continue
        if kind == "choice":
            if value:
                command.extend((flag, "y"))
            continue
        if value is None or value == "":
            if required:
                raise ValueError("Required field is empty: %s" % name)
            continue
        command.extend((flag, str(value)))
    return command


def build_cli_argv(
    command: List[str], python_executable: Optional[str] = None
) -> List[str]:
    """Build a shell-free invocation of the installed CLI entry point."""
    return [python_executable or sys.executable, "-c", CLI_RUNNER, *command]


async def run_cli_process(
    argv: List[str],
    on_output: Callable[[str, str], None],
    on_process: Optional[Callable[[asyncio.subprocess.Process], None]] = None,
) -> int:
    """Run the CLI without a shell and forward both output streams line by line."""
    process = await asyncio.create_subprocess_exec(
        *argv,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    if on_process is not None:
        on_process(process)

    async def forward(stream_name: str, stream) -> None:
        while True:
            line = await stream.readline()
            if not line:
                return
            on_output(
                stream_name, line.decode("utf-8", errors="replace").rstrip("\r\n")
            )

    try:
        await asyncio.gather(
            forward("stdout", process.stdout),
            forward("stderr", process.stderr),
        )
        return await process.wait()
    except asyncio.CancelledError:
        if process.returncode is None:
            try:
                process.terminate()
            except ProcessLookupError:
                pass
            try:
                await asyncio.wait_for(process.wait(), timeout=2)
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
        raise


class ZeroSpecterTUI(App[None]):
    """Responsive tool browser and form runner for the current CLI modules."""

    TITLE = "ZeroSpecter"
    CSS = """
    Screen { background: #161616; color: #eeeeee; }
    Header { background: #202020; color: #eeeeee; }
    Footer { background: #202020; }
    #workspace { height: 1fr; layout: horizontal; }
    #sidebar { width: 27; border-right: solid #cc2200; padding: 1; }
    #main { width: 1fr; padding: 1 2; }
    #category-list { height: 1fr; }
    #tool-list, #tool-detail { height: 1fr; }
    #tool-detail { display: none; }
    #tool-search { margin-bottom: 1; }
    .tool-choice { width: 1fr; margin-bottom: 1; }
    .planned-tool { color: #888888; padding: 1; }
    .field-label { margin-top: 1; color: #bbbbbb; }
    .field-input { margin-bottom: 1; }
    .field-checkbox { margin: 1 0; }
    #tool-fields { height: auto; max-height: 1fr; }
    #action-row { height: auto; margin: 1 0; }
    #run-status { color: #bbbbbb; height: auto; }
    #run-output { height: 1fr; min-height: 5; border: round #444444; }
    #workspace.compact-layout { layout: vertical; }
    #workspace.compact-layout #sidebar {
        width: 1fr; height: 8; border-right: none; border-bottom: solid #cc2200;
    }
    #workspace.compact-layout #category-list { height: 5; }
    #workspace.compact-layout #main { width: 1fr; height: 1fr; padding: 1; }
    """
    BINDINGS = [
        ("q", "quit", "Sair"),
        ("escape", "back", "Voltar"),
        ("/", "focus_search", "Buscar"),
        ("?", "help", "Ajuda"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.selected_category = "Recon"
        self.selected_tool: Optional[str] = None
        self._process: Optional[asyncio.subprocess.Process] = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="workspace"):
            with Vertical(id="sidebar"):
                yield Label("CATEGORIAS", classes="section-heading")
                yield ListView(
                    *(ListItem(Label(category)) for category in CATEGORIES),
                    id="category-list",
                )
            with Vertical(id="main"):
                yield Label(self.selected_category, id="category-heading")
                with VerticalScroll(id="tool-list"):
                    yield Input(placeholder="Buscar ferramentas", id="tool-search")
                    with Vertical(id="tool-choices"):
                        pass
                with Vertical(id="tool-detail"):
                    yield Label("", id="tool-title")
                    yield Static("", id="tool-description")
                    with VerticalScroll(id="tool-fields"):
                        pass
                    with Horizontal(id="action-row"):
                        yield Button("Executar", id="run-tool", variant="primary")
                        yield Button("Cancelar", id="cancel-run", disabled=True)
                        yield Button("Voltar às ferramentas", id="back-to-tools")
                    yield Static("Pronto", id="run-status")
                    yield RichLog(id="run-output", wrap=True, markup=False)
        yield Footer()

    async def on_mount(self) -> None:
        self._update_layout(self.size.width, self.size.height)
        await self._render_category(self.selected_category)

    def on_resize(self, event) -> None:
        self._update_layout(event.size.width, event.size.height)

    def _update_layout(self, width: int, height: int) -> None:
        workspace = self.query_one("#workspace", Horizontal)
        workspace.set_class(width < 96 or height < 24, "compact-layout")

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.list_view.id != "category-list":
            return
        if self._process is not None and self._process.returncode is None:
            self.query_one("#run-status", Static).update(
                "Cancele ou aguarde a execução atual antes de trocar de categoria."
            )
            return
        self.selected_category = tuple(CATEGORIES)[event.index]
        self.selected_tool = None
        self.query_one("#category-heading", Label).update(self.selected_category)
        self.query_one("#tool-list").display = True
        self.query_one("#tool-detail").display = False
        await self._render_category(self.selected_category)

    async def _render_category(self, category: str) -> None:
        choices = self.query_one("#tool-choices", Vertical)
        await choices.remove_children()
        for tool_id in CATEGORIES[category]:
            tool = TOOL_CATALOG[tool_id]
            if tool["enabled"]:
                await choices.mount(
                    Button(
                        str(tool["label"]),
                        id="tool-" + tool_id,
                        classes="tool-choice",
                    )
                )
            else:
                await choices.mount(
                    Static(
                        str(tool["label"]),
                        id="tool-" + tool_id,
                        classes="planned-tool tool-choice",
                    )
                )

    async def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id != "tool-search":
            return
        query = event.value.casefold()
        for widget in self.query(".tool-choice"):
            tool_id = (widget.id or "")[len("tool-") :]
            label = str(TOOL_CATALOG[tool_id]["label"]).casefold()
            widget.display = query in label

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id or ""
        if button_id.startswith("tool-"):
            tool_id = button_id[len("tool-") :]
            await self._show_tool(tool_id)
        elif button_id == "run-tool":
            self.run_worker(self._run_selected_tool(), group="cli-run", exclusive=True)
        elif button_id == "cancel-run":
            if self._process is not None and self._process.returncode is None:
                self.query_one("#run-status", Static).update("Cancelando…")
                try:
                    self._process.terminate()
                except ProcessLookupError:
                    pass
        elif button_id == "back-to-tools":
            self.action_back()

    async def _show_tool(self, tool_id: str) -> None:
        tool = TOOL_CATALOG[tool_id]
        if not tool["enabled"]:
            return
        self.selected_tool = tool_id
        self.query_one("#tool-list").display = False
        self.query_one("#tool-detail").display = True
        self.query_one("#tool-title", Label).update(str(tool["label"]))
        self.query_one("#tool-description", Static).update(str(tool["description"]))
        fields = self.query_one("#tool-fields", VerticalScroll)
        await fields.remove_children()
        for name, label, kind, _flag, default, required in tool["fields"]:
            suffix = " *" if required else ""
            if kind == "flag":
                await fields.mount(
                    Checkbox(
                        label + suffix,
                        value=bool(default),
                        id="field-" + name,
                        classes="field-checkbox",
                    )
                )
            elif kind == "choice":
                await fields.mount(
                    Checkbox(
                        label + suffix,
                        value=bool(default),
                        id="field-" + name,
                        classes="field-checkbox",
                    )
                )
            else:
                await fields.mount(Label(label + suffix, classes="field-label"))
                await fields.mount(
                    Input(value=str(default), id="field-" + name, classes="field-input")
                )
        self.query_one("#run-output", RichLog).clear()
        self.query_one("#run-status", Static).update("Pronto")

    def _collect_values(self) -> Dict[str, object]:
        values: Dict[str, object] = {}
        for name, _label, kind, _flag, _default, _required in TOOL_CATALOG[
            self.selected_tool
        ]["fields"]:
            if kind in ("flag", "choice"):
                values[name] = self.query_one("#field-" + name, Checkbox).value
            else:
                values[name] = self.query_one("#field-" + name, Input).value
        return values

    async def _run_selected_tool(self) -> None:
        if self.selected_tool is None:
            return
        try:
            command = build_command(self.selected_tool, self._collect_values())
        except ValueError as error:
            self.query_one("#run-status", Static).update(str(error))
            return

        argv = build_cli_argv(command)
        output = self.query_one("#run-output", RichLog)
        output.clear()
        self.query_one("#run-status", Static).update("Executando…")
        self.query_one("#run-tool", Button).disabled = True
        self.query_one("#cancel-run", Button).disabled = False
        self.query_one("#category-list", ListView).disabled = True
        self.query_one("#tool-search", Input).disabled = True
        try:
            return_code = await run_cli_process(
                argv,
                lambda stream, line: output.write(
                    Text(line, style="white" if stream == "stdout" else "yellow")
                ),
                on_process=lambda process: setattr(self, "_process", process),
            )
            if return_code == 0:
                status = "Concluído (0)"
            elif return_code == 130 or return_code < 0:
                status = "Interrompido"
            else:
                status = "Falhou (%s)" % return_code
            self.query_one("#run-status", Static).update(status)
        except (OSError, ValueError) as error:
            self.query_one("#run-status", Static).update(
                "Não foi possível iniciar o CLI: %s" % error
            )
        finally:
            self._process = None
            self.query_one("#run-tool", Button).disabled = False
            self.query_one("#cancel-run", Button).disabled = True
            self.query_one("#category-list", ListView).disabled = False
            self.query_one("#tool-search", Input).disabled = False

    def action_back(self) -> None:
        if self.selected_tool is None:
            return
        if self._process is not None and self._process.returncode is None:
            self.query_one("#run-status", Static).update(
                "Cancele ou aguarde a execução atual antes de voltar."
            )
            return
        self.selected_tool = None
        self.query_one("#tool-detail").display = False
        self.query_one("#tool-list").display = True

    def action_focus_search(self) -> None:
        self.query_one("#tool-search", Input).focus()

    def action_help(self) -> None:
        self.notify("Setas/Enter navegam; Esc volta; q encerra.")


def launch() -> int:
    """Start the full-screen terminal interface."""
    ZeroSpecterTUI().run()
    return 0
