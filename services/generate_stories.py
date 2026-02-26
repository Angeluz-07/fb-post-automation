import ollama
import json
import os
from datetime import datetime

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_CONFIG_PATH = BASE_DIR / ".data" / ".prompts_config.json"

@dataclass
class PromptConfig:
    system_content: str
    user_content: str
    id: str 
    name: str
    num_predict: int = 200


class PromptConfigRepo:
    def __init__(self, file_path: str = PROMPT_CONFIG_PATH):
        self.file_path = Path(file_path)

    def _read_all(self) -> List[dict]:
        with open(self.file_path, encoding='utf-8') as f:
            return json.load(f)
        
    def get_all(self) -> List[PromptConfig]:
        data = self._read_all()
        return [self._map_to_entity(item) for item in data]
    
    def _map_to_entity(self, data: dict) -> PromptConfig:
        """Helper to reconstruct the objects from a dictionary."""
        system = "\n".join(data['system_content'])
        user = "\n".join(data['user_content'])
        return PromptConfig(
            system_content=system,
            user_content=user,
            name=data["name"],
            id=data["id"],
            num_predict=data["num_predict"]
        )

    def get_by_id(self, id: str) -> Optional[PromptConfig]:
        data = self._read_all()
        item = next((x for x in data if x["id"] == id), None)
        return self._map_to_entity(item) if item else None

prompts_config_repository = PromptConfigRepo()

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