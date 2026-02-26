import requests
import os
import random
from PIL import Image, ImageStat
import time
from pages import pages_repository

# --- CONFIGURACIÓN ---
PAGE_ID = ""
page = pages_repository.get_by_id(PAGE_ID)

INPUT_FOLDER = './.data/ss/input_pictures'
DEBUG_FOLDER = './.data/ss/processed_pictures'

TARGET_RES = (1080, 1920)

# --- NUEVOS PARÁMETROS ---
NUM_IMAGENES_A_PUBLICAR = 3  # Cantidad de imágenes por ejecución
DELAY_DEFAULT = 30            # Segundos entre cada publicación

os.makedirs(DEBUG_FOLDER, exist_ok=True)

def get_page_token(user_token, page_id):
    url = f"https://graph.facebook.com/v21.0/{page_id}?fields=access_token&access_token={user_token}"
    r = requests.get(url).json()
    return r.get('access_token')

def get_dominant_color(image):
    stat = ImageStat.Stat(image)
    return tuple(int(c) for c in stat.mean)

def preprocess_image(image_path):
    with Image.open(image_path) as img:
        if img.mode in ("RGBA", "P"): img = img.convert("RGB")
        
        original_width, original_height = img.size
        aspect_ratio = original_height / original_width
        
        new_width = TARGET_RES[0]
        new_height = int(new_width * aspect_ratio)
        img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        bg_color = get_dominant_color(img)
        canvas = Image.new('RGB', TARGET_RES, bg_color)
        
        y_offset = (TARGET_RES[1] - new_height) // 2
        canvas.paste(img_resized, (0, y_offset))
        
        file_name = os.path.basename(image_path)
        debug_path = os.path.join(DEBUG_FOLDER, f"proc_{file_name}")
        canvas.save(debug_path, "JPEG", quality=90)
        return debug_path

def my_fn(page_id, token, img_path):
    upload_url = f"https://graph.facebook.com/v21.0/{page_id}/photos"
    payload = {'access_token': token, 'published': 'false'}
    
    try:
        with open(img_path, 'rb') as img:
            files = {'source': img}
            response = requests.post(upload_url, data=payload, files=files)
            res_data = response.json()
            
        if 'id' not in res_data:
            print(f"   ❌ Error en subida: {res_data}")
            return False

        photo_id = res_data['id']
        story_url = f"https://graph.facebook.com/v21.0/{page_id}/photo_stories"
        story_payload = {'photo_id': photo_id, 'access_token': token}
        
        publish_res = requests.post(story_url, data=story_payload)
        result = publish_res.json()
        
        if result.get('success'):
            print(f"   ✅ Story publicada con éxito! ID: {photo_id}")
            return True
        else:
            print(f"   ❌ Error al publicar story: {result}")
            return False
    except Exception as e:
        print(f"   💥 Ocurrió un error: {e}")
        return False

def obtener_todas_las_fotos(directorio):
    """Busca imágenes en el directorio y todas sus subcarpetas."""
    extensiones = ('.jpg', '.png', '.jpeg')
    lista_fotos = []
    for root, dirs, files in os.walk(directorio):
        for file in files:
            if file.lower().endswith(extensiones):
                lista_fotos.append(os.path.join(root, file))
    return lista_fotos

def main():
    todas_las_fotos = obtener_todas_las_fotos(INPUT_FOLDER)
    
    if not todas_las_fotos:
        return print("Carpeta vacía o sin imágenes compatibles.")

    # Seleccionar lote aleatorio
    cantidad = min(len(todas_las_fotos), NUM_IMAGENES_A_PUBLICAR)
    lote = random.sample(todas_las_fotos, cantidad)
    
    print(f"📂 Encontradas {len(todas_las_fotos)} fotos. Iniciando lote de {cantidad}...")

    for i, foto_path in enumerate(lote):
        print(f"\n📸 [{i+1}/{cantidad}] Procesando: {os.path.basename(foto_path)}")
        ruta_procesada = preprocess_image(foto_path)
        
        token_pagina = page.access_token
        
        if token_pagina:
            print(f"   🚀 Publicando en: {page.name}...")
            my_fn(page.id, token_pagina, ruta_procesada)
        else:
            print(f"   ⚠️ No se pudo obtener token para {page['nombre']}")

        # Delay entre imágenes del lote (no se aplica en la última)
        if i < cantidad - 1:
            print(f"⏳ Esperando {DELAY_DEFAULT} segundos para la siguiente...")
            time.sleep(DELAY_DEFAULT)

    print("\n✨ Proceso de lote finalizado.")

if __name__ == "__main__":
    main()