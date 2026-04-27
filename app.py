from flask import Flask, render_template, request, redirect
import sqlite3
import os
import math

app = Flask(__name__)

def init_db():
    os.makedirs("static", exist_ok=True)
    conn = sqlite3.connect("database.db")
    conn.execute("""
    CREATE TABLE IF NOT EXISTS data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        age INTEGER,
        study_hours REAL,
        grade REAL
    )
    """)
    conn.close()

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/form')
def form():
    return render_template("form.html")

@app.route('/submit', methods=['POST'])
def submit():
    age = int(request.form['age'])
    hours = float(request.form['hours'])
    grade = float(request.form['grade'])

    conn = sqlite3.connect("database.db")
    conn.execute(
        "INSERT INTO data (age, study_hours, grade) VALUES (?, ?, ?)",
        (age, hours, grade)
    )
    conn.commit()
    conn.close()

    return redirect('/dashboard')

def compute_correlation(rows, avg_hours, avg_grade):
    n = len(rows)
    if n < 2:
        return None
    cov = sum((h - avg_hours) * (g - avg_grade) for _, h, g in rows) / (n - 1)
    var_hours = sum((h - avg_hours) ** 2 for _, h, _ in rows) / (n - 1)
    var_grade = sum((g - avg_grade) ** 2 for _, _, g in rows) / (n - 1)
    if var_hours == 0 or var_grade == 0:
        return None
    return cov / math.sqrt(var_hours * var_grade)

@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect("database.db")
    rows = conn.execute("SELECT age, study_hours, grade FROM data").fetchall()
    conn.close()

    if not rows:
        return render_template(
            "dashboard.html",
            avg_grade="N/A",
            avg_hours="N/A",
            correlation="N/A",
            max_grade="N/A",
            min_grade="N/A",
            interpretation="Aucune donnée disponible, ajoute des entrées via le formulaire.",
            table="<p>Aucune donnée enregistrée.</p>"
        )

    count = len(rows)
    total_grade = sum(r[2] for r in rows)
    total_hours = sum(r[1] for r in rows)

    avg_grade = total_grade / count
    avg_hours = total_hours / count
    correlation = compute_correlation(rows, avg_hours, avg_grade)
    correlation_display = round(correlation, 2) if correlation is not None else "N/A"

    max_grade = max(r[2] for r in rows)
    min_grade = min(r[2] for r in rows)

    if correlation is None:
        interpretation = "Pas assez de données pour calculer la corrélation."
    elif correlation > 0.5:
        interpretation = "Plus les étudiants étudient, meilleures sont leurs notes."
    elif correlation < -0.5:
        interpretation = "Relation inverse inattendue."
    else:
        interpretation = "Relation faible entre étude et performance."

    table = "<table border='1'><tr><th>Âge</th><th>Heures d'étude</th><th>Note</th></tr>"
    for age, hours, grade in rows:
        table += f"<tr><td>{age}</td><td>{hours}</td><td>{grade}</td></tr>"
    table += "</table>"

    return render_template(
        "dashboard.html",
        avg_grade=round(avg_grade, 2),
        avg_hours=round(avg_hours, 2),
        correlation=correlation_display,
        max_grade=max_grade,
        min_grade=min_grade,
        interpretation=interpretation,
        table=table
    )

if __name__ == "__main__":
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))