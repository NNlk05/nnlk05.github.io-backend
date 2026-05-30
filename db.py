import json
from pathlib import Path
from typing import Any, Dict, List, Optional, TypeVar

T = TypeVar('T')

class DB:
    def __init__(self, filepath: str | Path) -> None:
        self.filepath: Path = Path(filepath)
        self.data: Dict[str, List[Dict[str, Any]]] = {}
        self._load()
    
    def _load(self) -> None:
        if self.filepath.exists():
            with open(self.filepath, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {}
    
    def _dump(self) -> None:
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(self.filepath, 'w') as f:
            json.dump(self.data, f, indent=2, default=str)
    
    def create_collection(self, name: str) -> None:
        if name not in self.data:
            self.data[name] = []
            self._dump()
    
    def insert(self, collection: str, document: Dict[str, Any]) -> int:
        if collection not in self.data:
            self.create_collection(collection)
        
        doc_id: int = max([d.get('_id', 0) for d in self.data[collection]], default=0) + 1
        document['_id'] = doc_id
        self.data[collection].append(document)
        self._dump()
        return doc_id
    
    def find(self, collection: str, **filters: Any) -> List[Dict[str, Any]]:
        if collection not in self.data:
            return []
        
        return [
            doc for doc in self.data[collection]
            if all(doc.get(k) == v for k, v in filters.items())
        ]
    
    def find_one(self, collection: str, **filters: Any) -> Optional[Dict[str, Any]]:
        results = self.find(collection, **filters)
        return results[0] if results else None
    
    def find_all(self, collection: str) -> List[Dict[str, Any]]:
        return self.data.get(collection, []).copy()
    
    def update(self, collection: str, filters: Dict[str, Any], update: Dict[str, Any]) -> int:
        if collection not in self.data:
            return 0
        
        count: int = 0
        for doc in self.data[collection]:
            if all(doc.get(k) == v for k, v in filters.items()):
                doc.update(update)
                count += 1
        
        if count > 0:
            self._dump()
        return count
    
    def delete(self, collection: str, **filters: Any) -> int:
        if collection not in self.data:
            return 0
        
        initial_len: int = len(self.data[collection])
        self.data[collection] = [
            doc for doc in self.data[collection]
            if not all(doc.get(k) == v for k, v in filters.items())
        ]
        
        deleted: int = initial_len - len(self.data[collection])
        if deleted > 0:
            self._dump()
        return deleted
