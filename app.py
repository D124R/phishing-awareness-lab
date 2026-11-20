import os
import sqlite3
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-only-change-this-key")

DB_PATH = os.path.join("database", "lab.db")

CHALLENGES = [
    {
        "id": 1,
        "title": "Identificando mensagens suspeitas",
        "level": "Iniciante",
        "xp": 100,
        "description": "Aprenda a reconhecer sinais comuns de phishing."
    },
    {
        "id": 2,
        "title": "Analisando remetentes",
        "level": "Iniciante",
        "xp": 150,
        "description": "Observe endereços fictícios e identifique inconsistências."
    },
    {
        "id": 3,
        "title": "Engenharia social",
        "level": "Intermediário",
        "xp": 200,
        "description": "Reconheça técnicas de manipulação em mensagens."
    }
]

def connect_db():
    os.makedirs("database", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                activity TEXT NOT NULL,
                points INTEGER NOT NULL,
                correct INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

def save_result(activity, points, correct):
    with connect_db() as conn:
        conn.execute(
            "INSERT INTO results (activity, points, correct) VALUES (?, ?, ?)",
            (activity, points, int(correct))
        )

def get_stats():
    with connect_db() as conn:
        total = conn.execute(
            "SELECT COUNT(*) FROM results"
        ).fetchone()[0]

        correct = conn.execute(
            "SELECT COUNT(*) FROM results WHERE correct = 1"
        ).fetchone()[0]

        xp = conn.execute(
            "SELECT COALESCE(SUM(points), 0) FROM results"
        ).fetchone()[0]

    return {
        "total": total,
        "correct": correct,
        "xp": xp,
        "accuracy": round((correct / total) * 100) if total else 0
    }

@app.route("/")
def index():
    return render_template("index.html", stats=get_stats())

@app.route("/desafios")
def challenges():
    return render_template(
        "challenges.html",
        challenges=CHALLENGES
    )

@app.route("/simulador", methods=["GET", "POST"])
def simulator():
    result = None

    # Mensagem inteiramente fictícia para treinamento.
    email = {
        "sender": "suporte@exemplo-suspeito.test",
        "subject": "Aviso de segurança da sua conta",
        "message": (
            "Esta é uma mensagem fictícia de treinamento. "
            "Observe o remetente, o tom de urgência e o contexto."
        )
    }

    if request.method == "POST":
        answer = request.form.get("answer", "")
        correct = answer == "phishing"
        points = 100 if correct else 0

        save_result("Simulador", points, correct)

        result = {
            "correct": correct,
            "points": points,
            "explanation": (
                "Correto! O domínio fictício e o contexto da mensagem "
                "são sinais que merecem atenção."
                if correct else
                "Observe o remetente e o contexto. "
                "A resposta correta era identificar a mensagem como suspeita."
            )
        }

    return render_template("simulator.html", email=email, result=result)

@app.route("/analisador", methods=["GET", "POST"])
def analyzer():
    analysis = None

    if request.method == "POST":
        message = request.form.get("message", "").strip()

        if len(message) > 5000:
            analysis = {
                "error": "O texto deve ter no máximo 5.000 caracteres."
            }
        elif not message:
            analysis = {"error": "Digite uma mensagem para analisar."}
        else:
            indicators = []

            patterns = {
                "Linguagem de urgência": [
                    "urgente", "imediatamente", "agora", "prazo"
                ],
                "Solicitação de informações": [
                    "senha", "credenciais", "dados pessoais"
                ],
                "Promessas ou ameaças": [
                    "bloqueada", "suspensa", "premio", "prêmio"
                ]
            }

            lowered = message.lower()

            for category, words in patterns.items():
                if any(word in lowered for word in words):
                    indicators.append(category)

            analysis = {
                "indicators": indicators,
                "count": len(indicators),
                "message": (
                    "Foram encontrados sinais que merecem atenção."
                    if indicators else
                    "Nenhum dos indicadores básicos configurados foi encontrado. "
                    "Isso não garante que a mensagem seja legítima."
                )
            }

    return render_template("analyzer.html", analysis=analysis)

@app.route("/relatorios")
def reports():
    stats = get_stats()

    with connect_db() as conn:
        results = conn.execute(
            "SELECT activity, points, correct, created_at "
            "FROM results ORDER BY id DESC LIMIT 20"
        ).fetchall()

    return render_template(
        "reports.html",
        stats=stats,
        results=results
    )

@app.route("/sobre")
def about():
    return render_template("about.html")

@app.route("/resetar", methods=["POST"])
def reset():
    with connect_db() as conn:
        conn.execute("DELETE FROM results")
    return redirect(url_for("reports"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
