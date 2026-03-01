"""
Personal AI Assistant - Backend
Roda localmente com Ollama (Mistral) + Whisper + Coqui TTS
"""

import os
import json
import uuid
import tempfile
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
import httpx

from database import init_db, get_db_connection
from llm import chat_with_mistral, build_system_prompt
from voice import transcribe_audio, synthesize_speech, save_voice_sample, is_clone_enabled, set_clone_enabled

# ─── App Setup ────────────────────────────────────────────────────────────────

app = FastAPI(title="Personal AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
DATA_DIR = BASE_DIR / "data"
VOICES_DIR = BASE_DIR / "voices"

app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

# ─── Startup ──────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup():
    init_db()
    print("✅ Banco de dados inicializado")
    print("✅ Personal AI rodando em http://localhost:8000")

# ─── Models ───────────────────────────────────────────────────────────────────

class MessageRequest(BaseModel):
    session_id: str
    content: str
    use_voice: bool = False

class SessionCreate(BaseModel):
    name: str
    type: str = "general"  # "general" | "rotina"

class DailyLog(BaseModel):
    date: str
    energy: float
    focus: float
    study_hours: float
    questions_solved: int
    subjects: str
    did_well: str
    needs_improvement: str
    notes: Optional[str] = ""

class Decision(BaseModel):
    date: str
    type: str
    context: str
    choice: str
    result: str
    reason: str

# ─── Root ─────────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return FileResponse(str(FRONTEND_DIR / "index.html"))

# ─── Sessions ─────────────────────────────────────────────────────────────────

@app.get("/api/sessions")
async def get_sessions():
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM sessions ORDER BY updated_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]

@app.post("/api/sessions")
async def create_session(body: SessionCreate):
    session_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO sessions (id, name, type, created_at, updated_at) VALUES (?,?,?,?,?)",
            (session_id, body.name, body.type, now, now)
        )
        conn.commit()
    return {"id": session_id, "name": body.name, "type": body.type, "created_at": now}

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    with get_db_connection() as conn:
        conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        conn.commit()
    return {"ok": True}

# ─── Messages ─────────────────────────────────────────────────────────────────

@app.get("/api/sessions/{session_id}/messages")
async def get_messages(session_id: str):
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM messages WHERE session_id = ? ORDER BY created_at ASC",
            (session_id,)
        ).fetchall()
        return [dict(r) for r in rows]

@app.post("/api/chat")
async def send_message(body: MessageRequest):
    # Salvar mensagem do usuário
    now = datetime.now().isoformat()
    msg_id = str(uuid.uuid4())

    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO messages (id, session_id, role, content, created_at) VALUES (?,?,?,?,?)",
            (msg_id, body.session_id, "user", body.content, now)
        )
        # Buscar histórico da sessão
        history = conn.execute(
            "SELECT role, content FROM messages WHERE session_id = ? ORDER BY created_at ASC",
            (body.session_id,)
        ).fetchall()
        # Tipo da sessão
        session = conn.execute(
            "SELECT type, name FROM sessions WHERE id = ?", (body.session_id,)
        ).fetchone()
        conn.commit()

    # Carregar dados do usuário para contexto
    user_data = load_user_data()
    session_type = session["type"] if session else "general"
    session_name = session["name"] if session else "Chat"

    # Montar system prompt personalizado
    system_prompt = build_system_prompt(user_data, session_type, session_name)

    # Histórico para o LLM
    messages_for_llm = [{"role": r["role"], "content": r["content"]} for r in history]

    # Chamar Mistral via Ollama
    try:
        response_text = await chat_with_mistral(system_prompt, messages_for_llm)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Erro no LLM: {str(e)}. Verifique se o Ollama está rodando com 'ollama serve'")

    # Salvar resposta
    resp_id = str(uuid.uuid4())
    resp_now = datetime.now().isoformat()
    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO messages (id, session_id, role, content, created_at) VALUES (?,?,?,?,?)",
            (resp_id, body.session_id, "assistant", response_text, resp_now)
        )
        conn.execute(
            "UPDATE sessions SET updated_at = ? WHERE id = ?",
            (resp_now, body.session_id)
        )
        conn.commit()

    result = {"id": resp_id, "content": response_text, "role": "assistant"}

    # Sintetizar voz se pedido
    if body.use_voice:
        try:
            audio_path = await synthesize_speech(response_text)
            result["audio_url"] = f"/api/audio/{Path(audio_path).name}"
        except Exception as e:
            print(f"TTS falhou: {e}")

    return result

# ─── Voice ────────────────────────────────────────────────────────────────────

@app.post("/api/voice/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    """Recebe áudio, retorna transcrição (Whisper local)"""
    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
        content = await audio.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        text = await transcribe_audio(tmp_path)
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na transcrição: {str(e)}")
    finally:
        os.unlink(tmp_path)

@app.post("/api/voice/synthesize")
async def synthesize(text: str = Form(...)):
    """Converte texto em fala (com voz clonada se disponível)"""
    try:
        audio_path = await synthesize_speech(text)
        return FileResponse(audio_path, media_type="audio/wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/voice/upload-sample")
async def upload_voice_sample(audio: UploadFile = File(...)):
    """Recebe amostra de voz para clonagem e converte para WAV"""
    from voice import _convert_to_wav

    VOICES_DIR.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
        content = await audio.read()
        tmp.write(content)
        tmp_path = tmp.name

    main_sample = str(VOICES_DIR / "my_voice.wav")

    try:
        converted = _convert_to_wav(tmp_path, main_sample)
        if not converted:
            with open(main_sample, "wb") as f:
                f.write(content)
    finally:
        os.unlink(tmp_path)

    return {"ok": True, "message": "Amostra de voz salva! Será usada para clonagem."}

@app.get("/api/audio/{filename}")
async def get_audio(filename: str):
    audio_path = Path(tempfile.gettempdir()) / filename
    if not audio_path.exists():
        raise HTTPException(status_code=404)
    media_type = "audio/mpeg" if filename.endswith(".mp3") else "audio/wav"
    return FileResponse(str(audio_path), media_type=media_type)

@app.get("/api/voice/has-sample")
async def has_voice_sample():
    sample = VOICES_DIR / "my_voice.wav"
    return {"has_sample": sample.exists()}

# ─── User Data (Logs & Decisions) ─────────────────────────────────────────────

@app.get("/api/data/logs")
async def get_logs():
    with get_db_connection() as conn:
        rows = conn.execute("SELECT * FROM daily_logs ORDER BY date DESC").fetchall()
        return [dict(r) for r in rows]

@app.post("/api/data/logs")
async def add_log(log: DailyLog):
    with get_db_connection() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO daily_logs 
            (date, energy, focus, study_hours, questions_solved, subjects, did_well, needs_improvement, notes)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (log.date, log.energy, log.focus, log.study_hours, log.questions_solved,
              log.subjects, log.did_well, log.needs_improvement, log.notes))
        conn.commit()
    return {"ok": True}

@app.get("/api/data/decisions")
async def get_decisions():
    with get_db_connection() as conn:
        rows = conn.execute("SELECT * FROM decisions ORDER BY date DESC").fetchall()
        return [dict(r) for r in rows]

@app.post("/api/data/decisions")
async def add_decision(d: Decision):
    with get_db_connection() as conn:
        conn.execute("""
            INSERT INTO decisions (date, type, context, choice, result, reason)
            VALUES (?,?,?,?,?,?)
        """, (d.date, d.type, d.context, d.choice, d.result, d.reason))
        conn.commit()
    return {"ok": True}

@app.get("/api/data/insights")
async def get_insights():
    """Calcula insights rápidos dos dados"""
    with get_db_connection() as conn:
        logs = conn.execute("SELECT * FROM daily_logs ORDER BY date DESC LIMIT 30").fetchall()
        decisions = conn.execute("SELECT * FROM decisions").fetchall()

    if not logs:
        return {"insights": []}

    avg_energy = sum(r["energy"] for r in logs) / len(logs)
    avg_focus = sum(r["focus"] for r in logs) / len(logs)
    total_study = sum(r["study_hours"] for r in logs)
    good_decisions = sum(1 for d in decisions if d["result"] == "bom")
    total_decisions = len(decisions)

    return {
        "avg_energy": round(avg_energy, 1),
        "avg_focus": round(avg_focus, 1),
        "total_study_hours": round(total_study, 1),
        "decision_success_rate": round(good_decisions / total_decisions * 100, 1) if total_decisions else 0,
        "log_count": len(logs),
        "decision_count": total_decisions
    }

# ─── Helpers ──────────────────────────────────────────────────────────────────

def load_user_data() -> dict:
    """Carrega todos os dados do usuário para contexto da IA"""
    with get_db_connection() as conn:
        logs = conn.execute(
            "SELECT * FROM daily_logs ORDER BY date DESC LIMIT 20"
        ).fetchall()
        decisions = conn.execute(
            "SELECT * FROM decisions ORDER BY date DESC LIMIT 30"
        ).fetchall()

    return {
        "logs": [dict(r) for r in logs],
        "decisions": [dict(r) for r in decisions]
    }
