import ast
import json
from pathlib import Path

source = Path("mdeditor.py").read_text(encoding="utf-8")
ast.parse(source, filename="mdeditor.py")
details = Path("details.xml").read_text(encoding="utf-8")
requirements = Path("lib/requirements.txt").read_text(encoding="utf-8")
settings = json.loads(Path("config/settings.json").read_text(encoding="utf-8"))
assert "PyQt5" not in source
assert "PyQt6" in source
assert "app.exec()" in source
assert "exec_()" not in source
assert "QDialog.DialogCode.Accepted" in source
assert "markdown.markdown" in source
assert "<platform>AlphaCube</platform>" in details
assert settings["platform"] == "AlphaCube"
assert "PyQt6" in requirements and "Markdown" in requirements
assert "class MarkdownEditor" in source
print("MDEDITOR_STATIC_FUNCTIONAL_CHECK_OK")
