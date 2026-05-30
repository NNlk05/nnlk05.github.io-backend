from os import environ
from pathlib import Path
from typing import Any, Dict, List, Optional, TypeVar
import firebase_admin
from firebase_admin import credentials, firestore

T = TypeVar('T')

class DB:
    def __init__(self) -> None:
        self._load_env_file()
        self._initialize_firebase()
        self.db = firestore.client()

    def _load_env_file(self) -> None:
        env_path: Path = Path('.env')
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    clean_line: str = line.strip()
                    if not clean_line or clean_line.startswith('#'):
                        continue
                    if '=' in clean_line:
                        key, value = clean_line.split('=', 1)
                        environ[key.strip()] = value.strip().strip("'\"")

    def _initialize_firebase(self) -> None:
        if not firebase_admin._apps:
            key_path: str = environ.get('FIREBASE_KEY_PATH', '')
            cred: credentials.Certificate = credentials.Certificate(key_path)
            firebase_admin.initialize_app(cred)

    def create_collection(self, name: str) -> None:
        pass

    def insert(self, collection: str, document: Dict[str, Any]) -> int:
        doc_id: str = str(document.get('id', ''))
        if not doc_id:
            return 0
        self.db.collection(collection).document(doc_id).set(document)
        return 1

    def find_one(self, collection: str, **filters: Any) -> Optional[Dict[str, Any]]:
        doc_id: str = str(filters.get('id', ''))
        if doc_id:
            doc = self.db.collection(collection).document(doc_id).get()
            return doc.to_dict() if doc.exists else None

        query = self.db.collection(collection)
        for key, value in filters.items():
            query = query.where(key, '==', value)
        
        docs: list = list(query.limit(1).stream())
        return docs[0].to_dict() if docs else None

    def find_all(self, collection: str) -> List[Dict[str, Any]]:
        return [doc.to_dict() for doc in self.db.collection(collection).stream()]

    def find(self, collection: str, **filters: Any) -> List[Dict[str, Any]]:
        query = self.db.collection(collection)
        for key, value in filters.items():
            query = query.where(key, '==', value)
        return [doc.to_dict() for doc in query.stream()]

    def update(self, collection: str, filters: Dict[str, Any], update_data: Dict[str, Any]) -> int:
        doc: Optional[Dict[str, Any]] = self.find_one(collection, **filters)
        if not doc:
            return 0
        doc_id: str = str(doc.get('id', ''))
        self.db.collection(collection).document(doc_id).set(update_data, merge=True)
        return 1

    def delete(self, collection: str, **filters: Any) -> int:
        doc: Optional[Dict[str, Any]] = self.find_one(collection, **filters)
        if not doc:
            return 0
        doc_id: str = str(doc.get('id', ''))
        self.db.collection(collection).document(doc_id).delete()
        return 1