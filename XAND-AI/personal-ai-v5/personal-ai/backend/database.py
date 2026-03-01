"""
Database - SQLite local
"""

import sqlite3
import json
from pathlib import Path
from contextlib import contextmanager

DB_PATH = Path(__file__).parent.parent / "data" / "personal_ai.db"
DATA_DIR = Path(__file__).parent.parent / "data"

def init_db():
    DATA_DIR.mkdir(exist_ok=True)
    with get_db_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT DEFAULT 'general',
                created_at TEXT,
                updated_at TEXT
            );

            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                session_id TEXT,
                role TEXT,
                content TEXT,
                created_at TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            );

            CREATE TABLE IF NOT EXISTS daily_logs (
                date TEXT PRIMARY KEY,
                energy REAL,
                focus REAL,
                study_hours REAL DEFAULT 0,
                questions_solved INTEGER DEFAULT 0,
                subjects TEXT DEFAULT '',
                did_well TEXT DEFAULT '',
                needs_improvement TEXT DEFAULT '',
                notes TEXT DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                type TEXT,
                context TEXT,
                choice TEXT,
                result TEXT,
                reason TEXT
            );
        """)
        conn.commit()
        _seed_initial_data(conn)

def _seed_initial_data(conn):
    """Popula o banco com os dados já coletados pelo usuário"""

    # Criar sessão principal de rotina se não existir
    existing = conn.execute("SELECT id FROM sessions WHERE type = 'rotina'").fetchone()
    if not existing:
        from datetime import datetime
        now = datetime.now().isoformat()
        conn.execute(
            "INSERT INTO sessions (id, name, type, created_at, updated_at) VALUES (?,?,?,?,?)",
            ("rotina-principal", "🎯 Organizador de Rotina", "rotina", now, now)
        )

    # Decisões já coletadas
    decisions_count = conn.execute("SELECT COUNT(*) FROM decisions").fetchone()[0]
    if decisions_count == 0:
        decisions = [
            ("2026-02-13", "estudo", "acordar cedo para estudar", "decidi acordar cedo (4:40) em vez de dormir mais", "bom", "Dormi 8 horas, hábito sedimentado de 2 meses; deu foco, mas se sono ruim, priorizo sono."),
            ("2026-02-13", "esporte", "depois de estudar e me alimentar", "decidi treinar vôlei de areia às 8:00", "bom", "Gosto do esporte; campeonato paranaense perto, então treino com mais afinidade e concentração."),
            ("2026-02-14", "estudo", "simulado canguru da matemática", "decidi desistir do simulado depois de resolver algumas questões", "ruim", "Estudei bastante e tive uma expectativa grande, o simulado teve uma quebra grande de expectativa, o que gerou frustração."),
            ("2026-02-14", "estudo", "estudo canguru da matemática", "decidi usar o celular a tarde inteira", "ruim", "Quebra de expectativa gerou frustração que me fez pensar em desistir da prova."),
            ("2026-02-15", "estudo", "organização geral", "decidi criar metas de longo prazo", "bom", "Reconheci minhas fraquezas, e meus objetivos, e sedimentei metas para alcançar"),
            ("2026-02-15", "relações pessoais", "conversa pessoal", "decidi deixar o passado para trás", "bom", "Reconheci que o passado já aconteceu, e pedi opinião á essa pessoa"),
            ("2026-02-15", "relações pessoais", "conversa pessoal", "decidi pedir conselho de amigos", "bom", "Reconheci que preciso de ajuda em certos aspectos da vida"),
            ("2026-02-16", "treino", "calistenia", "decidi acordar bem cedo e treinar calistenia", "bom", "Tive um sono bom e de qualidade, consegui treinar de forma correta e tranquila."),
            ("2026-02-16", "alimentação", "comer de forma saudável", "decidi comer 5 ovos com dois pães, e tomar Whey", "bom", "Tive um treino bom e tenho consciência de que treino sem alimentação deve resultar em perda de músculo."),
            ("2026-02-16", "estudo", "estudo canguru da matemática", "decidi resolver as questões fáceis da prova de 2021 nível j", "bom", "Sessão de estudo boa, acertei 10 questões de 10 respondidas, aumentei minha confiança ao responder com calma."),
            ("2026-02-16", "estudo", "estudo canguru da matemática", "decidi fazer outras coisas além de estudar pois isso subiu pra cabeça", "ruim", "Apesar de estudar e conseguir bons resultados, isso ocasionou em pausas desordenadas e sem nexo."),
        ]
        conn.executemany(
            "INSERT INTO decisions (date, type, context, choice, result, reason) VALUES (?,?,?,?,?,?)",
            decisions
        )

    # Logs diários já coletados
    logs_count = conn.execute("SELECT COUNT(*) FROM daily_logs").fetchone()[0]
    if logs_count == 0:
        logs = [
            ("2026-02-22", 7.5, 7.0, 0, 0, "", "Joguei relativamente bem no torneio, quartas de final", "Virada de bola em situações mais complicadas", "Torneio paranaense de vôlei de areia"),
            ("2026-02-23", 7.0, 6.0, 3.5, 0, "IA, ENEM, Programação", "Estudei com foco bastante tempo, tipo umas 4 horas", "Mais resiliência e paciência, conciliar Canguru e programação", "2 blocos IA, 1 bloco ENEM, 25min programação leve"),
            ("2026-02-25", 7.0, 6.0, 3.0, 0, "Machine Learning", "Estudei tópicos importantes de machine learning com foco", "Começar a jornada de estudos um pouco antes, foco total", ""),
        ]
        conn.executemany("""
            INSERT OR IGNORE INTO daily_logs 
            (date, energy, focus, study_hours, questions_solved, subjects, did_well, needs_improvement, notes)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, logs)

    conn.commit()

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
