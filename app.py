from flask import Flask, render_template, request, redirect
import sqlite3
import os
import pandas as pd
import matplotlib.pyplot as plt

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

@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect("database.db")
    df = pd.read_sql_query("SELECT * FROM data", conn)
    conn.close()

    if df.empty:
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

    avg_grade = df['grade'].mean()
    avg_hours = df['study_hours'].mean()
    correlation = df['study_hours'].corr(df['grade'])
    correlation_display = round(correlation, 2) if pd.notna(correlation) else "N/A"

    max_grade = df['grade'].max()
    min_grade = df['grade'].min()

    if correlation > 0.5:
        interpretation = "Plus les étudiants étudient, meilleures sont leurs notes."
    elif correlation < -0.5:
        interpretation = "Relation inverse inattendue."
    else:
        interpretation = "Relation faible entre étude et performance."

    plt.figure()
    plt.scatter(df['study_hours'], df['grade'])
    plt.xlabel("Heures d'étude")
    plt.ylabel("Notes")
    plt.title("Relation étude / note")
    plt.savefig(os.path.join("static", "plot.png"))
    plt.close()

    table = df.to_html(classes='table', index=False)

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