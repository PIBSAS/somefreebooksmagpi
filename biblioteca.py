import os
import shutil
import json
import io
from urllib.parse import quote, unquote
import fitz
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.getcwd()
DOCS_DIR = os.path.join(BASE_DIR, "docs")
PDF_DIR = BASE_DIR  # carpeta con tus PDFs
ANCHO = 332
ALTO = 443

# --- Crear carpetas necesarias ---
os.makedirs(DOCS_DIR, exist_ok=True)
STATIC_DIR = os.path.join(DOCS_DIR, "static")
os.makedirs(STATIC_DIR, exist_ok=True)

# --- Funciones ---
def buscar_pdfs_recursivo(base_dir):
    pdfs = []
    for root, _, files in os.walk(base_dir):
        if 'docs' in root.split(os.sep):
            continue
        for f in files:
            if f.lower().endswith(".pdf"):
                carpeta_relativa = os.path.relpath(root, base_dir)
                if carpeta_relativa == ".":
                    carpeta_relativa = "."
                else:
                    carpeta_relativa = carpeta_relativa.replace("\\", "/")
                pdfs.append((os.path.join(root, f), carpeta_relativa, f))
    return pdfs

def crear_logo_pdf(ruta_salida):
    img = Image.new("RGB", (256, 256), (220, 20, 60))
    draw = ImageDraw.Draw(img)
    try:
        fuente = ImageFont.truetype("arialbd.ttf", size=100)
    except:
        fuente = ImageFont.load_default()
    texto = "PDF"
    bbox = draw.textbbox((0,0), texto, font=fuente)
    posicion = ((256-(bbox[2]-bbox[0])//2), (256-(bbox[3]-bbox[1])//2))
    draw.text(posicion, texto, fill=(255,255,255), font=fuente)
    img.save(ruta_salida, "WEBP")

def crear_favicon():
    ruta_logo = os.path.join(STATIC_DIR, "logo.webp")
    ruta_fav = os.path.join(STATIC_DIR, "favicon.ico")
    img = Image.open(ruta_logo).convert("RGBA")
    img = img.resize((64,64), Image.LANCZOS)
    img.save(ruta_fav, format="ICO")

def crear_manifest():
    manifest = {
        "name": "Mi Web App PDF",
        "short_name": "PDFApp",
        "start_url": "./",
        "display": "standalone",
        "background_color": "#dc143c",
        "theme_color": "#dc143c",
        "description": "Visualizador de PDFs con miniaturas",
        "icons": [
            {"src": "/static/logo.webp", "sizes": "256x256", "type": "image/webp"},
            {"src": "/static/favicon.ico", "sizes": "64x64 32x32 24x24 16x16", "type": "image/x-icon"}
        ]
    }
    ruta = os.path.join(STATIC_DIR, "site.webmanifest")
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4)

def crear_service_worker(pdfs):
    urls = ["./", "/static/logo.webp", "/static/favicon.ico", "/static/site.webmanifest"]
    for ruta_pdf, carpeta, archivo in pdfs:
        base = os.path.splitext(archivo)[0]
        miniatura = f"/{carpeta}/{base}.webp" if carpeta!="." else f"/{base}.webp"
        pdf_url = f"/{carpeta}/{archivo}" if carpeta!="." else f"/{archivo}"
        urls.append(pdf_url)
        urls.append(miniatura)
    contenido = f"""
const CACHE_NAME = "revistas-cache-v1";
const urlsToCache = {urls};

self.addEventListener("install", event => {{
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(urlsToCache))
  );
}});

self.addEventListener("fetch", event => {{
  event.respondWith(
    caches.match(event.request).then(response => response || fetch(event.request).catch(() => new Response("No hay conexión y el recurso no está en caché.", {{
      headers: {{ "Content-Type": "text/plain" }}
    }})))
  );
}});
"""
    ruta_sw = os.path.join(STATIC_DIR, "service-worker.js")
    with open(ruta_sw, "w", encoding="utf-8") as f:
        f.write(contenido.strip())

def extraer_miniaturas(pdfs):
    for ruta_pdf, carpeta, archivo in pdfs:
        base = os.path.splitext(archivo)[0]
        salida_carpeta = os.path.join(DOCS_DIR, carpeta)
        os.makedirs(salida_carpeta, exist_ok=True)
        salida_miniatura = os.path.join(salida_carpeta, base+".webp")
        if os.path.exists(salida_miniatura):
            continue
        try:
            with fitz.open(ruta_pdf) as doc:
                pagina = doc[0]
                pix = pagina.get_pixmap(matrix=fitz.Matrix(300/72,300/72))
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                img_red = img.resize((ANCHO, ALTO), Image.LANCZOS)
                img_red.save(salida_miniatura, "WEBP", quality=80, lossless=True)
        except Exception as e:
            print(f"Error en {archivo}: {e}")

def generar_html(pdfs):
    from collections import defaultdict
    pdfs_por_carpeta = defaultdict(list)
    for ruta, carpeta, archivo in pdfs:
        carpeta_cod = quote(carpeta) if carpeta!="." else "."
        archivo_cod = quote(archivo)
        pdfs_por_carpeta[carpeta_cod].append((archivo_cod, archivo))

    html = "<!DOCTYPE html><html lang='es'><head><meta charset='UTF-8'><title>PDF Web</title>"
    html += "<link rel='icon' href='static/favicon.ico'><link rel='manifest' href='static/site.webmanifest'>"
    html += "<script>if('serviceWorker'in navigator){window.addEventListener('load',()=>navigator.serviceWorker.register('static/service-worker.js'))}</script>"
    html += "<style>body{font-family:Arial,sans-serif;} .pdfs-container{display:grid;gap:20px;}</style></head><body>"
    for carpeta, archivos in pdfs_por_carpeta.items():
        html += f"<h2>{unquote(carpeta)}</h2><div class='pdfs-container'>"
        for archivo_cod, nombre in archivos:
            base = os.path.splitext(nombre)[0]
            ruta_miniatura = f"{carpeta}/{base}.webp" if carpeta!="." else f"{base}.webp"
            ruta_pdf = f"{carpeta}/{archivo_cod}" if carpeta!="." else archivo_cod
            html += f"<div><img src='{ruta_miniatura}' width='200' onclick=\"window.open('{ruta_pdf}','_blank')\"><p>{base}</p></div>"
        html += "</div>"
    html += "</body></html>"
    ruta_index = os.path.join(DOCS_DIR, "index.html")
    with open(ruta_index, "w", encoding="utf-8") as f:
        f.write(html)

# --- Ejecución ---
pdf_files = buscar_pdfs_recursivo(PDF_DIR)
extraer_miniaturas(pdf_files)
crear_logo_pdf(os.path.join(STATIC_DIR, "logo.webp"))
crear_favicon()
crear_manifest()
crear_service_worker(pdf_files)
generar_html(pdf_files)

print("✅ Sitio PWA estático generado en 'docs/' listo para GitHub Pages.")
