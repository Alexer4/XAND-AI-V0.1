# ⚡ XAND.AI — v0.1

> *"Insanity is doing the same things and expecting different results."*

**XAND.AI** is a personal AI assistant that runs **100% locally** on your PC.  
It's not a generic chatbot — it's a digital alter ego trained on **your own data**: your decisions, your energy levels, your focus, your weekly routine.

---

##  What is XAND.AI?

The core idea is simple: **the more you use and log, the smarter it gets about you.**

Every conversation, XAND.AI automatically loads:
- Your decision history (good and bad) with identified patterns
- Your daily logs of energy, focus, and study hours
- Your weekly routine with goals and schedule
- Your performance metrics over time

All of this becomes real context for the language model — no generic advice.

---

##  Features v0.1

-  **Multiple chats** with locally saved history (SQLite)
-  **Routine Chat** dedicated to smart planning
-  **Weekly routine panel** with schedule, goals and progress tracking
-  **Daily log** — energy, focus, study hours, wins and improvements
-  **Real-time metrics** on sidebar (avg energy, focus, hours, decision success rate)
-  **Voice input** — speak instead of type (local Whisper)
-  **Voice response** — XAND.AI replies in audio (PT-BR)
-  **Decision tracking** — log choices and outcomes so the AI learns your patterns
-  **100% local** — your data never leaves your computer

---

##  Stack

| Layer | Technology |
|---|---|
| LLM | [Ollama](https://ollama.com) + Mistral 7B (local) |
| Backend | Python + FastAPI |
| STT | faster-whisper (local) |
| TTS | edge-tts (PT-BR, AntonioNeural) |
| Database | SQLite |
| Frontend | HTML + CSS + JS (single file) |

---

##  Installation

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com) installed

### Step by step

```bash
# 1. Clone the repository
git clone https://github.com/your-username/xand-ai.git
cd xand-ai

# 2. Download the language model (first time only, ~4GB)
ollama pull mistral

# 3. Install dependencies
python setup.py

# 4. Start Ollama (separate terminal)
ollama serve

# 5. Start XAND.AI
python start.py
```

Browser opens automatically at `http://localhost:8000`.

---

##  Project structure

```
xand-ai/
├── backend/
│   ├── main.py          # FastAPI — chat, voice and data endpoints
│   ├── database.py      # SQLite — tables and seed data
│   ├── llm.py           # Ollama/Mistral integration + system prompt
│   ├── voice.py         # STT (Whisper) + TTS (edge-tts)
│   └── requirements.txt
├── frontend/
│   └── index.html       # Full interface (HTML + CSS + JS)
├── data/
│   └── personal_ai.db   # Database (auto-generated)
├── voices/
│   └── my_voice.wav     # Voice sample for cloning (optional)
├── setup.py             # Auto installer
├── start.py             # App launcher
└── README.md
```

---

##  How the AI learns about you

### Daily log
Click  at the end of each day and fill in:
- Energy and focus levels (0-10)
- Study hours and questions solved
- What went well and what needs improvement

### Decision tracking
Log important decisions via API or interface:
```python
import requests

requests.post("http://localhost:8000/api/data/decisions", json={
    "date": "2026-03-01",
    "type": "study",
    "context": "felt like using my phone",
    "choice": "chose to study one more block",
    "result": "good",
    "reason": "stayed disciplined even when tired"
})
```

### Weekly routine
Paste your weekly schedule in structured format and XAND.AI uses it to plan and hold you accountable.

---

##  Configuration

### Switch the language model
In `backend/llm.py`:
```python
MODEL = "mistral"      # default
# MODEL = "phi4"       # smaller, faster (4B)
# MODEL = "llama3.1"   # smarter (7B)
```

### Enable voice cloning
1. Click 🎤 in the app
2. Record 30+ seconds of your voice
3. Enable "Use my cloned voice" in the panel

---

##  Roadmap

- [ ] Energy/focus evolution charts over time
- [ ] Personal data fine-tuning
- [ ] Calendar integration
- [ ] Automatic weekly analysis report
- [ ] Specialized volleyball coach mode
- [ ] Data export to Excel/PDF
- [ ] Authentication for secure deployment
- [ ] Multi-user support

---

##  License
Vibe coding with Claude.
MIT License — use, modify and distribute freely.

---

<div align="center">
  <strong>XAND.AI v0.1</strong> · Built for personal high performance<br>
  <em>Study · Sport · Discipline</em>
</div>
