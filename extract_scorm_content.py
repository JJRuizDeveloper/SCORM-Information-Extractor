# Autor: @JJRuizDeveloper
# Título: Extractor de información SCORM
# Requerimientos: pip install beautifulsoup4

''' 
Descripción: Dada una ruta al archivo .zip del SCORM, este script extrae los datos 
de dicho SCORM y entrega un JSON legible con su información para que pueda ser
procesdado.
'''

import os
import zipfile
import tempfile
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import json

# 1. Extrae el zip del SCORM
def extract_scorm(zip_path):
    temp_dir = tempfile.mkdtemp()
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    return temp_dir

# 2. Parsea el imsmanifest.xml
def parse_manifest(scorm_folder):
    manifest_path = os.path.join(scorm_folder, 'imsmanifest.xml')
    tree = ET.parse(manifest_path)
    root = tree.getroot()

    # Namespace general (puede variar, a veces no hay namespace)
    ns = {'ns': root.tag.split('}')[0].strip('{')}

    # Título del curso
    title_elem = root.find(".//ns:organization/ns:title", ns)
    course_title = title_elem.text if title_elem is not None else "Curso sin título"

    sco_items = []
    for item in root.findall(".//ns:organization/ns:item", ns):
        sco_title_elem = item.find("ns:title", ns)
        sco_title = sco_title_elem.text if sco_title_elem is not None else "Sin título"

        identifierref = item.attrib.get("identifierref")
        href = None

        if identifierref:
            resource = root.find(f".//ns:resource[@identifier='{identifierref}']", ns)
            href = resource.attrib.get("href") if resource is not None else None

        sco_items.append({
            "title": sco_title,
            "resource_href": href
        })

    return course_title, sco_items

# 3. Extrae texto visible desde archivos HTML
def extract_html_content(html_path):
    try:
        with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
            soup = BeautifulSoup(f, 'html.parser')
            for tag in soup(['script', 'style', 'nav']):
                tag.decompose()
            return soup.get_text(separator=' ', strip=True)
    except Exception as e:
        return f"[Error al leer HTML: {e}]"

# 4. Construye el JSON estructurado
def build_scorm_json(zip_path):
    scorm_dir = extract_scorm(zip_path)
    course_title, sco_items = parse_manifest(scorm_dir)

    topics = []
    for sco in sco_items:
        content_text = ""
        if sco['resource_href']:
            html_path = os.path.join(scorm_dir, sco['resource_href'])
            if os.path.exists(html_path):
                content_text = extract_html_content(html_path)
        topics.append({
            "title": sco['title'],
            "text": content_text,
            "resource_href": sco['resource_href']
        })

    return {
        "course_title": course_title,
        "topics": topics
    }

# 5. Uso principal
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extrae contenido de un paquete SCORM")
    parser.add_argument("scorm_zip", help="Ruta al archivo .zip del SCORM")
    parser.add_argument("--output", help="Ruta para guardar el JSON de salida", default="scorm_content.json")
    args = parser.parse_args()

    result = build_scorm_json(args.scorm_zip)

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Contenido extraído y guardado en {args.output}")
