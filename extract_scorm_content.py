import os
import zipfile
import tempfile
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import json

def extract_scorm(zip_path):
    """Extrae el ZIP SCORM a un directorio temporal"""
    temp_dir = tempfile.mkdtemp()
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
    except Exception as e:
        raise RuntimeError(f"Error extrayendo SCORM: {e}")
    return temp_dir

def parse_manifest(scorm_folder):
    """Lee imsmanifest.xml y obtiene título y recursos asociados"""
    manifest_path = os.path.join(scorm_folder, 'imsmanifest.xml')
    if not os.path.exists(manifest_path):
        raise FileNotFoundError("imsmanifest.xml no encontrado")

    try:
        tree = ET.parse(manifest_path)
    except ET.ParseError as e:
        raise RuntimeError(f"imsmanifest.xml corrupto: {e}")

    root = tree.getroot()

    # Manejo flexible de namespaces
    ns = {}
    if '}' in root.tag:
        ns['ns'] = root.tag.split('}')[0].strip('{')

    def find(elem, path):
        return elem.find(path, ns) if ns else elem.find(path)

    def findall(elem, path):
        return elem.findall(path, ns) if ns else elem.findall(path)

    # Título del curso
    title_elem = find(root, ".//ns:organization/ns:title") if ns else root.find(".//organization/title")
    course_title = title_elem.text.strip() if title_elem is not None and title_elem.text else "Curso sin título"

    sco_items = []
    for item in findall(root, ".//ns:organization//ns:item") if ns else root.findall(".//organization//item"):
        sco_title_elem = find(item, "ns:title") if ns else item.find("title")
        sco_title = sco_title_elem.text.strip() if sco_title_elem is not None and sco_title_elem.text else "Sin título"

        identifierref = item.attrib.get("identifierref")
        resources = []

        if identifierref:
            resource_elem = find(root, f".//ns:resource[@identifier='{identifierref}']") if ns else root.find(f".//resource[@identifier='{identifierref}']")
            if resource_elem is not None:
                # href principal
                href = resource_elem.attrib.get("href")
                if href:
                    resources.append(href)
                # todos los <file>
                for file_elem in findall(resource_elem, ".//ns:file") if ns else resource_elem.findall(".//file"):
                    file_href = file_elem.attrib.get("href")
                    if file_href and file_href not in resources:
                        resources.append(file_href)

        sco_items.append({
            "title": sco_title,
            "resources": resources
        })

    return course_title, sco_items

def extract_html_content(html_path):
    """Extrae texto y HTML de un archivo"""
    try:
        with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
            soup = BeautifulSoup(f, 'lxml')
            for tag in soup(['script', 'style', 'nav']):
                tag.decompose()
            return {
                "text": soup.get_text(separator=' ', strip=True),
                "html": str(soup)
            }
    except Exception as e:
        return {
            "text": f"[Error al leer HTML: {e}]",
            "html": ""
        }

def build_scorm_json(zip_path):
    scorm_dir = extract_scorm(zip_path)
    course_title, sco_items = parse_manifest(scorm_dir)

    topics = []
    for sco in sco_items:
        content_blocks = []
        for res in sco['resources']:
            abs_path = os.path.join(scorm_dir, res)
            if os.path.exists(abs_path) and res.lower().endswith(('.html', '.htm')):
                html_data = extract_html_content(abs_path)
                content_blocks.append({
                    "file": res,
                    "text": html_data["text"],
                    "html": html_data["html"]
                })
            else:
                # Archivo no HTML o inexistente: lo anotamos igual
                content_blocks.append({
                    "file": res,
                    "text": "",
                    "html": "",
                    "note": "No es HTML o no existe en el paquete"
                })

        topics.append({
            "title": sco['title'],
            "resources": sco['resources'],
            "contents": content_blocks
        })

    return {
        "course_title": course_title,
        "topics": topics
    }

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extractor robusto de contenido SCORM")
    parser.add_argument("scorm_zip", help="Ruta al archivo .zip del SCORM")
    parser.add_argument("--output", help="Ruta para guardar el JSON", default="scorm_content.json")
    args = parser.parse_args()

    try:
        result = build_scorm_json(args.scorm_zip)
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"Contenido extraído y guardado en {args.output}")
    except Exception as e:
        print(f"Error: {e}")
