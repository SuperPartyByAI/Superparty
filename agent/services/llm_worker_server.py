from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests, uvicorn
from agent.common.env import getenv

app = FastAPI()
OLLAMA_URL = getenv("OLLAMA_URL","http://localhost:11434")
DEFAULT_MODEL = getenv("LLM_MODEL","llama3.2:3b")

class GenReq(BaseModel):
    prompt: str
    model: str = None

@app.get("/health")
def health(): return {"status":"ok","model":DEFAULT_MODEL}

@app.post("/generate")
def generate(req: GenReq):
    try:
        r=requests.post(f"{OLLAMA_URL}/api/generate",
                       json={"model":req.model or DEFAULT_MODEL,"prompt":req.prompt,"stream":False},timeout=120)
        r.raise_for_status(); return r.json()
    except Exception as e: raise HTTPException(500,str(e))

if __name__=="__main__": uvicorn.run(app,host="0.0.0.0",port=8100)
