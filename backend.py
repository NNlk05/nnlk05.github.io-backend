from db import DB
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from pathlib import Path

app = FastAPI()
db = DB(Path('documents.json'))

class EditorDocument(BaseModel):
    id: str
    content: str

class DocumentResponse(BaseModel):
    id: str
    content: str

@app.post('/documents')
def create_document(document: EditorDocument) -> DocumentResponse:
    db.create_collection('documents')
    doc_id = db.insert('documents', {
        'id': document.id,
        'content': document.content
    })
    return DocumentResponse(id=document.id, content=document.content)

@app.get('/documents/{document_id}')
def get_document(document_id: str) -> DocumentResponse:
    doc = db.find_one('documents', id=document_id)
    if not doc:
        raise HTTPException(status_code=404, detail='Document not found')
    return DocumentResponse(id=doc['id'], content=doc['content'])

def main() -> None:
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)

if __name__ == '__main__':
    main()
