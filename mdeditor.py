import sys
import os
import markdown
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QAction, QFileDialog,
    QMessageBox, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
)
from PyQt5.QtGui import QTextCursor, QFont, QTextCharFormat, QIcon, QColor, QPalette
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter

class MarkdownEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Editor Markdown Avanzado")
        self.resize(1100, 700)
        # Beautiful app icon
        app_icon_path = os.path.join(os.path.dirname(__file__), "app", "app-icon.ico")
        if os.path.exists(app_icon_path):
            self.setWindowIcon(QIcon(app_icon_path))

        # State
        self.current_file = None
        self.text_changed = False

        # Central Widget and Beautiful Layout
        widget = QWidget()
        self.setCentralWidget(widget)
        self.central_layout = QVBoxLayout(widget)
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.central_layout.setSpacing(0)

        # Custom Title/Bar
        title_bar = QLabel("✨ Editor Markdown ✨", alignment=Qt.AlignCenter)
        title_bar.setStyleSheet("font-family: 'Segoe UI'; font-size: 32px; font-weight: bold; color: #fff; background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #67119a, stop:1 #18d6b4); padding: 20px 0; border-bottom-left-radius: 30px; border-bottom-right-radius: 30px;")
        self.central_layout.addWidget(title_bar)

        # Editor/Preview row
        main_row = QHBoxLayout()
        main_row.setSpacing(0)
        self.central_layout.addLayout(main_row, 1)

        # Editor area
        self.editor = QTextEdit()
        self.editor.setAcceptRichText(False)
        self.editor.setStyleSheet("""
            QTextEdit {
                background: #181c2e;
                color: #eaeaea;
                border: none;
                font-family: 'Fira Mono', 'Consolas', monospace;
                font-size: 17px;
                padding: 30px;
                border-top-left-radius: 25px;
                border-bottom-left-radius: 25px;
            }
            QTextEdit:focus { border: 2px solid #18d6b4; }
        """)
        self.editor.setPlaceholderText("Escribe Markdown aquí…")
        main_row.addWidget(self.editor, 3)

        # Preview area
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setStyleSheet("""
            QTextEdit {
                background: #222043;
                color: #b5e0e2;
                border: none;
                font-family: 'Segoe UI', 'Arial';
                font-size: 17px;
                padding: 30px;
                border-top-right-radius: 25px;
                border-bottom-right-radius: 25px;
            }
        """)
        main_row.addWidget(self.preview, 3)

        # File Tools Bar (Flat color buttons, fixed HEX codes, no gradients, no box-shadow)
        tools_bar = QHBoxLayout()
        tools_bar.setSpacing(18)
        tools_bar.setContentsMargins(28, 16, 28, 16)

        BUTTON_STYLE = """
            QPushButton {
                background: #18d6b4;
                color: white;
                font-size: 17px;
                font-family: 'Segoe UI';
                border: none;
                border-radius: 24px;
                min-width: 110px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background: #14e88b;
                color: white;
            }
        """

        self.btn_new = QPushButton("🆕 Nuevo")
        self.btn_new.setStyleSheet(BUTTON_STYLE)
        tools_bar.addWidget(self.btn_new)

        self.btn_open = QPushButton("📂 Abrir")
        self.btn_open.setStyleSheet(BUTTON_STYLE)
        tools_bar.addWidget(self.btn_open)

        self.btn_save = QPushButton("💾 Guardar")
        self.btn_save.setStyleSheet(BUTTON_STYLE)
        tools_bar.addWidget(self.btn_save)

        self.btn_save_as = QPushButton("📝 Guardar como")
        self.btn_save_as.setStyleSheet(BUTTON_STYLE)
        tools_bar.addWidget(self.btn_save_as)

        self.btn_print = QPushButton("🖨️ Imprimir")
        self.btn_print.setStyleSheet(BUTTON_STYLE)
        tools_bar.addWidget(self.btn_print)

        self.btn_about = QPushButton("❓ Acerca de")
        self.btn_about.setStyleSheet(BUTTON_STYLE)
        tools_bar.addWidget(self.btn_about)

        tools_bar.addStretch(1)

        # Toggle Preview Button (OK to keep its style as it's legal CSS)
        self.btn_toggle_preview = QPushButton("👓 Vista previa")
        self.btn_toggle_preview.setStyleSheet("""
            QPushButton {
                background: #fff; color: #67119a; font-weight: bold;
                border-radius: 21px; padding: 7px 16px; border: 2px solid #18d6b4;
            }
            QPushButton:checked { background: #18d6b4; color: white; }
        """)
        self.btn_toggle_preview.setCheckable(True)
        self.btn_toggle_preview.setChecked(True)
        tools_bar.addWidget(self.btn_toggle_preview)

        self.central_layout.insertLayout(1, tools_bar)

        # Status bar (beautified)
        self.status = QLabel("✨ Listo")
        self.status.setStyleSheet("color: #fff; font-size: 15px; background: #67119a; padding: 6px 14px; border-bottom-left-radius: 13px;")
        self.central_layout.addWidget(self.status)

        # Word/Char Count to the right
        self.word_count_label = QLabel("Palabras: 0 | Caracteres: 0")
        self.word_count_label.setStyleSheet("color: #fff; background: #67119a; font-size: 15px; padding: 6px 18px; border-bottom-right-radius: 13px; qproperty-alignment: AlignRight;")
        word_info_row = QHBoxLayout()
        word_info_row.addStretch(1)
        word_info_row.addWidget(self.word_count_label)
        self.central_layout.addLayout(word_info_row)

        # Connections
        self.btn_new.clicked.connect(self.new_file)
        self.btn_open.clicked.connect(self.open_file)
        self.btn_save.clicked.connect(self.save_file)
        self.btn_save_as.clicked.connect(self.save_as_file)
        self.btn_print.clicked.connect(self.print_file)
        self.btn_about.clicked.connect(self.about)
        self.btn_toggle_preview.toggled.connect(self.toggle_preview)

        self.editor.textChanged.connect(self.update_preview)
        self.editor.textChanged.connect(self.update_word_count)
        self.editor.textChanged.connect(self.set_text_changed)

        self.update_preview()
        self.update_word_count()

        # Apply global stylesheet for gorgeous look
        self.setStyleSheet("""
            QMainWindow {
                background-color: #23213a;
            }
            QLabel {
                font-family: 'Segoe UI';
            }
        """)

    def update_title(self):
        title = "Editor Markdown"
        if self.current_file:
            title = f"{os.path.basename(self.current_file)} - {title}"
        if self.text_changed:
            title = f"*{title}"
        self.setWindowTitle(title)

    def update_word_count(self):
        text = self.editor.toPlainText()
        words = len(text.strip().split())
        chars = len(text)
        self.word_count_label.setText(f"Palabras: {words} | Caracteres: {chars}")

    def update_preview(self):
        if self.btn_toggle_preview.isChecked():
            markdown_text = self.editor.toPlainText()
            html = markdown.markdown(markdown_text, extensions=["fenced_code", "tables", "codehilite"])
            # Improve the preview with beautiful CSS for Markdown
            beautiful_css = """
                <style>
                body { background: #222043; color: #b5e0e2; font-family: 'Segoe UI', 'Arial'; font-size: 1.1em; }
                h1, h2, h3, h4 { color: #18d6b4; margin-top: 1.3em; }
                code, pre { background: #17152f; color: #f9d49b; border-radius: 8px; padding: 3px 8px; font-family: 'Fira Mono','Consolas',monospace; }
                a { color: #c379f7; text-decoration: underline; }
                ul, ol { margin-left: 32px; }
                blockquote { border-left: 5px solid #18d6b4; background: #201e36; color: #f0ecec; margin: 10px 0px; padding: 11px 18px; border-radius: 7px; }
                table { border-collapse: collapse; background: #241e30; }
                th, td { border: 1px solid #18d6b4; padding: 7px 15px; color: #dff2eb; }
                </style>
            """
            self.preview.setHtml(beautiful_css + "<body>" + html + "</body>")
        else:
            self.preview.clear()

    def set_text_changed(self):
        self.text_changed = True
        self.update_title()
        self.status.setText("⏳ Cambios no guardados")

    def toggle_preview(self, checked):
        self.preview.setVisible(checked)
        if checked:
            self.update_preview()

    # --- File Actions ---
    def new_file(self):
        if self.text_changed:
            reply = QMessageBox.question(
                self, "Documento no guardado",
                "¿Desea guardar los cambios antes de crear un nuevo documento?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            if reply == QMessageBox.Save:
                self.save_file()
            elif reply == QMessageBox.Cancel:
                return
        self.editor.clear()
        self.current_file = None
        self.text_changed = False
        self.update_title()
        self.status.setText("✨ Nuevo documento creado")

    def open_file(self):
        if self.text_changed:
            reply = QMessageBox.question(
                self, "Documento no guardado",
                "¿Desea guardar los cambios antes de abrir otro documento?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            if reply == QMessageBox.Save:
                self.save_file()
            elif reply == QMessageBox.Cancel:
                return
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Abrir archivo", "",
            "Archivos Markdown (*.md *.markdown);;Todos los archivos (*.*)"
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    self.editor.setPlainText(f.read())
                self.current_file = file_path
                self.text_changed = False
                self.update_title()
                self.status.setText(f"🟢 Archivo abierto: {os.path.basename(file_path)}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo abrir el archivo:\n{str(e)}")
                self.status.setText("❌ Error al abrir el archivo")

    def save_file(self):
        if self.current_file:
            try:
                with open(self.current_file, "w", encoding="utf-8") as f:
                    f.write(self.editor.toPlainText())
                self.text_changed = False
                self.update_title()
                self.status.setText(f"💾 Archivo guardado: {os.path.basename(self.current_file)}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo guardar el archivo:\n{str(e)}")
                self.status.setText("❌ Error al guardar el archivo")
        else:
            self.save_as_file()

    def save_as_file(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Guardar como", "",
            "Archivos Markdown (*.md *.markdown);;Todos los archivos (*.*)"
        )
        if file_path:
            self.current_file = file_path
            self.save_file()

    def print_file(self):
        printer = QPrinter()
        dialog = QPrintDialog(printer, self)
        if dialog.exec_() == QPrintDialog.Accepted:
            self.editor.print_(printer)

    # --- About Dialog ---
    def about(self):
        QMessageBox.about(
            self, "Acerca del Editor Markdown",
            "<h2 style='color:#18d6b4;'>Editor Markdown</h2>"
            "<p>Un editor de texto bello, moderno y multiplataforma con soporte para Markdown y vista previa estilizada.</p>"
            "<p><b>Versión:</b> v2.0-25.11-18.48 UltraGlitter</p>"
            "<p>Hecho por <b>JESUS QUIJADA (JESUSQUIJADA34)</b></p>"
        )

    def closeEvent(self, event):
        if self.text_changed:
            reply = QMessageBox.question(
                self, "Documento no guardado",
                "¿Desea guardar los cambios antes de salir?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )

            if reply == QMessageBox.Save:
                self.save_file()
                event.accept()
            elif reply == QMessageBox.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = MarkdownEditor()
    editor.show()
    sys.exit(app.exec_())
