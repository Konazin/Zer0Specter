from __future__ import annotations
from zer0specter.modules.zip_cracker import zipcrack
from zer0specter.modules.passwd_gen import password_generator
from zer0specter.modules.port_scanner import portscanner
from zer0specter.modules.sniffer import sniffer
from zer0specter.modules.wifi_attack import wifi_attack
from zer0specter.modules.ip_geo import ip_locator

import sys

# ── Verificação antecipada de dependências ────────────────────────────────────

def _check_deps() -> None:
    try:
        import PyQt6  # noqa: F401
    except ImportError:
        print("[Zer0Specter GUI] PyQt6 não encontrado.")
        print("  Instale com:  pip install zer0specter[gui]")
        print("  Ou diretamente: pip install PyQt6")
        sys.exit(1)

# ── Imports PyQt6 (após checagem) ─────────────────────────────────────────────

def _build_app():
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
        QStackedWidget, QLabel, QPushButton, QSizePolicy, QStatusBar,
        QFrame, QLineEdit, QSpinBox, QCheckBox, QTextEdit
    )
    from PyQt6.QtCore    import Qt, QSize, QThread, pyqtSignal, QObject
    from PyQt6.QtGui     import QFont, QColor, QPalette, QIcon, QTextCursor

    from zer0specter import __version__

    # ── Paleta de cores (light theme) ────────────────────────────────────
    PALETTE = {
        "bg":        "#f0f0f0",
        "sidebar":   "#dcdcdc",
        "panel":     "#ffffff",
        "accent":    "#007acc",
        "accent_h":  "#005fa0",
        "text":      "#222222",
        "text_dim":  "#555555",
        "border":    "#cccccc",
        "success":   "#1b8c3f",
        "warning":   "#b38600",
        "danger":    "#cc3300",
    }

    SIDEBAR_BTN_STYLE = f"""
        QPushButton {{
            background: transparent;
            color: {PALETTE['text_dim']};
            border: none;
            border-left: 3px solid transparent;
            padding: 12px 20px;
            text-align: left;
            font-size: 13px;
            letter-spacing: 0.5px;
        }}
        QPushButton:hover {{
            color: {PALETTE['text']};
            background: {PALETTE['panel']};
            border-left: 3px solid {PALETTE['accent']};
        }}
        QPushButton:checked {{
            color: {PALETTE['accent_h']};
            background: {PALETTE['panel']};
            border-left: 3px solid {PALETTE['accent_h']};
            font-weight: bold;
        }}
    """

    # ── Sidebar ───────────────────────────────────────────────────────────

    class Sidebar(QFrame):
        ITEMS = [
            ("  Dashboard",    0),
            ("  ZIP Cracker",  1),
            ("  Port Scanner", 2),
            ("  Sniffer",      3),
            ("  Wi-Fi Deauth", 4),
            ("  IP Locator",   5),
            ("  Pass Gen",     6),
        ]

        def __init__(self, stack: QStackedWidget, parent=None):
            super().__init__(parent)
            self.setFixedWidth(200)
            self.setStyleSheet(f"background: {PALETTE['sidebar']}; border-right: 1px solid {PALETTE['border']};")

            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)

            # Logo
            logo = QLabel("  Zer0Specter")
            logo.setStyleSheet(f"color: {PALETTE['accent_h']}; font-size: 15px; font-weight: bold; padding: 24px 20px 16px;")
            layout.addWidget(logo)

            sep = QFrame()
            sep.setFixedHeight(1)
            sep.setStyleSheet(f"background: {PALETTE['border']};")
            layout.addWidget(sep)

            self._buttons: list[QPushButton] = []
            for label, idx in self.ITEMS:
                btn = QPushButton(label)
                btn.setCheckable(True)
                btn.setStyleSheet(SIDEBAR_BTN_STYLE)
                btn.clicked.connect(lambda _, i=idx, b=btn: self._select(i, b, stack))
                layout.addWidget(btn)
                self._buttons.append(btn)

            layout.addStretch()

            # Versão no rodapé
            ver = QLabel(f"  v{__version__}")
            ver.setStyleSheet(f"color: {PALETTE['text_dim']}; font-size: 11px; padding: 12px 20px;")
            layout.addWidget(ver)

            self._buttons[0].setChecked(True)

        def _select(self, index: int, btn: QPushButton, stack: QStackedWidget):
            for b in self._buttons:
                b.setChecked(False)
            btn.setChecked(True)
            stack.setCurrentIndex(index)

    # ── Painéis dos módulos ───────────────────────────────────────────────

    def _base_panel(title: str, subtitle: str) -> tuple[QWidget, QVBoxLayout]:
        """Retorna um widget base com cabeçalho padronizado."""
        w      = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(8)
        w.setStyleSheet(f"background: {PALETTE['panel']};")

        t = QLabel(title)
        t.setStyleSheet(f"color: {PALETTE['accent_h']}; font-size: 20px; font-weight: bold;")
        layout.addWidget(t)

        s = QLabel(subtitle)
        s.setStyleSheet(f"color: {PALETTE['text_dim']}; font-size: 13px;")
        layout.addWidget(s)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {PALETTE['border']}; margin: 8px 0;")
        layout.addWidget(sep)

        return w, layout

    def _make_dashboard() -> QWidget:
        w, layout = _base_panel("Dashboard", "visão geral do sistema")

        stats = [
            ("Módulos ativos",   "6"),
            ("Versão",           f"v{__version__}"),
            ("Plataforma",       sys.platform),
            ("Python",           sys.version.split()[0]),
        ]
        for label, value in stats:
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setStyleSheet(f"color: {PALETTE['text_dim']}; font-size: 13px;")
            val = QLabel(value)
            val.setStyleSheet(f"color: {PALETTE['text']}; font-size: 13px; font-weight: bold;")
            row.addWidget(lbl)
            row.addStretch()
            row.addWidget(val)
            layout.addLayout(row)

        layout.addStretch()

        note = QLabel("⚠  Use apenas em redes e sistemas autorizados.")
        note.setStyleSheet(f"color: {PALETTE['warning']}; font-size: 12px; margin-top: 16px;")
        layout.addWidget(note)
        return w

    active_threads: list[QThread] = []

    def _capture_output(func, args):
        """Executa o módulo e retorna o texto da saída (stdout)."""
        import io, sys

        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            try:
                func(args)
            except SystemExit as se:
                # argparse chama SystemExit em --help/erro; capturar e continuar
                pass
            result = sys.stdout.getvalue()
            if result:
                print(result, end="")  # eco para terminal também
            return result.strip() or "(sem saída)"
        except Exception as exc:
            print(f"[GUI-ERROR] {exc}")
            return f"[ERRO] {exc}"
        finally:
            sys.stdout = old_stdout

    class ModuleWorker(QObject):
        progress = pyqtSignal(str)
        finished = pyqtSignal(str)

        def __init__(self, func, args):
            super().__init__()
            self.func = func
            self.args = args

        def run(self):
            import io, sys

            class _StreamProxy(io.TextIOBase):
                def __init__(self, emit_signal):
                    self.emit_signal = emit_signal

                def write(self, text):
                    if not text:
                        return 0
                    text = str(text)
                    # enviar ao terminal real
                    sys.__stdout__.write(text)
                    sys.__stdout__.flush()
                    # avance para GUI
                    self.emit_signal.emit(text)
                    return len(text)

                def flush(self):
                    try:
                        sys.__stdout__.flush()
                    except Exception:
                        pass

            old_stdout, old_stderr = sys.stdout, sys.stderr
            sys.stdout = _StreamProxy(self.progress)
            sys.stderr = _StreamProxy(self.progress)

            try:
                try:
                    self.func(self.args)
                except SystemExit:
                    pass
                except Exception as exc:
                    print(f"[MODULE ERROR] {exc}")
                finally:
                    pass

                result = "[COMPLETED]"
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr

            self.finished.emit(result)

    def _run_module(func, args, output_widget):
        if isinstance(output_widget, QTextEdit):
            output_widget.clear()
            output_widget.append("Executando...\n")
        else:
            output_widget.setText("Executando...")

        worker = ModuleWorker(func, args)
        thread = QThread()

        worker.moveToThread(thread)

        def update_progress(text: str):
            if isinstance(output_widget, QTextEdit):
                cursor = output_widget.textCursor()
                cursor.movePosition(QTextCursor.End)
                cursor.insertText(text)
                output_widget.setTextCursor(cursor)
            else:
                output_widget.setText(text.strip())

        worker.progress.connect(update_progress)
        worker.finished.connect(lambda text: update_progress(f"\n{text}\n"))
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(lambda: active_threads.remove(thread) if thread in active_threads else None)

        thread.started.connect(worker.run)
        active_threads.append(thread)
        thread.start()

    def _make_passgen_panel() -> QWidget:
        w, layout = _base_panel("Pass Gen", "gerador de senhas seguras")

        length_lbl = QLabel("Comprimento:")
        length_lbl.setStyleSheet(f"color: {PALETTE['text']};")
        length_spin = QSpinBox()
        length_spin.setRange(4, 128)
        length_spin.setValue(16)

        prefix_lbl = QLabel("Prefixo:")
        prefix_lbl.setStyleSheet(f"color: {PALETTE['text']};")
        prefix_edit = QLineEdit()

        punct_cb = QCheckBox("Caracteres especiais")
        nums_cb = QCheckBox("Números")
        upper_cb = QCheckBox("Maiúsculas")

        generate_btn = QPushButton("Gerar senha")
        generate_btn.setStyleSheet(f"background: {PALETTE['accent']}; color: #fff; padding: 8px;")

        output_label = QLabel("")
        output_label.setWordWrap(True)
        output_label.setStyleSheet(f"color: {PALETTE['success']}; font-weight: bold; margin-top: 10px;")

        def on_generate_pass():
            args = ["-nc", str(length_spin.value())]
            if prefix_edit.text():
                args += ["-px", prefix_edit.text()]
            if punct_cb.isChecked():
                args += ["-p", "y"]
            if nums_cb.isChecked():
                args += ["-n", "y"]
            if upper_cb.isChecked():
                args += ["-up", "y"]
            _run_module(password_generator, args, output_label)

        generate_btn.clicked.connect(on_generate_pass)

        for row in [(length_lbl, length_spin), (prefix_lbl, prefix_edit)]:
            hl = QHBoxLayout()
            hl.addWidget(row[0])
            hl.addWidget(row[1])
            layout.addLayout(hl)

        layout.addWidget(punct_cb)
        layout.addWidget(nums_cb)
        layout.addWidget(upper_cb)
        layout.addWidget(generate_btn)
        layout.addWidget(output_label)
        layout.addStretch()
        return w

    def _make_iplocator_panel() -> QWidget:
        w, layout = _base_panel("IP Locator", "geolocalização de endereços IP")

        ip_edit = QLineEdit()
        ip_edit.setPlaceholderText("IP opcional (ex.: 8.8.8.8)")

        locate_btn = QPushButton("Localizar IP")
        locate_btn.setStyleSheet(f"background: {PALETTE['accent']}; color: #fff; padding: 8px;")

        output_text = QTextEdit()
        output_text.setReadOnly(True)
        output_text.setStyleSheet(f"background: {PALETTE['panel']}; color: {PALETTE['text']};")

        def on_locate():
            target = ip_edit.text().strip()
            args = ["-ip", target] if target else []
            _run_module(ip_locator, args, output_text)

        locate_btn.clicked.connect(on_locate)

        layout.addWidget(ip_edit)
        layout.addWidget(locate_btn)
        layout.addWidget(output_text)
        layout.addStretch()
        return w

    def _make_zipcrack_panel() -> QWidget:
        w, layout = _base_panel("ZIP Cracker", "força bruta em arquivos .zip")

        path_edit = QLineEdit()
        path_edit.setPlaceholderText("Caminho do arquivo zip")
        length_spin = QSpinBox(); length_spin.setRange(1, 8); length_spin.setValue(4)
        letters_cb = QCheckBox("Letras")
        numbers_cb = QCheckBox("Números")
        special_cb = QCheckBox("Caracteres especiais")

        run_btn = QPushButton("Iniciar crack")
        run_btn.setStyleSheet(f"background: {PALETTE['accent']}; color: #fff; padding: 8px;")
        out = QTextEdit(); out.setReadOnly(True)

        def on_run():
            args = ["-p", path_edit.text().strip(), "-s", str(length_spin.value())]
            if letters_cb.isChecked(): args += ["-l", "y"]
            if numbers_cb.isChecked(): args += ["-n", "y"]
            if special_cb.isChecked(): args += ["-sc", "y"]
            _run_module(zipcrack, args, out)

        run_btn.clicked.connect(on_run)

        layout.addWidget(path_edit)
        layout.addWidget(QLabel("Tamanho da senha")); layout.addWidget(length_spin)
        layout.addWidget(letters_cb); layout.addWidget(numbers_cb); layout.addWidget(special_cb)
        layout.addWidget(run_btn); layout.addWidget(out); layout.addStretch()
        return w

    def _make_portscanner_panel() -> QWidget:
        w, layout = _base_panel("Port Scanner", "varredura de portas + banner")

        target_edit = QLineEdit(); target_edit.setPlaceholderText("Host ou IP")
        start_spin = QSpinBox(); start_spin.setRange(1, 65535); start_spin.setValue(1)
        end_spin = QSpinBox(); end_spin.setRange(1, 65535); end_spin.setValue(1024)
        timeout_spin = QSpinBox(); timeout_spin.setRange(1, 30); timeout_spin.setValue(1)

        run_btn = QPushButton("Iniciar scan")
        run_btn.setStyleSheet(f"background: {PALETTE['accent']}; color: #fff; padding: 8px;")
        out = QTextEdit(); out.setReadOnly(True)

        def on_run():
            args = ["-t", target_edit.text().strip(), "-s", str(start_spin.value()), "-e", str(end_spin.value()), "-d", str(timeout_spin.value())]
            _run_module(portscanner, args, out)

        run_btn.clicked.connect(on_run)
        layout.addWidget(target_edit)
        layout.addWidget(QLabel("Porta início")); layout.addWidget(start_spin)
        layout.addWidget(QLabel("Porta fim")); layout.addWidget(end_spin)
        layout.addWidget(QLabel("Timeout")); layout.addWidget(timeout_spin)
        layout.addWidget(run_btn); layout.addWidget(out); layout.addStretch()
        return w

    def _make_sniffer_panel() -> QWidget:
        w, layout = _base_panel("Sniffer", "captura de pacotes em tempo real")

        iface_edit = QLineEdit(); iface_edit.setPlaceholderText("Interface (ex.: eth0)")
        run_btn = QPushButton("Iniciar sniffer")
        run_btn.setStyleSheet(f"background: {PALETTE['accent']}; color: #fff; padding: 8px;")
        out = QTextEdit(); out.setReadOnly(True)

        def on_run():
            args = ["-i", iface_edit.text().strip()]
            _run_module(sniffer, args, out)

        run_btn.clicked.connect(on_run)
        layout.addWidget(iface_edit); layout.addWidget(run_btn); layout.addWidget(out); layout.addStretch()
        return w

    def _make_wifiattack_panel() -> QWidget:
        w, layout = _base_panel("Wi-Fi Deauth", "deautenticação de clientes Wi-Fi")

        iface_edit = QLineEdit(); iface_edit.setPlaceholderText("Interface em monitor mode")
        ap_edit = QLineEdit(); ap_edit.setPlaceholderText("MAC do AP")
        client_edit = QLineEdit(); client_edit.setPlaceholderText("MAC do cliente")
        count_spin = QSpinBox(); count_spin.setRange(0, 1000); count_spin.setValue(20)
        interval_spin = QSpinBox(); interval_spin.setRange(0, 10); interval_spin.setValue(0)

        run_btn = QPushButton("Executar ataque")
        run_btn.setStyleSheet(f"background: {PALETTE['danger']}; color: #fff; padding: 8px;")
        out = QTextEdit(); out.setReadOnly(True)

        def on_run():
            args = ["-i", iface_edit.text().strip(), "-a", ap_edit.text().strip(), "-c", client_edit.text().strip(), "-n", str(count_spin.value()), "--interval", str(interval_spin.value())]
            _run_module(wifi_attack, args, out)

        run_btn.clicked.connect(on_run)

        layout.addWidget(iface_edit); layout.addWidget(ap_edit); layout.addWidget(client_edit)
        layout.addWidget(QLabel("Contagem (0 infinito)")); layout.addWidget(count_spin)
        layout.addWidget(QLabel("Intervalo (s)")); layout.addWidget(interval_spin)
        layout.addWidget(run_btn); layout.addWidget(out); layout.addStretch()
        return w

    # ── Janela principal ──────────────────────────────────────────────────

    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle(f"Zer0Specter v{__version__}")
            self.setMinimumSize(960, 620)
            self.setStyleSheet(f"background: {PALETTE['bg']}; color: {PALETTE['text']};")
            self.setStyleSheet(r"""
                QWidget { background: #f4f4f8; color: #1d1d1d; }
                QFrame { background: #ffffff; }
                QLineEdit, QSpinBox, QTextEdit { background: #ffffff; color: #1d1d1d; border: 1px solid #d1d1d1; border-radius: 4px; }
                QPushButton { background: #007acc; color: #ffffff; border: 1px solid #0068b3; border-radius: 4px; padding: 6px 10px; }
                QPushButton:hover { background: #0088ff; }
                QPushButton:pressed { background: #005fa0; }
                QCheckBox { color: #2b2b2b; }
                QLabel { color: #2b2b2b; }
                QStatusBar { background: #e0e0e0; color: #333333; }
            """)

            # Stack de painéis
            stack = QStackedWidget()
            stack.addWidget(_make_dashboard())
            stack.addWidget(_make_zipcrack_panel())
            stack.addWidget(_make_portscanner_panel())
            stack.addWidget(_make_sniffer_panel())
            stack.addWidget(_make_wifiattack_panel())
            stack.addWidget(_make_iplocator_panel())
            stack.addWidget(_make_passgen_panel())

            # Layout principal
            body   = QWidget()
            h_lay  = QHBoxLayout(body)
            h_lay.setContentsMargins(0, 0, 0, 0)
            h_lay.setSpacing(0)
            h_lay.addWidget(Sidebar(stack))
            h_lay.addWidget(stack)

            self.setCentralWidget(body)

            # Status bar
            sb = QStatusBar()
            sb.setStyleSheet(f"background: {PALETTE['sidebar']}; color: {PALETTE['text_dim']}; font-size: 11px;")
            sb.showMessage("Zer0Specter pronto.  Use apenas em ambientes autorizados.")
            self.setStatusBar(sb)

        def closeEvent(self, event):
            for thread in list(active_threads):
                if thread.isRunning():
                    thread.quit()
                    thread.wait(2000)
                    if thread.isRunning():
                        thread.terminate()
            active_threads.clear()
            event.accept()

    return QApplication, MainWindow

# ── Ponto de entrada público ──────────────────────────────────────────────────

def launch(args=None) -> None:
    """Inicializa e exibe a janela principal da GUI."""
    _check_deps()
    QApplication, MainWindow = _build_app()

    app = QApplication(sys.argv)
    app.setApplicationName("Zer0Specter")

    # Estilo sólido via palette para garantir legibilidade e evitar tela preta total
    from PyQt6.QtGui import QPalette, QColor

    app.setStyle("Fusion")
    palette = app.palette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#1e1e1e"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#e8e8e8"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#262626"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#202020"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#000000"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#e8e8e8"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#2d2d2d"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#ededed"))
    palette.setColor(QPalette.ColorRole.BrightText, QColor("#ff5555"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#cc2200"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    app.setPalette(palette)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    launch()