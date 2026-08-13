# Editor Markdown Avanzado

> Un editor de Markdown bello y moderno hecho con PyQt5.
>
> **Vista previa en vivo.**  
> **Interfaz inspirada y cuidada.**  
> **Soporte para tablas, código, impresión y más.**

---

## Características principales

- **Vista previa estilizada** en tiempo real del Markdown.
- **Contador de palabras y caracteres.**
- **Botones rápidos**: Nuevo, Abrir, Guardar, Guardar Como, Imprimir, Acerca de.
- **Diseño atractivo** con esquemas de color modernos.
- **Soporte extendido** para tablas, bloques de código, resaltado, enlaces y más.
- Diálogo para **Acerca de** integrado.
- **Atajos de teclado** estándar por el sistema operativo.
- **Corrección de errores** frecuentes y mejoras continuas basadas en feedback.

---

## Uso rápido

1. Asegúrate de tener **Python >=3.6** y **PyQt5** y **markdown** instalados:

   ```bash
   pip install PyQt5 markdown
   ```

2. Descarga los archivos (`mdeditor.py` y la carpeta `app` con el ícono opcional).

3. Ejecuta:

   ```bash
   python mdeditor.py
   ```

---

## Archivos

- `mdeditor.py` — código fuente principal del editor.
- `app/app-icon.ico` — ícono usado en la ventana (opcional).

---

## Captura de pantalla

![Editor Markdown Avanzado screenshot](./screenshot.png)

---

## Créditos

Desarrollado con 🧡 usando [PyQt5](https://riverbankcomputing.com/software/pyqt/).

---

## Historial y corrección de errores

- Versión actual: varias correcciones de bugs menores de formato y estabilidad.
- Cada versión incorpora revisiones basadas en reportes de usuarios y pruebas manuales.

---


## Clasificación y compatibilidad

Este proyecto se clasifica como **AlphaCube** porque su código fuente está preparado para ejecutarse en al menos dos sistemas operativos: **Linux y Windows**. Utiliza PyQt6 y Python-Markdown, sin depender de `sudo`, rutas exclusivas de Linux ni APIs exclusivas de Windows. En Windows, los lanzadores no ejecutan comandos privilegiados; en Linux, la aplicación tampoco necesita privilegios de administrador para abrir o guardar documentos del usuario.

La migración a PyQt6 incluye los enums modernos de Qt, `QAction` desde `PyQt6.QtGui`, `QDialog.exec()` para impresión y `QApplication.exec()` como entrypoint. La dependencia obsoleta `pyqt5-tools` fue eliminada de `lib/requirements.txt`.

## Instalación reproducible

Se requiere Python 3.8 o posterior. Desde la raíz del proyecto, instala las dependencias con:

```bash
python -m pip install -r lib/requirements.txt
python mdeditor.py
```

En Windows se recomienda un entorno virtual:

```powershell
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r lib/requirements.txt
py mdeditor.py
```

En Linux puede utilizarse:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r lib/requirements.txt
python mdeditor.py
```

## Pruebas automatizadas

Para entornos sin pantalla, Qt puede ejecutarse en modo offscreen:

```bash
QT_QPA_PLATFORM=offscreen python static_functional_check.py
QT_QPA_PLATFORM=offscreen python pyqt6_smoke_test.py
python -m py_compile mdeditor.py static_functional_check.py pyqt6_smoke_test.py
```

`static_functional_check.py` valida la sintaxis, los imports de PyQt6, la clasificación AlphaCube, las dependencias y la ausencia de APIs PyQt5 o entrypoints `exec_()`. `pyqt6_smoke_test.py` crea la ventana, procesa encabezados, negrita y listas Markdown, comprueba la vista previa HTML y verifica el contador de palabras.

## Estructura requerida por PackageMaker

La estructura del proyecto se revisa con **MoonFix**, que restaura los archivos auxiliares faltantes sin sobrescribir el script principal existente. Estos componentes forman parte del contrato del paquete `.iflapp`:

| Archivo o carpeta | Propósito |
| --- | --- |
| `details.xml` | Metadatos del publisher, aplicación, versión, autor, plataforma y correlación. |
| `config/settings.json` | Configuración serializada utilizada por PackageMaker. |
| `manifest.res` | Recurso de manifiesto requerido para AlphaCube y Windows. |
| `version.res` | Recursos de versión para el artefacto compilado. |
| `autorun` | Lanzador para sistemas Unix-like. |
| `autorun.bat` | Lanzador para Windows; no utiliza `sudo`. |
| `updater.py` | Integración del actualizador del formato PackageMaker. |
| `.storedetail` | Correlación de almacenamiento del paquete. |
| `app/`, `assets/`, `config/`, `docs/`, `lib/`, `source/` | Carpetas estructurales con sus marcadores `.container`. |

MoonFix debe ejecutarse sobre una copia aislada o sobre el proyecto seleccionado explícitamente. Su resultado se debe revisar antes del commit. Los archivos `.res`, lanzadores, actualizador, documentación y marcadores no deben eliminarse al preparar un release.

## Convención de versión y publicación

El nombre interno completo del paquete conserva el formato de PackageMaker:

```text
publisher.appname.v(version)-(yy.mm-hh.mm)-platform
```

Para GitHub, el **tag y el título del release deben contener únicamente la versión**, por ejemplo `v2.0.0`; no deben incluir el nombre del proyecto, la hora ni la plataforma. El release solo debe publicarse después de comprobar que el `.iflapp` contiene el código fuente o los binarios esperados, `details.xml`, `manifest.res`, `version.res`, los lanzadores, `config/settings.json` y todos los marcadores estructurales.

## Archivos de auditoría

- `mdeditor.py`: implementación principal del editor PyQt6.
- `lib/requirements.txt`: dependencias reproducibles de PyQt6 y Markdown.
- `details.xml` y `config/settings.json`: metadatos normalizados por MoonFix.
- `manifest.res` y `version.res`: recursos requeridos por PackageMaker.
- `static_functional_check.py`: auditoría estática.
- `pyqt6_smoke_test.py`: smoke test funcional en modo offscreen.
- `app/app-icon.ico`: icono de la aplicación.
