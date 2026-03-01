#  XAND.AI — v0.1

> *"Insanidade é fazer as mesmas coisas e esperar resultados diferentes."*

**XAND.AI** é um assistente de IA pessoal que roda **100% localmente** no seu PC.  
Não é um chatbot genérico — é um alter ego digital treinado com os **seus próprios dados**: suas decisões, sua energia, seu foco, sua rotina semanal.

---

##  O que é o XAND.AI?

A ideia central é simples: **quanto mais você usa e registra, mais inteligente ele fica sobre você.**

A cada conversa, o XAND.AI carrega automaticamente:
- Seu histórico de decisões (boas e ruins) com os padrões identificados
- Seus registros diários de energia, foco e horas de estudo
- Sua rotina semanal com metas e agenda
- Suas métricas de performance ao longo do tempo

Tudo isso vira contexto real para o modelo de linguagem — nada de conselhos genéricos.

---

##  Funcionalidades v0.1

-  **Múltiplos chats** com histórico salvo localmente (SQLite)
-  **Chat de Rotina** dedicado a planejamento inteligente
-  **Painel de rotina semanal** com agenda, metas e progresso
-  **Registro diário** — energia, foco, horas de estudo, o que foi bem e o que melhorar
-  **Métricas em tempo real** na sidebar (energia média, foco, horas, taxa de acerto)
-  **Input por voz** — fale em vez de digitar (Whisper local)
-  **Resposta por voz** — XAND.AI responde em áudio (PT-BR)
-  **Sistema de decisões** — registre escolhas e resultados para a IA aprender seus padrões
-  **100% local** — seus dados nunca saem do seu computador

---

## 🛠️ Stack

| Camada | Tecnologia |
|---|---|
| LLM | [Ollama](https://ollama.com) + Mistral 7B (local) |
| Backend | Python + FastAPI |
| STT | faster-whisper (local) |
| TTS | edge-tts (PT-BR, AntonioNeural) |
| Banco de dados | SQLite |
| Frontend | HTML + CSS + JS (single file) |

---

## 🚀Instalação

### Pré-requisitos

- Python 3.10+
- [Ollama](https://ollama.com) instalado

### Passo a passo

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/xand-ai.git
cd xand-ai

# 2. Baixe o modelo de linguagem (só na primeira vez, ~4GB)
ollama pull mistral

# 3. Instale as dependências
python setup.py

# 4. Inicie o Ollama (terminal separado)
ollama serve

# 5. Inicie o XAND.AI
python start.py
```

O navegador abre automaticamente em `http://localhost:8000`.

---

## 📁 Estrutura do projeto

```
xand-ai/
├── backend/
│   ├── main.py          # API FastAPI — endpoints de chat, voz, dados
│   ├── database.py      # SQLite — tabelas e dados iniciais
│   ├── llm.py           # Integração Ollama/Mistral + system prompt
│   ├── voice.py         # STT (Whisper) + TTS (edge-tts)
│   └── requirements.txt
├── frontend/
│   └── index.html       # Interface completa (HTML + CSS + JS)
├── data/
│   └── personal_ai.db   # Banco de dados (gerado automaticamente)
├── voices/
│   └── my_voice.wav     # Amostra de voz para clonagem (opcional)
├── setup.py             # Instalação automática
├── start.py             # Iniciar o app
└── README.md
```

---

##  Como a IA aprende sobre você

### Registro diário
Clique em  e preencha ao final de cada dia:
- Nível de energia e foco (0-10)
- Horas de estudo e questões resolvidas
- O que foi bem e o que precisa melhorar

### Registro de decisões
Via API ou interface, registre decisões importantes:
```python
import requests

requests.post("http://localhost:8000/api/data/decisions", json={
    "date": "2026-03-01",
    "type": "estudo",
    "context": "vontade de usar o celular",
    "choice": "escolhi estudar mais 1 bloco",
    "result": "bom",
    "reason": "Disciplina mesmo cansado"
})
```

### Rotina semanal
Cole sua rotina no formato estruturado e o XAND.AI a usa para planejar e cobrar.

---

##  Configuração

### Trocar o modelo de linguagem
Em `backend/llm.py`:
```python
MODEL = "mistral"      # padrão
# MODEL = "phi4"       # menor, mais rápido (4B)
# MODEL = "llama3.1"   # mais inteligente (7B)
```

### Ativar clonagem de voz
1. Clique em  no app
2. Grave 30+ segundos da sua voz
3. Ative "Usar minha voz clonada" no painel

---

## 🗺️ Roadmap

- [ ] Gráficos de evolução de energia/foco ao longo do tempo
- [ ] Fine-tuning com dados pessoais
- [ ] Integração com calendário
- [ ] Análise semanal automática com relatório
- [ ] Modo coach de vôlei especializado
- [ ] Export dos dados para Excel/PDF
- [ ] Autenticação para deployment seguro
- [ ] Suporte a múltiplos usuários

---

##  Licença

MIT License — use, modifique e distribua à vontade.

Made with vibe coding with Claude!

---

<div align="center">
  <strong>XAND.AI v0.1</strong> · Feito para alta performance pessoal<br>
  <em>Estudo · Esporte · Disciplina</em>
</div>
