import sys
import os
import markdown
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QAction, QFileDialog,
                            QMessageBox, QToolBar, QFontComboBox, QSpinBox, QComboBox,
                            QSplitter, QLabel, QDockWidget, QVBoxLayout, QWidget)
from PyQt5.QtGui import QTextCursor, QFont, QTextCharFormat, QTextBlockFormat, QTextListFormat
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter

class MarkdownEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Editor Markdown Avanzado")
        self.resize(1200, 800)

        # Variables de estado
        self.current_file = None
        self.text_changed = False

        # Crear widgets principales
        self.create_widgets()
        # Crear acciones
        self.create_actions()
        # Crear menús
        self.create_menus()
        # Crear barra de herramientas
        self.create_toolbars()
        # Crear barra de estado
        self.create_statusbar()
        # Configurar conexiones
        self.setup_connections()
        # Aplicar estilos
        self.apply_styles()

        # Configuración inicial
        self.update_title()

    def create_widgets(self):
        # Splitter para dividir editor y vista previa
        self.splitter = QSplitter(Qt.Horizontal)

        # Editor de texto
        self.editor = QTextEdit()
        self.editor.setAcceptRichText(False)  # Para edición de Markdown puro
        self.editor.setLineWrapMode(QTextEdit.WidgetWidth)

        # Vista previa de Markdown
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)

        # Añadir widgets al splitter
        self.splitter.addWidget(self.editor)
        self.splitter.addWidget(self.preview)
        self.splitter.setSizes([600, 400])

        # Establecer widget central
        self.setCentralWidget(self.splitter)

    def create_actions(self):
        # Acciones de archivo
        self.new_action = QAction("&Nuevo", self)
        self.new_action.setShortcut("Ctrl+N")

        self.open_action = QAction("&Abrir", self)
        self.open_action.setShortcut("Ctrl+O")

        self.save_action = QAction("&Guardar", self)
        self.save_action.setShortcut("Ctrl+S")

        self.save_as_action = QAction("Guardar &como", self)
        self.save_as_action.setShortcut("Ctrl+Shift+S")

        self.print_action = QAction("&Imprimir", self)
        self.print_action.setShortcut("Ctrl+P")

        self.exit_action = QAction("&Salir", self)
        self.exit_action.setShortcut("Ctrl+Q")

        # Acciones de edición
        self.undo_action = QAction("&Deshacer", self)
        self.undo_action.setShortcut("Ctrl+Z")

        self.redo_action = QAction("&Rehacer", self)
        self.redo_action.setShortcut("Ctrl+Y")

        self.cut_action = QAction("Cor&tar", self)
        self.cut_action.setShortcut("Ctrl+X")

        self.copy_action = QAction("&Copiar", self)
        self.copy_action.setShortcut("Ctrl+C")

        self.paste_action = QAction("&Pegar", self)
        self.paste_action.setShortcut("Ctrl+V")

        self.select_all_action = QAction("Seleccionar &todo", self)
        self.select_all_action.setShortcut("Ctrl+A")

        # Acciones de formato
        self.bold_action = QAction("&Negrita", self)
        self.bold_action.setShortcut("Ctrl+B")
        self.bold_action.setCheckable(True)

        self.italic_action = QAction("&Itálica", self)
        self.italic_action.setShortcut("Ctrl+I")
        self.italic_action.setCheckable(True)

        self.underline_action = QAction("&Subrayado", self)
        self.underline_action.setShortcut("Ctrl+U")
        self.underline_action.setCheckable(True)

        self.heading1_action = QAction("Título &1", self)
        self.heading1_action.setShortcut("Ctrl+1")

        self.heading2_action = QAction("Título &2", self)
        self.heading2_action.setShortcut("Ctrl+2")

        self.heading3_action = QAction("Título &3", self)
        self.heading3_action.setShortcut("Ctrl+3")

        self.bullet_list_action = QAction("Lista &viñetas", self)
        self.bullet_list_action.setShortcut("Ctrl+Shift+L")

        self.numbered_list_action = QAction("Lista &numerada", self)

        self.link_action = QAction("Insertar &enlace", self)
        self.link_action.setShortcut("Ctrl+K")

        self.image_action = QAction("Insertar &imagen", self)

        # Acciones de vista
        self.toggle_preview_action = QAction("&Vista previa", self)
        self.toggle_preview_action.setShortcut("F9")
        self.toggle_preview_action.setCheckable(True)
        self.toggle_preview_action.setChecked(True)

        # Acciones de ayuda
        self.about_action = QAction("&Acerca de", self)

        # Actualizar acciones
        self.update_actions()

    def create_menus(self):
        # Menú Archivo
        file_menu = self.menuBar().addMenu("&Archivo")
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(self.print_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        # Menú Editar
        edit_menu = self.menuBar().addMenu("&Editar")
        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.cut_action)
        edit_menu.addAction(self.copy_action)
        edit_menu.addAction(self.paste_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.select_all_action)

        # Menú Formato
        format_menu = self.menuBar().addMenu("F&ormato")
        format_menu.addAction(self.bold_action)
        format_menu.addAction(self.italic_action)
        format_menu.addAction(self.underline_action)
        format_menu.addSeparator()
        headings_menu = format_menu.addMenu("&Títulos")
        headings_menu.addAction(self.heading1_action)
        headings_menu.addAction(self.heading2_action)
        headings_menu.addAction(self.heading3_action)
        format_menu.addSeparator()
        format_menu.addAction(self.bullet_list_action)
        format_menu.addAction(self.numbered_list_action)
        format_menu.addSeparator()
        format_menu.addAction(self.link_action)
        format_menu.addAction(self.image_action)

        # Menú Vista
        view_menu = self.menuBar().addMenu("&Vista")
        view_menu.addAction(self.toggle_preview_action)

        # Menú Ayuda
        help_menu = self.menuBar().addMenu("A&yuda")
        help_menu.addAction(self.about_action)

    def create_toolbars(self):
        # Barra de herramientas de archivo
        file_toolbar = QToolBar("Archivo")
        file_toolbar.setIconSize(QSize(16, 16))
        file_toolbar.addAction(self.new_action)
        file_toolbar.addAction(self.open_action)
        file_toolbar.addAction(self.save_action)
        self.addToolBar(file_toolbar)

        # Barra de herramientas de edición
        edit_toolbar = QToolBar("Editar")
        edit_toolbar.setIconSize(QSize(16, 16))
        edit_toolbar.addAction(self.undo_action)
        edit_toolbar.addAction(self.redo_action)
        edit_toolbar.addSeparator()
        edit_toolbar.addAction(self.cut_action)
        edit_toolbar.addAction(self.copy_action)
        edit_toolbar.addAction(self.paste_action)
        self.addToolBar(edit_toolbar)

        # Barra de herramientas de formato
        format_toolbar = QToolBar("Formato")
        format_toolbar.setIconSize(QSize(16, 16))

        # Selector de fuente
        self.font_combo = QFontComboBox()
        self.font_combo.setCurrentFont(QFont("Arial"))
        format_toolbar.addWidget(self.font_combo)

        # Tamaño de fuente
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 72)
        self.font_size.setValue(12)
        format_toolbar.addWidget(self.font_size)

        format_toolbar.addSeparator()
        format_toolbar.addAction(self.bold_action)
        format_toolbar.addAction(self.italic_action)
        format_toolbar.addAction(self.underline_action)

        format_toolbar.addSeparator()
        self.alignment_combo = QComboBox()
        self.alignment_combo.addItems(["Alinear izquierda", "Centrar", "Alinear derecha", "Justificar"])
        format_toolbar.addWidget(self.alignment_combo)

        self.addToolBar(format_toolbar)

    def create_statusbar(self):
        self.status_bar = self.statusBar()
        self.status_label = QLabel("Listo")
        self.status_bar.addWidget(self.status_label)

        # Contador de palabras/caracteres
        self.word_count_label = QLabel("Palabras: 0 | Caracteres: 0")
        self.status_bar.addPermanentWidget(self.word_count_label)

    def setup_connections(self):
        # Conexiones de archivo
        self.new_action.triggered.connect(self.new_file)
        self.open_action.triggered.connect(self.open_file)
        self.save_action.triggered.connect(self.save_file)
        self.save_as_action.triggered.connect(self.save_as_file)
        self.print_action.triggered.connect(self.print_file)
        self.exit_action.triggered.connect(self.close)

        # Conexiones de edición
        self.undo_action.triggered.connect(self.editor.undo)
        self.redo_action.triggered.connect(self.editor.redo)
        self.cut_action.triggered.connect(self.editor.cut)
        self.copy_action.triggered.connect(self.editor.copy)
        self.paste_action.triggered.connect(self.editor.paste)
        self.select_all_action.triggered.connect(self.editor.selectAll)

        # Conexiones de formato
        self.bold_action.triggered.connect(self.toggle_bold)
        self.italic_action.triggered.connect(self.toggle_italic)
        self.underline_action.triggered.connect(self.toggle_underline)

        self.heading1_action.triggered.connect(lambda: self.set_heading(1))
        self.heading2_action.triggered.connect(lambda: self.set_heading(2))
        self.heading3_action.triggered.connect(lambda: self.set_heading(3))

        self.bullet_list_action.triggered.connect(self.insert_bullet_list)
        self.numbered_list_action.triggered.connect(self.insert_numbered_list)

        self.link_action.triggered.connect(self.insert_link)
        self.image_action.triggered.connect(self.insert_image)

        # Conexiones de vista
        self.toggle_preview_action.toggled.connect(self.toggle_preview)

        # Conexiones de ayuda
        self.about_action.triggered.connect(self.about)

        # Conexiones de widgets
        self.font_combo.currentFontChanged.connect(self.set_font)
        self.font_size.valueChanged.connect(self.set_font_size)
        self.alignment_combo.currentIndexChanged.connect(self.set_alignment)

        # Conexiones del editor
        self.editor.textChanged.connect(self.update_preview)
        self.editor.textChanged.connect(self.update_word_count)
        self.editor.textChanged.connect(self.set_text_changed)
        self.editor.cursorPositionChanged.connect(self.update_actions)

    def apply_styles(self):
        # Estilo QSS para toda la aplicación
        style = """
        QMainWindow {
            background-color: #f5f5f5;
        }

        QTextEdit {
            background-color: white;
            border: 1px solid #ccc;
            padding: 5px;
            font-family: Arial;
            font-size: 12pt;
        }

        QToolBar {
            background-color: #f0f0f0;
            border: none;
            padding: 2px;
            spacing: 5px;
        }

        QToolButton {
            padding: 3px;
        }

        QToolButton:hover {
            background-color: #e0e0e0;
        }

        QStatusBar {
            background-color: #f0f0f0;
            border-top: 1px solid #ccc;
        }

        QMenuBar {
            background-color: #f0f0f0;
            border: none;
        }

        QMenuBar::item {
            padding: 5px 10px;
        }

        QMenuBar::item:selected {
            background-color: #e0e0e0;
        }

        QMenu {
            background-color: #f5f5f5;
            border: 1px solid #ccc;
        }

        QMenu::item:selected {
            background-color: #e0e0e0;
        }

        QComboBox, QSpinBox {
            padding: 2px;
            border: 1px solid #ccc;
            background-color: white;
        }
        """
        self.setStyleSheet(style)

    def update_actions(self):
        # Actualizar acciones basadas en el estado actual
        self.undo_action.setEnabled(self.editor.document().isUndoAvailable())
        self.redo_action.setEnabled(self.editor.document().isRedoAvailable())

        cursor = self.editor.textCursor()
        self.copy_action.setEnabled(cursor.hasSelection())
        self.cut_action.setEnabled(cursor.hasSelection())

        # Actualizar estado de formato
        self.bold_action.setChecked(self.get_format_bool("fontWeight", QFont.Bold))
        self.italic_action.setChecked(self.get_format_bool("fontItalic"))
        self.underline_action.setChecked(self.get_format_bool("textUnderline"))

    def get_format_bool(self, prop, value=True):
        cursor = self.editor.textCursor()
        fmt = cursor.charFormat()

        if prop == "fontWeight":
            return fmt.fontWeight() == QFont.Bold
        elif prop == "fontItalic":
            return fmt.fontItalic()
        elif prop == "textUnderline":
            return fmt.fontUnderline()

        return False

    def update_title(self):
        title = "Editor Markdown"
        if self.current_file:
            title = f"{os.path.basename(self.current_file)} - {title}"
        if self.text_changed:
            title = f"*{title}"
        self.setWindowTitle(title)

    def update_word_count(self):
        text = self.editor.toPlainText()
        words = len(text.split())
        chars = len(text)
        self.word_count_label.setText(f"Palabras: {words} | Caracteres: {chars}")

    def update_preview(self):
        if self.toggle_preview_action.isChecked():
            markdown_text = self.editor.toPlainText()
            html = markdown.markdown(markdown_text)
            self.preview.setHtml(html)

    def set_text_changed(self):
        self.text_changed = True
        self.update_title()

    def toggle_preview(self, checked):
        self.preview.setVisible(checked)
        if checked:
            self.update_preview()

    # Funciones de archivo
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
                self.status_label.setText(f"Archivo abierto: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo abrir el archivo:\n{str(e)}")

    def save_file(self):
        if self.current_file:
            try:
                with open(self.current_file, "w", encoding="utf-8") as f:
                    f.write(self.editor.toPlainText())
                self.text_changed = False
                self.update_title()
                self.status_label.setText(f"Archivo guardado: {self.current_file}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo guardar el archivo:\n{str(e)}")
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

    # Funciones de formato
    def toggle_bold(self):
        fmt = QTextCharFormat()
        if self.bold_action.isChecked():
            fmt.setFontWeight(QFont.Bold)
        else:
            fmt.setFontWeight(QFont.Normal)
        self.merge_format(fmt)

    def toggle_italic(self):
        fmt = QTextCharFormat()
        fmt.setFontItalic(self.italic_action.isChecked())
        self.merge_format(fmt)

    def toggle_underline(self):
        fmt = QTextCharFormat()
        fmt.setFontUnderline(self.underline_action.isChecked())
        self.merge_format(fmt)

    def merge_format(self, format):
        cursor = self.editor.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.WordUnderCursor)
        cursor.mergeCharFormat(format)
        self.editor.mergeCurrentCharFormat(format)

    def set_font(self, font):
        fmt = QTextCharFormat()
        fmt.setFontFamily(font.family())
        self.merge_format(fmt)

    def set_font_size(self, size):
        fmt = QTextCharFormat()
        fmt.setFontPointSize(size)
        self.merge_format(fmt)

    def set_alignment(self, index):
        cursor = self.editor.textCursor()
        block_fmt = cursor.blockFormat()

        if index == 0:  # Izquierda
            block_fmt.setAlignment(Qt.AlignLeft)
        elif index == 1:  # Centro
            block_fmt.setAlignment(Qt.AlignCenter)
        elif index == 2:  # Derecha
            block_fmt.setAlignment(Qt.AlignRight)
        elif index == 3:  # Justificar
            block_fmt.setAlignment(Qt.AlignJustify)

        cursor.mergeBlockFormat(block_fmt)

    def set_heading(self, level):
        cursor = self.editor.textCursor()
        fmt = QTextCharFormat()

        # Configurar formato según el nivel de encabezado
        if level == 1:
            fmt.setFontPointSize(24)
            fmt.setFontWeight(QFont.Bold)
        elif level == 2:
            fmt.setFontPointSize(20)
            fmt.setFontWeight(QFont.Bold)
        elif level == 3:
            fmt.setFontPointSize(16)
            fmt.setFontWeight(QFont.Bold)

        self.merge_format(fmt)

        # Insertar el prefijo de markdown si no está ya
        line_text = cursor.block().text()
        if not line_text.startswith("#" * level + " "):
            cursor.movePosition(QTextCursor.StartOfLine)
            cursor.insertText("#" * level + " ")

    def insert_bullet_list(self):
        cursor = self.editor.textCursor()
        cursor.insertText("- ")

    def insert_numbered_list(self):
        cursor = self.editor.textCursor()
        cursor.insertText("1. ")

    def insert_link(self):
        cursor = self.editor.textCursor()
        text = cursor.selectedText()
        if text:
            cursor.insertText(f"[{text}](url)")
        else:
            cursor.insertText("[texto del enlace](url)")

    def insert_image(self):
        cursor = self.editor.textCursor()
        cursor.insertText("![texto alternativo](ruta/a/la/imagen)")

    # Funciones de ayuda
    def about(self):
        QMessageBox.about(self, "Acerca del Editor Markdown",
                         "<h2>Editor Markdown Avanzado</h2>"
                         "<p>Un editor de texto multiplataforma con soporte para Markdown.</p>"
                         "<p>Versión 1.0</p>")

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
