from flask import Flask, render_template, request, redirect
import sqlite3
import os
import math

app = Flask(__name__)

# Initialisation de la base de données
def init_db():
    os.makedirs("static", exist_ok=True)
    conn = sqlite3.connect("database.db")
    conn.execute("""
    CREATE TABLE IF NOT EXISTS data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        age INTEGER,
        study_hours REAL,
        grade REAL,
        skin_color TEXT,
        education_level TEXT,
        major TEXT
    )
    """)
    conn.close()

# Page d'accueil
@app.route('/')
def index():
    return render_template("index.html")

# Formulaire
@app.route('/form')
def form():
    return render_template("form.html")

# Soumission du formulaire
@app.route('/submit', methods=['POST'])
def submit():
    try:
        age = int(request.form['age'])
        hours = float(request.form['hours'])
        grade = float(request.form['grade'])
        skin_color = request.form['skin_color']
        education_level = request.form['education_level']
        major = request.form['major']
    except:
        return "Erreur dans les données saisies"

    with sqlite3.connect("database.db") as conn:
        conn.execute(
            "INSERT INTO data (age, study_hours, grade, skin_color, education_level, major) VALUES (?, ?, ?, ?, ?, ?)",
            (age, hours, grade, skin_color, education_level, major)
        )

    return redirect('/dashboard')

# Calcul de corrélation
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

# Dashboard
@app.route('/dashboard')
def dashboard():
    with sqlite3.connect("database.db") as conn:
        rows = conn.execute(
            "SELECT age, study_hours, grade, skin_color, education_level, major FROM data"
        ).fetchall()

    if not rows:
        return render_template(
            "dashboard.html",
            avg_grade="N/A",
            avg_hours="N/A",
            correlation="N/A",
            max_grade="N/A",
            min_grade="N/A",
            interpretation="Aucune donnée disponible, ajoute des entrées via le formulaire.",
            rows=[],
            skin_counts={},
            level_counts={},
            major_counts={}
        )

    count = len(rows)
    total_grade = sum(r[2] for r in rows)
    total_hours = sum(r[1] for r in rows)

    avg_grade = total_grade / count
    avg_hours = total_hours / count

    correlation = compute_correlation(
        [(r[0], r[1], r[2]) for r in rows],
        avg_hours,
        avg_grade
    )

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

    # Comptages
    skin_counts = {}
    level_counts = {}
    major_counts = {}

    for age, hours, grade, skin, level, major in rows:
        skin_counts[skin] = skin_counts.get(skin, 0) + 1
        level_counts[level] = level_counts.get(level, 0) + 1
        major_counts[major] = major_counts.get(major, 0) + 1

    return render_template(
        "dashboard.html",
        avg_grade=round(avg_grade, 2),
        avg_hours=round(avg_hours, 2),
        correlation=correlation_display,
        max_grade=max_grade,
        min_grade=min_grade,
        interpretation=interpretation,
        rows=rows,
        skin_counts=skin_counts,
        level_counts=level_counts,
        major_counts=major_counts
    )

# Lancement de l'application
if __name__ == "__main__":
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))