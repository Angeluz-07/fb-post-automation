from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import json

BASE_DIR = Path(__file__).resolve().parent.parent
SECRETS_FILE_PATH = BASE_DIR / '.secrets.json'

@dataclass
class Page:
    name: str
    id: str
    access_token: str
    
    def __str__(self):
        return f'Page(name={self.name}, id={self.id})'

class PagesRepo:
    def __init__(self, file_path: str = SECRETS_FILE_PATH):
        self.file_path = Path(file_path)

    def _read_all(self) -> List[dict]:
        with open(self.file_path, 'r') as f:
            return json.load(f)
        
    def get_all(self) -> List[Page]:
        data = self._read_all()
        return [self._map_to_entity(item) for item in data]
    
    def _map_to_entity(self, data: dict) -> Page:
        """Helper to reconstruct the objects from a dictionary."""
        return Page(
            name=data['name'],
            access_token=data['access_token'],
            id=data['id']
        )

    def get_by_id(self, id: str) -> Optional[Page]:
        data = self._read_all()
        item = next((x for x in data if x["id"] == id), None)
        return self._map_to_entity(item) if item else None

print(PagesRepo().get_by_id("101349552584924"))