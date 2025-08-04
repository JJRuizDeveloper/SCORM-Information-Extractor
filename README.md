# 📦 SCORM Information Extractor / Extractor de Información SCORM

## Autor / Author: @JJRuizDeveloper

---

## 🌐 English

### 📌 Description
This script extracts structured information from a SCORM `.zip` package and outputs a readable `JSON` file containing its content. It's useful for processing, analyzing, or visualizing SCORM course data.

### 🛠 Requirements
- Python 3.6+
- Install dependencies:
  pip install beautifulsoup4

### 🚀 Usage
  python scorm_extractor.py path/to/scorm.zip --output output_file.json

- path/to/scorm.zip: Path to the SCORM package.
- --output: (Optional) Path where the JSON will be saved. Defaults to scorm_content.json.

### 📄 Output Example
  {
    "course_title": "Sample Course",
    "topics": [
      {
        "title": "Introduction",
        "text": "Welcome to the course...",
        "resource_href": "index.html"
      }
    ]
  }

---

## 🇪🇸 Español

### 📌 Descripción
Este script extrae información estructurada desde un paquete SCORM en formato `.zip` y genera un archivo `JSON` legible con el contenido. Es útil para procesar, analizar o visualizar los datos de un curso SCORM.

### 🛠 Requisitos
- Python 3.6 o superior
- Instalar dependencias:
  pip install beautifulsoup4

### 🚀 Uso
  python scorm_extractor.py ruta/al/archivo.zip --output archivo_salida.json

- ruta/al/archivo.zip: Ruta al paquete SCORM.
- --output: (Opcional) Ruta donde se guardará el archivo JSON. Por defecto se guarda como scorm_content.json.

### 📄 Ejemplo de salida
  {
    "course_title": "Curso de Ejemplo",
    "topics": [
      {
        "title": "Introducción",
        "text": "Bienvenido al curso...",
        "resource_href": "index.html"
      }
    ]
  }

---

## 📬 Contact
For issues or suggestions, feel free to open an issue or contact the author via GitHub.
