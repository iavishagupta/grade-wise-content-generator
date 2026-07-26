from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agents import pipeline

app = FastAPI(title="Agent-Based Content Pipeline")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    grade: int
    topic: str


@app.post("/generate")
def generate(req: GenerateRequest):
    try:
        result = pipeline(req.grade, req.topic)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return result


@app.get("/health")
def health():
    return {"status": "ok"}
