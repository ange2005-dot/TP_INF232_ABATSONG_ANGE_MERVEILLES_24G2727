from flask import Flask, render_template, request, redirect
import pandas as pd

app = Flask(__name__)

data = []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/form')
def form():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    entry = {
        "age": int(request.form['age']),
        "hours": float(request.form['hours']),
        "grade": float(request.form['grade']),
        "skin_color": request.form['skin_color'],
        "education_level": request.form['education_level'],
        "major": request.form['major']
    }
    data.append(entry)
    return redirect('/dashboard')

@app.route('/dashboard')
def dashboard():
    if not data:
        return render_template('dashboard.html', table=None)

    df = pd.DataFrame(data)

    avg_grade = round(df["grade"].mean(), 2)
    avg_hours = round(df["hours"].mean(), 2)
    correlation = round(df["hours"].corr(df["grade"]), 2)

    max_grade = df["grade"].max()
    min_grade = df["grade"].min()

    if correlation > 0.7:
        interpretation = "Forte corrélation entre travail et performance."
    elif correlation > 0.3:
        interpretation = "Corrélation modérée."
    else:
        interpretation = "Faible corrélation."

    skin_counts = df["skin_color"].value_counts().to_dict()
    level_counts = df["education_level"].value_counts().to_dict()
    major_counts = df["major"].value_counts().to_dict()

    table = df.to_html(classes='table', index=False)

    return render_template(
        'dashboard.html',
        avg_grade=avg_grade,
        avg_hours=avg_hours,
        correlation=correlation,
        max_grade=max_grade,
        min_grade=min_grade,
        interpretation=interpretation,
        skin_counts=skin_counts,
        level_counts=level_counts,
        major_counts=major_counts,
        table=table
    )

if __name__ == "__main__":
    app.run()