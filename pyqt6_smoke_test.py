import os
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PyQt6.QtWidgets import QApplication
from mdeditor import MarkdownEditor

app = QApplication([])
window = MarkdownEditor()
window.editor.setPlainText("# Título\n\nTexto **negrita**\n\n- uno\n- dos")
window.update_preview()
assert "Título" in window.preview.toHtml()
assert "negrita" in window.preview.toHtml()
window.update_word_count()
assert "Palabras:" in window.word_count_label.text()
window.text_changed = False
window.close()
app.quit()
print("MDEDITOR_PYQT6_OFFSCREEN_SMOKE_OK")
