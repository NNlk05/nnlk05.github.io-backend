from .db import DB
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from os import environ

app: FastAPI = FastAPI()

print(repr(environ.get("FIREBASE_CREDENTIALS_JSON", "")))

db: DB = DB()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://nnlk05.github.io"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EditorDocument(BaseModel):
    id: str
    content: str

class DocumentResponse(BaseModel):
    id: str
    content: str

@app.get("/")
def root():
    return {"status": "ok"}

@app.post('/documents')
def create_document(document: EditorDocument) -> DocumentResponse:
    db.create_collection('documents')
    db.insert('documents', {
        'id': document.id,
        'content': document.content
    })
    return DocumentResponse(id=document.id, content=document.content)

@app.get('/documents/{document_id}')
def get_document(document_id: str) -> DocumentResponse:
    doc: dict | None = db.find_one('documents', id=document_id)
    if not doc:
        raise HTTPException(status_code=404, detail='Document not found')
    return DocumentResponse(id=doc['id'], content=doc['content'])

def main() -> None:
    import uvicorn

    production: bool = environ.get('PRODUCTION', 'false').lower() == 'true'
    if production:
        uvicorn.run('index:app', host='0.0.0.0', port=8000, workers=4)
    else:
        uvicorn.run('index:app', host='0.0.0.0', port=8000, reload=True)

if __name__ == '__main__':
    main()