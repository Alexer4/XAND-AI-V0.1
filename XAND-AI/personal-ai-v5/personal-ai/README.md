# ⚡ Personal AI — Seu alter ego digital

Um assistente de IA local e personalizado que te conhece de verdade — baseado nos **seus dados reais**.

---

## O que ele faz

- 💬 **Múltiplos chats** com histórico salvo localmente
- 🎯 **Chat de Rotina** dedicado a planejamento inteligente
- 🧠 **IA que te conhece** — carrega seu histórico de decisões, energia, foco e estudo
- 🎙️ **Voz de entrada** — fale em vez de digitar (Whisper local)
- 🔊 **Voz de saída** — responde com a **sua própria voz** (Coqui XTTS-v2)
- 📋 **Registro diário** — adicione energia, foco, horas de estudo
- 📊 **Métricas em tempo real** — painel lateral com seus dados

---

## Pré-requisitos

| Ferramenta | Link |
|---|---|
| Python 3.10+ | https://python.org |
| Ollama | https://ollama.com |

---

## Instalação (5 minutos)

### 1. Clone / baixe o projeto

```bash
# Se tiver git:
git clone <url>
cd personal-ai

# Ou extraia o ZIP baixado
```

### 2. Execute o setup

```bash
python setup.py
```

Este script vai:
- Verificar Python e Ollama
- Baixar o modelo Mistral (~4GB, só na primeira vez)
- Instalar todas as dependências Python

### 3. Inicie

```bash
python start.py
```

O navegador vai abrir automaticamente em `http://localhost:8000`.

> **Nota:** O Ollama precisa estar rodando. Se não estiver, execute `ollama serve` em um terminal separado antes de rodar `start.py`.

---

## Uso

### 💬 Conversar
Selecione um chat na sidebar e comece a digitar. A IA já conhece seus padrões.

### 🎯 Organizador de Rotina
O chat principal. Peça para ele:
- "Planeja minha rotina de amanhã"
- "Qual é meu padrão quando quebro expectativas?"
- "Como otimizar minha semana de estudos?"

### 🎙️ Gravar sua voz (importante!)
1. Clique no botão 🎤 no topo direito
2. Grave 30+ segundos falando naturalmente
3. A IA vai responder com a sua voz

### 📋 Registrar o dia
Clique em 📋 e preencha: energia, foco, horas de estudo, o que foi bem e o que melhorar. **Quanto mais dados, mais precisa a IA fica.**

---

## Estrutura do projeto

```
personal-ai/
├── backend/
│   ├── main.py          # API FastAPI
│   ├── database.py      # SQLite + dados iniciais
│   ├── llm.py           # Integração Ollama/Mistral
│   ├── voice.py         # STT (Whisper) + TTS (Coqui)
│   └── requirements.txt
├── frontend/
│   └── index.html       # Interface completa
├── data/
│   └── personal_ai.db   # Banco de dados (criado automaticamente)
├── voices/
│   └── my_voice.wav     # Sua amostra de voz
├── setup.py             # Instalação
├── start.py             # Iniciar app
└── README.md
```

---

## Adicionar mais dados à IA

### Via interface
Use o botão 📋 para registros diários.

### Via API diretamente
```python
import requests

# Adicionar log diário
requests.post("http://localhost:8000/api/data/logs", json={
    "date": "2026-03-01",
    "energy": 8.0,
    "focus": 7.5,
    "study_hours": 4.0,
    "questions_solved": 15,
    "subjects": "Canguru, Machine Learning",
    "did_well": "Resolvi questões difíceis com calma",
    "needs_improvement": "Começar mais cedo",
    "notes": ""
})

# Adicionar decisão
requests.post("http://localhost:8000/api/data/decisions", json={
    "date": "2026-03-01",
    "type": "estudo",
    "context": "vontade de usar celular",
    "choice": "escolhi estudar mais 1 bloco",
    "result": "bom",
    "reason": "Disciplina mesmo cansado"
})
```

---

## Modelos alternativos

No `backend/llm.py`, mude a linha:
```python
MODEL = "mistral"
```

Opções disponíveis (requerem `ollama pull <modelo>`):
- `mistral` — padrão, bom equilíbrio (4GB)
- `llama3.2` — muito bom, maior (7GB)
- `phi3` — leve e rápido (2GB)
- `mistral-small` — mais rápido (2GB)

---

## Solução de problemas

**"Erro no LLM: Connection refused"**
→ Execute `ollama serve` em um terminal separado

**"faster-whisper não instalado"**
→ Execute `pip install faster-whisper`

**TTS lento na primeira vez**
→ Normal — o modelo XTTS-v2 (~1.8GB) é baixado automaticamente

**Sem voz em português no pyttsx3**
→ Instale vozes PT-BR no sistema operacional:
- Windows: Configurações → Fala → Adicionar vozes
- Linux: `apt install espeak-ng-data-pt`

---

## Roadmap sugerido

- [ ] Gráficos de evolução de energia/foco ao longo do tempo
- [ ] Modo "coach de vôlei" especializado
- [ ] Integração com calendário para planejamento real
- [ ] Análise de padrões semanais automática
- [ ] Export dos dados para Excel/PDF
