from flask import Flask, render_template, request, redirect
import pandas as pd
import os
import matplotlib
matplotlib.use("Agg")

os.makedirs("static", exist_ok=True)

app = Flask(__name__)

data = []

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/form")
def form():
    return render_template("form.html")

@app.route("/submit", methods=["POST"])
def submit():
    data.append({
        "age": int(request.form["age"]),
        "hours": float(request.form["hours"]),
        "grade": float(request.form["grade"]),
        "level": request.form["level"],
        "major": request.form["major"]
    })
    return redirect("/dashboard")

@app.route("/dashboard")
def dashboard():
    if not data:
        return render_template("dashboard.html", empty=True)

    df = pd.DataFrame(data)

    return render_template(
        "dashboard.html",
        avg_grade=round(df["grade"].mean(),2),
        avg_hours=round(df["hours"].mean(),2),
        correlation=round(df["hours"].corr(df["grade"]),2),
        major_counts=df["major"].value_counts().to_dict(),
        level_counts=df["level"].value_counts().to_dict(),
        table=df.to_html(classes="table", index=False)
    )

if __name__ == "__main__":
    app.run(debug=True)