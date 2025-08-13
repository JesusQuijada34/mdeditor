# Editor de Texto Avanzado con Markdown

![Editor de Texto](assets/screenshots/screenshot-1.png)

---
## Descripción

Un editor de texto moderno y multiplataforma con soporte para Markdown, diseñado para funcionar tanto en Windows como en Linux. Combina las funcionalidades de un editor de texto avanzado con la simplicidad del formato Markdown, incluyendo una vista previa en tiempo real.

---

## Características principales

✅ **Interfaz tipo Word 365** con barras de herramientas organizadas  
✅ **Soporte completo para Markdown** con vista previa en tiempo real  
✅ **Formato de texto avanzado**: negritas, cursivas, encabezados, listas  
✅ **Multiplataforma**: Funciona en Windows y Linux  
✅ **Contador de palabras y caracteres**  
✅ **Sistema de archivos completo**: nuevo, abrir, guardar, guardar como  
✅ **Impresión de documentos**  
✅ **Diseño personalizable** con estilos QSS  

---

## Requisitos del sistema

- Python 3.7 o superior
- Sistemas soportados:
  - Windows 10/11
  - Linux (Ubuntu, Fedora, etc.)

---

## Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/markdown-editor.git
   cd markdown-editor
   ```

2. Crea y activa un entorno virtual (recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

---

## Uso

Ejecuta la aplicación con:
```bash
python dpad.py
```

---

### Atajos de teclado importantes

| Combinación | Acción |
|------------|--------|
| Ctrl+N | Nuevo documento |
| Ctrl+O | Abrir documento |
| Ctrl+S | Guardar |
| Ctrl+Shift+S | Guardar como |
| Ctrl+P | Imprimir |
| Ctrl+B | Negrita |
| Ctrl+I | Cursiva |
| Ctrl+U | Subrayado |
| Ctrl+1/2/3 | Encabezado 1/2/3 |
| F9 | Mostrar/ocultar vista previa |

---

## Capturas de pantalla

*[Incluir aquí 2-3 capturas de pantalla mostrando:*
1. *La interfaz principal con el editor y vista previa*
2. *El menú de formato en acción*
3. *El diálogo de guardar archivo]*

---

## Roadmap

- [ ] Añadir resaltado de sintaxis Markdown
- [ ] Implementar temas oscuros/claros
- [ ] Añadir soporte para tablas
- [ ] Implementar exportación a PDF
- [ ] Añadir sistema de plugins

---

## Contribución

Las contribuciones son bienvenidas. Por favor, abre un issue primero para discutir los cambios propuestos.

---

## Licencia

Este proyecto está licenciado bajo la Licencia GNU - ver el archivo [LICENSE](LICENSE) para más detalles.