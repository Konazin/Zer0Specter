"""zer0specter/gui.app

Tkinter GUI para Zer0Specter (cross-platform).
"""

from __future__ import annotations
import io
import sys
import threading
import logging
import importlib
from typing import Callable

try:
    import tkinter as tk
    from tkinter import ttk
except ImportError as e:
    raise RuntimeError("Tkinter unavailable") from e

MODULE_MAP = {
    "zipcrack":    ("zer0specter.modules.zip_cracker",  "zipcrack"),
    "passgen":     ("zer0specter.modules.passwd_gen",   "password_generator"),
    "portscanner": ("zer0specter.modules.port_scanner", "portscanner"),
    "sniffer":     ("zer0specter.modules.sniffer",      "sniffer"),
    "wifi":        ("zer0specter.modules.wifi_attack",  "wifi_attack"),
    "ipgeo":       ("zer0specter.modules.ip_geo",       "ip_locator"),
}

class TextHandler(logging.Handler):
    def __init__(self, writer: Callable[[str], None]):
        super().__init__()
        self.writer = writer

    def emit(self, record):
        try:
            self.writer(self.format(record) + "\n")
        except Exception:
            pass


def _append_text(widget: tk.Text, text: str):
    widget.configure(state="normal")
    widget.insert(tk.END, text)
    widget.see(tk.END)
    widget.configure(state="disabled")


def _run_module(func, args, log_widget: tk.Text, status_var: tk.StringVar, btn: tk.Button):
    def worker():
        old_stdout, old_stderr = sys.stdout, sys.stderr
        old_zerolog = logging.getLogger("zer0specter")
        old_handlers = list(old_zerolog.handlers)
        old_level = old_zerolog.level
        root_logger = logging.getLogger()
        root_old_handlers = list(root_logger.handlers)
        root_old_level = root_logger.level

        class ProxyIO:
            def write(self, data):
                if data:
                    log_widget.after(0, _append_text, log_widget, str(data))
            def flush(self):
                pass

        sys.stdout = ProxyIO()
        sys.stderr = ProxyIO()

        handler = TextHandler(lambda msg: log_widget.after(0, _append_text, log_widget, msg))
        handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))

        old_zerolog.handlers = []
        old_zerolog.addHandler(handler)
        old_zerolog.setLevel(logging.DEBUG)

        root_logger.addHandler(handler)
        root_logger.setLevel(logging.DEBUG)

        status_var.set("Executing...")

        try:
            func(args)
            log_widget.after(0, _append_text, log_widget, "[✓] Completed.\n")
            status_var.set("Completed")
        except SystemExit:
            status_var.set("Completed")
        except KeyboardInterrupt:
            log_widget.after(0, _append_text, log_widget, "[!] Interrupted by user.\n")
            status_var.set("Interrupted")
        except Exception as exc:
            log_widget.after(0, _append_text, log_widget, f"[✗] Error: {type(exc).__name__}: {exc}\n")
            status_var.set("Error")
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            old_zerolog.handlers = old_handlers
            old_zerolog.setLevel(old_level)
            root_logger.handlers = root_old_handlers
            root_logger.setLevel(root_old_level)
            btn.configure(state="normal")

    btn.configure(state="disabled")
    threading.Thread(target=worker, daemon=True).start()


def _load_module(name: str):
    if name not in MODULE_MAP:
        return None
    module_path, func_name = MODULE_MAP[name]
    module = importlib.import_module(module_path)
    return getattr(module, func_name)


def launch(args=None):
    root = tk.Tk()
    root.title("Zer0Specter")
    root.geometry("1024x700")
    root.configure(bg="#161616")
    root.iconphoto(False, tk.PhotoImage(width=1, height=1))  # espaço de ícone neutro

    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TButton", background="#2f2f2f", foreground="#ffffff", relief="flat")
    style.map("TButton", background=[("active", "#3a3a3a")], foreground=[("active", "#ffffff")])
    style.configure("TCheckbutton", background="#1e1e1e", foreground="#ffffff", indicatorcolor="#33ff33")
    style.map("TCheckbutton", background=[("active", "#1e1e1e")])

    sidebar = tk.Frame(root, bg="#222222", width=220, bd=0, highlightthickness=0)
    sidebar.pack(side="left", fill="y")

    content = tk.Frame(root, bg="#1e1e1e")
    content.pack(side="right", fill="both", expand=True)

    panels = []
    active_btn = None

    def set_active_button(btn):
        nonlocal active_btn
        if active_btn is not None:
            active_btn.configure(bg="#2f2f2f")
        active_btn = btn
        active_btn.configure(bg="#cc2200")

    def show_panel(index):
        for panel in panels:
            panel.pack_forget()
        panels[index].pack(fill="both", expand=True)

    def make_log_frame(parent):
        frame = tk.Frame(parent, bg="#1e1e1e")
        frame.pack(fill="both", expand=True)

        log_widget = tk.Text(
            frame,
            bg="#121212",
            fg="#33ff33",
            insertbackground="#33ff33",
            state="disabled",
            height=15
        )

        log_widget.pack(fill="both", expand=True, padx=10, pady=10)

        return log_widget
    
    def add_panel(name, factory):
        btn = tk.Button(sidebar, text=name, bg="#2f2f2f", fg="#ffffff", relief="flat", activebackground="#3a3a3a", bd=0,
                        command=lambda i=len(panels): (show_panel(i), set_active_button(btn)))
        btn.pack(fill="x", pady=3, padx=6)
        panel = tk.Frame(content, bg="#1e1e1e")
        factory(panel)
        panels.append(panel)

    def panel_dashboard(panel):
        tk.Label(panel, text="Dashboard", fg="#ffffff", bg="#1e1e1e", font=("Arial", 16, "bold")).pack(anchor="w", padx=10, pady=10)
        stats = [("Active Modules", "6"), ("Platform", sys.platform), ("Python", sys.version.split()[0])]
        for name, value in stats:
            row = tk.Frame(panel, bg="#1e1e1e")
            row.pack(anchor="w", padx=10, pady=2)
            tk.Label(row, text=f"{name}:", fg="#bbbbbb", bg="#1e1e1e").pack(side="left")
            tk.Label(row, text=value, fg="#ffffff", bg="#1e1e1e", font=("Arial", 10, "bold")).pack(side="left", padx=8)

    def panel_zipcrack(panel):
        tk.Label(panel, text="ZIP Cracker", fg="#ffffff", bg="#1e1e1e", font=("Arial", 16, "bold")).pack(anchor="w", padx=10, pady=8)
        path_var = tk.StringVar()
        size_var = tk.IntVar(value=4)
        letters = tk.BooleanVar(value=True)
        numbers = tk.BooleanVar(value=False)
        special = tk.BooleanVar(value=False)

        tk.Label(panel, text="ZIP Path:", fg="#cccccc", bg="#1e1e1e").pack(anchor="w", padx=10)
        tk.Entry(panel, textvariable=path_var, width=60).pack(anchor="w", padx=10, pady=2)
        tk.Label(panel, text="Password Length:", fg="#cccccc", bg="#1e1e1e").pack(anchor="w", padx=10)
        tk.Spinbox(panel, from_=1, to=8, textvariable=size_var, width=5).pack(anchor="w", padx=10, pady=2)

        letters_cb = tk.Checkbutton(panel, text="Letters", variable=letters, onvalue=True, offvalue=False,
                       bg="#1e1e1e", fg="#ffffff", selectcolor="#000000", activebackground="#1e1e1e",
                       highlightthickness=0, borderwidth=0, anchor="w")
        letters_cb.pack(anchor="w", padx=10)
        def toggle_letters():
            if letters.get():
                letters_cb.config(bg="#cc2200")
            else:
                letters_cb.config(bg="#1e1e1e")
        letters_cb.config(command=toggle_letters)

        numbers_cb = tk.Checkbutton(panel, text="Numbers", variable=numbers, onvalue=True, offvalue=False,
                       bg="#1e1e1e", fg="#ffffff", selectcolor="#000000", activebackground="#1e1e1e",
                       highlightthickness=0, borderwidth=0, anchor="w")
        numbers_cb.pack(anchor="w", padx=10)
        def toggle_numbers():
            if numbers.get():
                numbers_cb.config(bg="#cc2200")
            else:
                numbers_cb.config(bg="#1e1e1e")
        numbers_cb.config(command=toggle_numbers)

        special_cb = tk.Checkbutton(panel, text="Special", variable=special, onvalue=True, offvalue=False,
                       bg="#1e1e1e", fg="#ffffff", selectcolor="#000000", activebackground="#1e1e1e",
                       highlightthickness=0, borderwidth=0, anchor="w")
        special_cb.pack(anchor="w", padx=10)
        def toggle_special():
            if special.get():
                special_cb.config(bg="#cc2200")
            else:
                special_cb.config(bg="#1e1e1e")
        special_cb.config(command=toggle_special)

        status = tk.StringVar(value="Ready")
        tk.Label(panel, textvariable=status, fg="#aaaaaa", bg="#1e1e1e").pack(anchor="w", padx=10, pady=4)
        log_widget = make_log_frame(panel)

        btn = tk.Button(panel, text="Run", bg="#cc2200", fg="#ffffff", relief="flat")

        def run():
            target = path_var.get().strip()
            if not target:
                _append_text(log_widget, "[ERROR] ZIP path is required.\n")
                return
            args_list = ["-p", target, "-s", str(size_var.get())]
            if letters.get(): args_list.extend(["-l", "y"])
            if numbers.get(): args_list.extend(["-n", "y"])
            if special.get(): args_list.extend(["-sc", "y"])
            _append_text(log_widget, f"$ zer0specter zipcrack {' '.join(args_list)}\n")
            _run_module(_load_module("zipcrack"), args_list, log_widget, status, btn)

        btn.config(command=run)
        btn.pack(anchor="w", padx=10, pady=8)

    def panel_portscanner(panel):
        tk.Label(panel, text="Port Scanner", fg="#ffffff", bg="#1e1e1e", font=("Arial", 16, "bold")).pack(anchor="w", padx=10, pady=8)
        target_var = tk.StringVar()
        start_var = tk.IntVar(value=1)
        end_var = tk.IntVar(value=1024)
        timeout_var = tk.IntVar(value=1)

        tk.Label(panel, text="Host/IP:", fg="#cccccc", bg="#1e1e1e").pack(anchor="w", padx=10)
        tk.Entry(panel, textvariable=target_var, width=60).pack(anchor="w", padx=10, pady=2)

        tk.Frame(panel, bg="#1e1e1e").pack(anchor="w", padx=10, pady=2)
        frame = tk.Frame(panel, bg="#1e1e1e")
        frame.pack(anchor="w", padx=10)
        tk.Label(frame, text="Start:", fg="#cccccc", bg="#1e1e1e").pack(side="left")
        tk.Spinbox(frame, from_=1, to=65535, textvariable=start_var, width=6).pack(side="left", padx=4)
        tk.Label(frame, text="End:", fg="#cccccc", bg="#1e1e1e").pack(side="left", padx=6)
        tk.Spinbox(frame, from_=1, to=65535, textvariable=end_var, width=6).pack(side="left", padx=4)

        tk.Label(panel, text="Timeout (s):", fg="#cccccc", bg="#1e1e1e").pack(anchor="w", padx=10)
        tk.Spinbox(panel, from_=1, to=30, textvariable=timeout_var, width=6).pack(anchor="w", padx=10, pady=2)

        status = tk.StringVar(value="Pronto")
        tk.Label(panel, textvariable=status, fg="#aaaaaa", bg="#1e1e1e").pack(anchor="w", padx=10, pady=4)
        log_widget = make_log_frame(panel)

        btn = tk.Button(panel, text="Run", bg="#cc2200", fg="#ffffff", relief="flat")

        def run():
            target = target_var.get().strip()
            if not target:
                _append_text(log_widget, "[ERROR] Host/IP is required.\n")
                return
            args_list = ["-t", target, "-s", str(start_var.get()), "-e", str(end_var.get()), "-d", str(timeout_var.get())]
            _append_text(log_widget, f"$ zer0specter portscanner {' '.join(args_list)}\n")
            _run_module(_load_module("portscanner"), args_list, log_widget, status, btn)

        btn.config(command=run)
        btn.pack(anchor="w", padx=10, pady=8)

    def panel_sniffer(panel):
        tk.Label(panel, text="Sniffer", fg="#ffffff", bg="#1e1e1e", font=("Arial", 16, "bold")).pack(anchor="w", padx=10, pady=8)
        iface_var = tk.StringVar()

        tk.Label(panel, text="Interface:", fg="#cccccc", bg="#1e1e1e").pack(anchor="w", padx=10)
        tk.Entry(panel, textvariable=iface_var, width=60).pack(anchor="w", padx=10, pady=2)

        status = tk.StringVar(value="Pronto")
        tk.Label(panel, textvariable=status, fg="#aaaaaa", bg="#1e1e1e").pack(anchor="w", padx=10, pady=4)
        log_widget = make_log_frame(panel)

        btn = tk.Button(panel, text="Run", bg="#cc2200", fg="#ffffff", relief="flat")

        def run():
            iface = iface_var.get().strip()
            if not iface:
                _append_text(log_widget, "[ERROR] Interface is required.\n")
                return
            args_list = ["-i", iface]
            _append_text(log_widget, f"$ zer0specter sniffer {' '.join(args_list)}\n")
            _run_module(_load_module("sniffer"), args_list, log_widget, status, btn)

        btn.config(command=run)
        btn.pack(anchor="w", padx=10, pady=8)

    def panel_wifi(panel):
        tk.Label(panel, text="Wi-Fi Deauth", fg="#ffffff", bg="#1e1e1e",
                font=("Arial", 16, "bold")).pack(anchor="w", padx=10, pady=8)

        iface_var = tk.StringVar()
        ap_var = tk.StringVar()
        client_var = tk.StringVar()
        count_var = tk.IntVar(value=20)
        interval_var = tk.DoubleVar(value=0.1)

        # -------- TOP (inputs)
        top_frame = tk.Frame(panel, bg="#1e1e1e")
        top_frame.pack(fill="x")

        tk.Label(top_frame, text="Interface:", fg="#cccccc", bg="#1e1e1e").pack(anchor="w", padx=10)
        tk.Entry(top_frame, textvariable=iface_var, width=60).pack(anchor="w", padx=10, pady=2)

        tk.Label(top_frame, text="AP MAC:", fg="#cccccc", bg="#1e1e1e").pack(anchor="w", padx=10)
        tk.Entry(top_frame, textvariable=ap_var, width=60).pack(anchor="w", padx=10, pady=2)

        tk.Label(top_frame, text="Client MAC:", fg="#cccccc", bg="#1e1e1e").pack(anchor="w", padx=10)
        tk.Entry(top_frame, textvariable=client_var, width=60).pack(anchor="w", padx=10, pady=2)

        tk.Label(top_frame, text="Count:", fg="#cccccc", bg="#1e1e1e").pack(anchor="w", padx=10)
        tk.Spinbox(top_frame, from_=0, to=10000, textvariable=count_var, width=8).pack(anchor="w", padx=10, pady=2)

        tk.Label(top_frame, text="Intervals:", fg="#cccccc", bg="#1e1e1e").pack(anchor="w", padx=10)
        tk.Entry(top_frame, textvariable=interval_var, width=8).pack(anchor="w", padx=10, pady=2)

        # -------- LOG (separado)
        log_frame = tk.Frame(panel, bg="#1e1e1e")
        log_frame.pack(fill="both", expand=True)

        log_widget = tk.Text(log_frame, bg="#121212", fg="#33ff33",
                            insertbackground="#33ff33", state="disabled")
        log_widget.pack(fill="both", expand=True, padx=10, pady=10)

        # -------- BOTTOM (botão + status)
        bottom_frame = tk.Frame(panel, bg="#1e1e1e")
        bottom_frame.pack(fill="x")

        status = tk.StringVar(value="Ready")
        tk.Label(bottom_frame, textvariable=status, fg="#aaaaaa",
                bg="#1e1e1e").pack(side="left", padx=10, pady=4)

        btn = tk.Button(bottom_frame, text="Start",
                        bg="#cc2200", fg="#ffffff", relief="flat")
        btn.pack(side="right", padx=10, pady=8)

        def run():
            iface = iface_var.get().strip()
            ap = ap_var.get().strip()
            client = client_var.get().strip()

            if not (iface and ap and client):
                _append_text(log_widget, "[ERROR] Please provide interface, AP, and client information.\n")
                return

            args_list = [
                "-i", iface,
                "-a", ap,
                "-c", client,
                "-n", str(count_var.get()),
                "--interval", str(interval_var.get())
            ]

            _append_text(log_widget, f"$ zer0specter wifi {' '.join(args_list)}\n")
            _run_module(_load_module("wifi"), args_list, log_widget, status, btn)

        btn.config(command=run)

    def panel_ipgeo(panel):
        tk.Label(panel, text="IP Locator", fg="#ffffff", bg="#1e1e1e", font=("Arial", 16, "bold")).pack(anchor="w", padx=10, pady=8)
        ip_var = tk.StringVar()

        tk.Label(panel, text="IP: (empty = your IP)", fg="#cccccc", bg="#1e1e1e").pack(anchor="w", padx=10)
        tk.Entry(panel, textvariable=ip_var, width=60).pack(anchor="w", padx=10, pady=2)

        status = tk.StringVar(value="Ready")
        tk.Label(panel, textvariable=status, fg="#aaaaaa", bg="#1e1e1e").pack(anchor="w", padx=10, pady=4)
        log_widget = make_log_frame(panel)

        def run():
            ip = ip_var.get().strip()
            args_list = ["-ip", ip] if ip else []
            _append_text(log_widget, f"$ zer0specter ipgeo {' '.join(args_list)}\n")
            _run_module(_load_module("ipgeo"), args_list, log_widget, status, btn)

        btn = tk.Button(panel, text="Run", bg="#cc2200", fg="#ffffff", relief="flat", command=run)
        btn.pack(anchor="w", padx=10, pady=8)

    def panel_passgen(panel):
        tk.Label(panel, text="Password Generator", fg="#ffffff", bg="#1e1e1e", font=("Arial", 16, "bold")).pack(anchor="w", padx=10, pady=8)
        prefix_var = tk.StringVar()
        length_var = tk.IntVar(value=16)
        upper_var = tk.BooleanVar(value=False)
        nums_var = tk.BooleanVar(value=False)
        punct_var = tk.BooleanVar(value=False)

        tk.Label(panel, text="Prefix (optional):", fg="#cccccc", bg="#1e1e1e").pack(anchor="w", padx=10)
        tk.Entry(panel, textvariable=prefix_var, width=60).pack(anchor="w", padx=10, pady=2)
        tk.Label(panel, text="Length:", fg="#cccccc", bg="#1e1e1e").pack(anchor="w", padx=10)
        tk.Spinbox(panel, from_=4, to=128, textvariable=length_var, width=6).pack(anchor="w", padx=10, pady=2)

        upper_cb = tk.Checkbutton(panel, text="Uppercase", variable=upper_var, onvalue=True, offvalue=False,
                       bg="#1e1e1e", fg="#ffffff", selectcolor="#000000", activebackground="#1e1e1e",
                       highlightthickness=0, borderwidth=0, anchor="w")
        upper_cb.pack(anchor="w", padx=10)
        def toggle_upper():
            if upper_var.get():
                upper_cb.config(bg="#cc2200")
            else:
                upper_cb.config(bg="#1e1e1e")
        upper_cb.config(command=toggle_upper)

        nums_cb = tk.Checkbutton(panel, text="Numbers", variable=nums_var, onvalue=True, offvalue=False,
                       bg="#1e1e1e", fg="#ffffff", selectcolor="#000000", activebackground="#1e1e1e",
                       highlightthickness=0, borderwidth=0, anchor="w")
        nums_cb.pack(anchor="w", padx=10)
        def toggle_nums():
            if nums_var.get():
                nums_cb.config(bg="#cc2200")
            else:
                nums_cb.config(bg="#1e1e1e")
        nums_cb.config(command=toggle_nums)

        punct_cb = tk.Checkbutton(panel, text="Special Characters", variable=punct_var, onvalue=True, offvalue=False,
                       bg="#1e1e1e", fg="#ffffff", selectcolor="#000000", activebackground="#1e1e1e",
                       highlightthickness=0, borderwidth=0, anchor="w")
        punct_cb.pack(anchor="w", padx=10)
        def toggle_punct():
            if punct_var.get():
                punct_cb.config(bg="#cc2200")
            else:
                punct_cb.config(bg="#1e1e1e")
        punct_cb.config(command=toggle_punct)

        status = tk.StringVar(value="Ready")
        tk.Label(panel, textvariable=status, fg="#aaaaaa", bg="#1e1e1e").pack(anchor="w", padx=10, pady=4)
        log_widget = make_log_frame(panel)

        btn = tk.Button(panel, text="Generate", bg="#cc2200", fg="#ffffff", relief="flat", width=15, height=2)

        def run():
            prefix = prefix_var.get().strip()
            args_list = ["-nc", str(length_var.get())]
            if prefix:
                args_list.extend(["-px", prefix])
            if upper_var.get(): args_list.extend(["-up", "y"])
            if nums_var.get(): args_list.extend(["-n", "y"])
            if punct_var.get(): args_list.extend(["-p", "y"])
            _append_text(log_widget, f"$ zer0specter passgen {' '.join(args_list)}\n")
            _run_module(_load_module("passgen"), args_list, log_widget, status, btn)

        btn.config(command=run)
        btn.pack(anchor="w", padx=10, pady=8)


    add_panel("Dashboard", panel_dashboard)
    add_panel("ZIP Cracker", panel_zipcrack)
    add_panel("Port Scanner", panel_portscanner)
    add_panel("Sniffer", panel_sniffer)
    add_panel("IP Locator", panel_ipgeo)
    add_panel("Pass Gen", panel_passgen)

    show_panel(0)
    if sidebar.winfo_children():
        set_active_button(sidebar.winfo_children()[0])

    root.mainloop()


if __name__ == "__main__":
    launch()
