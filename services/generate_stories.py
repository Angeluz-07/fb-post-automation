import ollama
import json
import os
from datetime import datetime
from pathlib import Path

from prompt_config import PromptConfig, prompts_config_repository

MODELO = "gemma3:4b" # mas literario
#MODELO = "llama3.2:3b" # mas equilibrado

def generar_story(out_folder: str, prompt_config: PromptConfig):

    response = ollama.chat(
        model=MODELO,
        messages=[
            {'role': 'system', 'content': prompt_config.system_content},
            {'role': 'user', 'content': prompt_config.user_content},
        ],
        options={'num_predict': prompt_config.num_predict, 'temperature': 0.8}
    )

    # Limpieza: Eliminamos posibles espacios en blanco extras
    historia = response['message']['content'].strip()
    
    # Guardar solo la historia
    data = {
        "tema": prompt_config.name,
        "texto": historia,
        "conteo_palabras": len(historia.split())
    }

    filename = f"historia_{datetime.now().strftime('%H%M%S')}.json"
    out_file = Path(out_folder) / filename
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return f"Generada: {data['conteo_palabras']} palabras."

if __name__ == "__main__":
    prompt = prompts_config_repository.get_by_id("2")
    out_folder = '.data/prompts_out'
    os.makedirs(out_folder, exist_ok=True)
    generar_story(out_folder, prompt)