import requests
import os
import random
from PIL import Image, ImageStat
import time
from pages import pages_repository, get_stories_input_folder, get_stories_output_folder

TARGET_RES = (1080, 1920)

# --- NUEVOS PARÁMETROS ---
NUM_IMAGENES_A_PUBLICAR = 3  # Cantidad de imágenes por ejecución
DELAY_DEFAULT = 30            # Segundos entre cada publicación


def get_page_token(user_token, page_id):
    url = f"https://graph.facebook.com/v21.0/{page_id}?fields=access_token&access_token={user_token}"
    r = requests.get(url).json()
    return r.get('access_token')

def get_dominant_color(image):
    stat = ImageStat.Stat(image)
    return tuple(int(c) for c in stat.mean)

def preprocess_image(image_path, debug_folder):
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
        debug_path = os.path.join(debug_folder, f"proc_{file_name}")
        canvas.save(debug_path, "JPEG", quality=90)
        return debug_path

def _publish_story(page_id, token, img_path):
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

def get_all_pictures(directorio):
    """Busca imágenes en el directorio y todas sus subcarpetas."""
    extensiones = ('.jpg', '.png', '.jpeg')
    lista_fotos = []
    for root, dirs, files in os.walk(directorio):
        for file in files:
            if file.lower().endswith(extensiones):
                lista_fotos.append(os.path.join(root, file))
    return lista_fotos

def main():
    for page in pages_repository.get_all():
        input_folder = get_stories_input_folder(page.stories_folder)
        debug_folder = get_stories_output_folder(page.stories_folder)
        os.makedirs(debug_folder, exist_ok=True)

        pictures_pool = get_all_pictures(input_folder)

        if not pictures_pool:
            return print("Carpeta vacía o sin imágenes compatibles.")

        # Seleccionar lote aleatorio
        cantidad = min(len(pictures_pool), NUM_IMAGENES_A_PUBLICAR)
        lote = random.sample(pictures_pool, cantidad)
    
        print(f"📂 Encontradas {len(pictures_pool)} fotos. Iniciando lote de {cantidad}...")

        for i, foto_path in enumerate(lote):
            print(f"\n📸 [{i+1}/{cantidad}] Procesando: {os.path.basename(foto_path)}")
            ruta_procesada = preprocess_image(foto_path, debug_folder)
            
            token_pagina = page.access_token
            
            if token_pagina:
                print(f"   🚀 Publicando en: {page.name}...")
                _publish_story(page.id, token_pagina, ruta_procesada)
            else:
                print(f"   ⚠️ No se pudo obtener token para {page['nombre']}")

            # Delay entre imágenes del lote (no se aplica en la última)
            if i < cantidad - 1:
                print(f"⏳ Esperando {DELAY_DEFAULT} segundos para la siguiente...")
                time.sleep(DELAY_DEFAULT)

        print(f"\n✨ Proceso de lote finalizado. for page {page.name}")

if __name__ == "__main__":
    main()