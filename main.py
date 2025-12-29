from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import sqlite3
import string
import random

app = FastAPI(title="Encurtador de URL Pro")

# --- BANCO DE DADOS (Configuração Simples) ---
def init_db():
    conn = sqlite3.connect("urls.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS urls 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, original TEXT, short TEXT UNIQUE)
    """)
    conn.commit()
    conn.close()

init_db()

# --- LÓGICA DE GERAÇÃO DE CÓDIGO ---
def gerar_codigo():
    caracteres = string.ascii_letters + string.digits
    return ''.join(random.choice(caracteres) for _ in range(6))

# --- MODELO DE DADOS ---
class URLRequest(BaseModel):
    url_original: str

# --- ROTAS (API) ---

@app.post("/encurtar")
def encurtar(request: URLRequest):
    codigo = gerar_codigo()
    
    conn = sqlite3.connect("urls.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO urls (original, short) VALUES (?, ?)", (request.url_original, codigo))
        conn.commit()
    except:
        raise HTTPException(status_code=500, detail="Erro ao salvar no banco")
    finally:
        conn.close()
        
    return {"url_encurtada": f"http://localhost:8000/{codigo}"}

@app.get("/{codigo}")
def redirecionar(codigo: str):
    conn = sqlite3.connect("urls.db")
    cursor = conn.cursor()
    cursor.execute("SELECT original FROM urls WHERE short = ?", (codigo,))
    resultado = cursor.fetchone()
    conn.close()
    
    if resultado:
        return RedirectResponse(url=resultado[0])
    raise HTTPException(status_code=404, detail="URL não encontrada")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
