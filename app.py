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
        "level": request.form['education_level'],
        "major": request.form['major']
    }
    data.append(entry)
    return redirect('/dashboard')

@app.route('/delete/<int:index>')
def delete(index):
    if 0 <= index < len(data):
        data.pop(index)
    return redirect('/dashboard')

@app.route('/dashboard')
def dashboard():
    if not data:
        return render_template('dashboard.html', empty=True)

    df = pd.DataFrame(data)

    avg_grade = round(df["grade"].mean(), 2)
    avg_hours = round(df["hours"].mean(), 2)
    correlation = round(df["hours"].corr(df["grade"]), 2)

    return render_template(
        'dashboard.html',
        avg_grade=avg_grade,
        avg_hours=avg_hours,
        correlation=correlation,
        data=data,
        grades=list(df["grade"]),
        hours=list(df["hours"]),
        majors=list(df["major"]),
        levels=list(df["level"])
    )

if __name__ == "__main__":
    app.run()