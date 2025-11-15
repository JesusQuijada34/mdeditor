# GitHub Copilot
# Updated updater.py: better error handling, performance, cross-platform installer generator,
# background worker for network I/O, Windows "acrylic" attempt, custom titlebar with SVG system buttons.

import sys
import os
import tempfile
import threading
import time
import traceback
import shutil
import subprocess
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPainter, QColor, QBrush, QIcon, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QMessageBox,
    QHBoxLayout, QFrame
)

# Config
XML_PATH = "details.xml"
LOG_PATH = "updater_log.txt"
CHECK_INTERVAL = 60  # seconds
GITHUB_API = "https://api.github.com"
INSTANCE_LOCK = os.path.join(tempfile.gettempdir(), "updater_running.lock")

# Lightweight QSS and fonts (kept minimal for clarity)
STYLE = """
QWidget { background-color: rgba(22,27,34,0.88); color: #c9d1d9; font-family: 'Segoe UI', 'JetBrains Mono', monospace; }
QLabel { color: #dbeafe; }
QPushButton { background:#2ea043;color:white;border-radius:8px;padding:8px 12px; }
QPushButton#flat { background:transparent;border:0;color:#c9d1d9; }
.titlebar { background:transparent; }
"""

# Small inline SVG icons for system buttons (UWP-like minimal)
SVG_MINIMIZE = """<svg viewBox="0 0 10 10" xmlns="http://www.w3.org/2000/svg"><rect x="1" y="5" width="8" height="1" rx="0.3" fill="currentColor"/></svg>"""
SVG_MAXIMIZE = """<svg viewBox="0 0 10 10" xmlns="http://www.w3.org/2000/svg"><rect x="1" y="1" width="8" height="8" stroke="currentColor" fill="none" stroke-width="0.9" rx="0.7"/></svg>"""
SVG_CLOSE = """<svg viewBox="0 0 10 10" xmlns="http://www.w3.org/2000/svg"><path d="M2 2 L8 8 M8 2 L2 8" stroke="currentColor" stroke-width="0.9" stroke-linecap="round"/></svg>"""

# Utilities
def log(msg):
    ts = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"{ts} {msg}\n")
    except Exception:
        pass
    print(f"{ts} {msg}")

def safe_parse_xml(text):
    try:
        root = ET.fromstring(text)
        return {
            "app": (root.findtext("app") or "").strip(),
            "version": (root.findtext("version") or "").strip(),
            "platform": (root.findtext("platform") or "").strip(),
            "author": (root.findtext("author") or "").strip()
        }
    except Exception as e:
        log(f"❌ XML parse error: {e}")
        return {}

def read_local_xml(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return safe_parse_xml(f.read())
    except Exception as e:
        log(f"❌ Error reading local XML: {e}")
        return {}

# Cross-platform rename of locked file best-effort
def try_rename_inuse(fname):
    for suffix in (".bak", ".old", ".waiting"):
        bak = fname + suffix
        try:
            if os.path.exists(fname):
                os.replace(fname, bak)
                log(f"ℹ️ Renamed {fname} -> {bak}")
                return True
        except PermissionError:
            continue
        except Exception as e:
            log(f"❌ rename error {fname}: {e}")
            continue
    return False

def generate_installer(ruta_carpeta, url, nombre_zip, log_path):
    """Generate platform-appropriate installer: .bat on Windows, .sh on *nix"""
    batch_id = uuid.uuid4().hex[:8]
    tmp = tempfile.gettempdir()
    if os.name == "nt":
        name = f"update_{batch_id}.bat"
    else:
        name = f"update_{batch_id}.sh"
    path = os.path.join(tmp, name)
    zip_full = os.path.join(ruta_carpeta, nombre_zip)
    log_full = os.path.join(ruta_carpeta, log_path)
    exe_to_launch = None
    try:
        for f in os.listdir(ruta_carpeta):
            if f.endswith(".exe") and f.lower() != os.path.basename(sys.argv[0]).lower():
                exe_to_launch = f
                break
    except Exception:
        pass

    try:
        if os.name == "nt":
            lines = [
                '@echo off',
                f'cd /d "{ruta_carpeta}"',
                f'echo [{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] Starting update... >> "{log_full}"',
                f'if exist "{zip_full}" del /f /q "{zip_full}"',
                f'bitsadmin /transfer "UpdateJob" /download /priority normal "{url}" "{zip_full}" || powershell -Command "(New-Object System.Net.WebClient).DownloadFile(\'{url}\', \'{zip_full}\')"',
                f'if exist "{zip_full}" (',
                f'  powershell -Command "Expand-Archive -Path \\"{zip_full}\\" -DestinationPath \\"{ruta_carpeta}\\" -Force"',
                f'  del /f /q "{zip_full}"',
                f') else ( echo ERROR downloading >> "{log_full}" )',
            ]
            if exe_to_launch:
                lines.append(f'start "" "{os.path.join(ruta_carpeta, exe_to_launch)}"')
            lines.append('exit /b 0')
        else:
            lines = [
                '#!/usr/bin/env bash',
                f'cd "{ruta_carpeta}" || exit 1',
                f'echo "[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] Starting update..." >> "{log_full}"',
                f'rm -f "{zip_full}"',
                f'curl -L -o "{zip_full}" "{url}" || wget -O "{zip_full}" "{url}" || true',
                f'if [ -f "{zip_full}" ]; then',
                f'  unzip -o "{zip_full}" -d "{ruta_carpeta}" || true',
                f'  rm -f "{zip_full}"',
                f'else',
                f'  echo "ERROR downloading" >> "{log_full}"',
                f'fi',
            ]
            if exe_to_launch:
                lines.append(f'nohup "{os.path.join(ruta_carpeta, exe_to_launch)}" >/dev/null 2>&1 &')
            lines.append('exit 0')
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        if os.name != "nt":
            os.chmod(path, 0o755)
        log(f"Installer generated at {path}")
        return path
    except Exception as e:
        log(f"❌ generate_installer error: {e}")
        return None

# Background worker to poll GitHub and check updates (keeps UI responsive)
class UpdateChecker(QThread):
    update_found = pyqtSignal(str, str, str, str)  # app, version, platform, url
    def __init__(self, xml_path=XML_PATH, interval=CHECK_INTERVAL, parent=None):
        super().__init__(parent)
        self.xml_path = xml_path
        self.interval = max(5, int(interval))
        self._stop = threading.Event()
        # lightweight metrics to help diagnose network issues
        self.metrics = {"checks": 0, "failures": 0, "last_response_ms": None}
        # robust requests session with retries for transient network errors
        self.session = requests.Session()
        retries = Retry(total=3, backoff_factor=0.5, status_forcelist=(500, 502, 503, 504))
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        self.session.headers.update({"Accept": "application/vnd.github.v3+json", "User-Agent": "updater"})

    def run(self):
        while not self._stop.is_set():
            try:
                if not self._has_connection():
                    self._emit_log("🌐 No network, waiting...")
                    time.sleep(5)
                    continue
                datos = read_local_xml(self.xml_path)
                if not datos or not datos.get("author"):
                    self._emit_log("⚠️ Local XML missing or invalid.")
                    time.sleep(self.interval)
                    continue
                self._emit_log(f"📖 {datos['app']} v{datos['version']} ({datos['platform']})")
                remote_version = self._read_remote_version(datos["author"], datos["app"])
                if remote_version and remote_version != datos["version"]:
                    self._emit_log(f"🔄 Remote version {remote_version}")
                    url = self._find_asset(datos["author"], datos["app"], remote_version, datos["platform"])
                    if url:
                        self.update_found.emit(datos["app"], remote_version, datos["platform"], url)
                        return
                    else:
                        self._emit_log("❌ Asset not found for platform")
                else:
                    self._emit_log("ℹ️ No updates")
            except Exception as e:
                self._emit_log(f"❌ Checker error: {e}")
            # sleep with early exit check
            for _ in range(int(self.interval)):
                if self._stop.is_set():
                    break
                time.sleep(1)

    def stop(self):
        """Signal the background checker thread to stop."""
        self._stop.set()

    def _emit_log(self, msg):
        """Internal logging helper for the checker (keeps signature used in run())."""
        try:
            self.metrics["checks"] = self.metrics.get("checks", 0) + 1
        except Exception:
            pass
        log(msg)

    def _has_connection(self):
        try:
    def _has_connection(self):
        try:
            # lightweight connectivity check
            self.session.get(GITHUB_API, timeout=4)
            return True
        except Exception:
            return False
        url = f"{GITHUB_API}/repos/{author}/{app}/releases/tags/{version}"
        try:
            r = self.session.get(url, timeout=8)
            if r.status_code != 200:
                self._emit_log(f"❌ Release {version} not found")
                return None
            assets = r.json().get("assets", [])
            target = f"{app}-{version}-{platform}.iflapp"
            for a in assets:
                if a.get("name") == target:
                    return a.get("browser_download_url")
            return None
        except Exception as e:
            self._emit_log(f"❌ GitHub API error: {e}")
            return None

# Platform-specific attempt to enable Windows blur (Mica/ Acrylic). Non-fatal if fails.
def try_enable_windows_blur(win):
    if os.name != "nt":
        return
    try:
        import ctypes
        from ctypes import wintypes
        # Try DwmEnableBlurBehindWindow (classic blur behind) as a safe option:
        dwm = ctypes.windll.dwmapi
        class DWM_BLURBEHIND(ctypes.Structure):
            _fields_ = [("dwFlags", wintypes.DWORD), ("fEnable", wintypes.BOOL),
                        ("hRgnBlur", wintypes.HRGN), ("fTransitionOnMaximized", wintypes.BOOL)]
        DWM_BB_ENABLE = 0x00000001
        bb = DWM_BLURBEHIND()
        bb.dwFlags = DWM_BB_ENABLE
        bb.fEnable = True
        bb.hRgnBlur = 0
        bb.fTransitionOnMaximized = False
        hwnd = wintypes.HWND(int(win.winId()))
        dwm.DwmEnableBlurBehindWindow(hwnd, ctypes.byref(bb))
    except Exception:
        log("ℹ️ Windows blur not available or failed (non-fatal)")

# Helper to convert small SVG string to QIcon
def svg_to_icon(svg_str, size=16, color="#c9d1d9"):
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    from PyQt5.QtSvg import QSvgRenderer
    renderer = QSvgRenderer(bytes(svg_str.replace("currentColor", color), "utf-8"))
    painter = QPainter(pix)
    renderer.render(painter)
    painter.end()
    return QIcon(pix)

# Custom frameless window with titlebar and system buttons, acrylic-like background
class UpdaterWindow(QWidget):
    def __init__(self, appname, version, platform, url):
        super().__init__(flags=Qt.Window)
        self.appname = appname
        self.version = version
        self.platform = platform
        self.url = url
        self.setWindowTitle(f"Updater - {appname}")
        self.setFixedSize(560, 320)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet(STYLE)
        try_enable_windows_blur(self)
        self._drag_pos = None
        self.init_ui()

    def paintEvent(self, e):
        super().paintEvent(e)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = self.rect().adjusted(0, 0, -1, -1)
        p.setBrush(QBrush(QColor(22, 27, 34, 220)))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(r, 14, 14)

    def init_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(12, 12, 12, 12)
        main.setSpacing(8)

        # Title bar
        titlebar = QFrame(self)
        titlebar.setObjectName("titlebar")
        tb_layout = QHBoxLayout(titlebar)
        tb_layout.setContentsMargins(8, 6, 8, 6)
        tb_layout.setSpacing(6)
        title = QLabel(f"{self.appname} — Actualizador", self)
        title.setFont(QFont("Segoe UI", 11))
        title.setStyleSheet("color:#e6eef8;")
        tb_layout.addWidget(title)
        tb_layout.addStretch()

        btn_min = QPushButton()
        btn_max = QPushButton()
        btn_close = QPushButton()
        btn_min.setObjectName("flat"); btn_max.setObjectName("flat"); btn_close.setObjectName("flat")
        btn_min.setIcon(svg_to_icon(SVG_MINIMIZE, 12))
        btn_max.setIcon(svg_to_icon(SVG_MAXIMIZE, 12))
        btn_close.setIcon(svg_to_icon(SVG_CLOSE, 12, color="#ff6b6b"))
        btn_min.setFixedSize(36, 24); btn_max.setFixedSize(36, 24); btn_close.setFixedSize(36, 24)
        btn_min.clicked.connect(self.showMinimized)
        btn_max.clicked.connect(self.toggle_max_restore)
        btn_close.clicked.connect(self.close)
        tb_layout.addWidget(btn_min); tb_layout.addWidget(btn_max); tb_layout.addWidget(btn_close)
        main.addWidget(titlebar)

        # Body
        body = QVBoxLayout()
        body.setSpacing(10)
        lbl = QLabel(f"v{self.version} ({self.platform})")
        lbl.setFont(QFont("JetBrains Mono", 12))
        lbl.setStyleSheet("color:#9ad1ff")
        lbl.setAlignment(Qt.AlignCenter)
        body.addWidget(lbl)
        info = QLabel("Hay una actualización disponible. ¿Deseas actualizar ahora?\nSe generará un instalador seguro y automático.")
        info.setWordWrap(True)
        info.setAlignment(Qt.AlignCenter)
        body.addWidget(info)

        btns = QHBoxLayout()
        btn_cancel = QPushButton("Cancelar")
        btn_python = QPushButton("Actualizar (Python)")
        btn_batch = QPushButton("Actualizar (Rápido)")
        btns.addStretch()
        btns.addWidget(btn_cancel); btns.addWidget(btn_python); btns.addWidget(btn_batch); btns.addStretch()
        btn_cancel.clicked.connect(self.close)
        btn_python.clicked.connect(self.install_python)
        btn_batch.clicked.connect(self.install_batch)

        body.addLayout(btns)
        main.addLayout(body)

    def mousePressEvent(self, ev):
        if ev.button() == Qt.LeftButton:
            self._drag_pos = ev.globalPos() - self.frameGeometry().topLeft()
            ev.accept()

    def mouseMoveEvent(self, ev):
        if self._drag_pos and ev.buttons() & Qt.LeftButton:
            self.move(ev.globalPos() - self._drag_pos)
            ev.accept()

    def toggle_max_restore(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def show_permission_error(self, fn):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Permiso Denegado")
        msg.setText(f"No se pudo actualizar el archivo: {fn}\nCierra la aplicación objetivo o ejecuta como administrador.")
        msg.exec_()

    def install_python(self):
        # Simple, safe python fallback (runs in background thread)
        t = threading.Thread(target=self._install_python_worker, daemon=True)
        t.start()
        QMessageBox.information(self, "Instalación iniciada", "La instalación mediante Python se está ejecutando en segundo plano. Revisa el log.")
        self.close()

    def _install_python_worker(self):
        destino = "update.zip"
        try:
            log("🔐 Backing up files")
            bakdir = "backup_embestido"
            os.makedirs(bakdir, exist_ok=True)
            for f in os.listdir("."):
                if f in (bakdir, destino):
                    continue
                if os.path.isfile(f):
                    try:
                        shutil.copy2(f, os.path.join(bakdir, f))
                    except Exception as e:
                        log(f"⚠️ backup {f}: {e}")
            log(f"⬇️ Downloading {self.url}")
            with requests.get(self.url, stream=True, timeout=30) as r:
                r.raise_for_status()
                with open(destino, "wb") as out:
                    for chunk in r.iter_content(8192):
                        if chunk:
                            out.write(chunk)
            try:
                shutil.unpack_archive(destino, ".")
            except PermissionError as ex:
                fn = getattr(ex, "filename", "") or ""
                log(f"🔀 PermissionError unpacking, trying rename: {fn}")
                if fn and try_rename_inuse(fn):
                    try:
                        shutil.unpack_archive(destino, ".")
                    except Exception as again:
                        log(f"❌ final unpack error: {again}")
                        self.show_permission_error(fn)
                        return
                else:
                    self.show_permission_error(fn or "(unknown)")
                    return
            except Exception as e:
                log(f"❌ unpack failed: {e}")
                return
            try:
                os.remove(destino)
            except Exception:
                pass
            # Relaunch if app binary present
            exe = f"{self.appname}.exe" if os.name == "nt" else f"./{self.appname}"
            if os.path.exists(exe):
                try:
                    subprocess.Popen([exe], cwd=os.path.abspath(os.path.dirname(__file__)))
                except Exception:
                    pass
            log("✅ Python install finished.")
        except Exception as e:
            log(f"❌ install_python error: {e}\n{traceback.format_exc()}")

            log(f"Launching installer: {script}")
            if os.name == "nt":
                os.startfile(script)
            else:
                # ensure we invoke the script directly (it is created executable on non-NT)
                try:
                    subprocess.Popen([script])
                except Exception:
        except Exception as e:
            log(f"❌ install_python error: {e}\n{traceback.format_exc()}")
            # Inform the user and stop this worker; do not reference undefined variables.
            try:
                QMessageBox.warning(self, "Error de instalación", "La instalación automática falló. Consulta el log para más detalles.")
            except Exception:
                pass
            return
                        log("🛑 Another updater instance running.")
                        return
                    except OSError:
                        # stale lock, remove it
                        log("⚠️ Stale instance lock found and will be removed.")
                        try:
                            os.remove(INSTANCE_LOCK)
                        except Exception:
def main():
    # Acquire simple PID lock to avoid multiple instances (tries to clear stale locks)
    try:
        if os.path.exists(INSTANCE_LOCK):
            try:
                with open(INSTANCE_LOCK, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    pid = int(content or "0")
                if pid > 0:
                    try:
                        # signal 0 does not kill; it raises if process does not exist (works on Unix and Windows)
                        os.kill(pid, 0)
                        log("🛑 Another updater instance running.")
                        return
                    except OSError:
                        # stale lock, remove it
                        log("⚠️ Stale instance lock found and will be removed.")
                        try:
                            os.remove(INSTANCE_LOCK)
                        except Exception:
                            pass
            except Exception:
                # corrupted lock file, remove and continue
                try:
                    os.remove(INSTANCE_LOCK)
                except Exception:
                    pass
        try:
            with open(INSTANCE_LOCK, "w", encoding="utf-8") as f:
                f.write(str(os.getpid()))
        except Exception as e:
            log(f"❌ Could not create instance lock: {e}")
            return

        log("Updater started.")
        # Start Qt app and background checker
        app = QApplication(sys.argv)
        checker = UpdateChecker()
        # If update found, show UI on main thread
        def on_update(appname, version, platform, url):
            win = UpdaterWindow(appname, version, platform, url)
            win.show()

        checker.update_found.connect(on_update)
        checker.start()
        try:
            sys.exit(app.exec_())
        finally:
            # Ensure checker stops and lock is removed on exit
            try:
                checker.stop()
                checker.wait(2000)
            except Exception:
                pass
            try:
                if os.path.exists(INSTANCE_LOCK):
                    os.remove(INSTANCE_LOCK)
            except Exception:
                pass

if __name__ == "__main__":
    main()