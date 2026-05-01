from flask import Flask, render_template, request, redirect
import pandas as pd
import matplotlib
matplotlib.use("Agg")

app = Flask(__name__)

# stockage temporaire
data = []

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("index.html")

# ---------------- FORM ----------------
@app.route("/form")
def form():
    return render_template("form.html")

# ---------------- SUBMIT ----------------
@app.route("/submit", methods=["POST"])
def submit():
    student = {
        "name": request.form["name"],
        "age": int(request.form["age"]),
        "level": request.form["level"],
        "major": request.form["major"],
        "hours": float(request.form["hours"]),
        "grade": float(request.form["grade"])
    }

    data.append(student)

    return redirect("/dashboard")

# ---------------- DELETE ----------------
@app.route("/delete/<int:i>")
def delete(i):
    if i < len(data):
        data.pop(i)
    return redirect("/dashboard")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():

    if not data:
        return render_template("dashboard.html", empty=True)

    df = pd.DataFrame(data)

    # filtres
    level_filter = request.args.get("level", "all")
    major_filter = request.args.get("major", "all")

    if level_filter != "all":
        df = df[df["level"] == level_filter]

    if major_filter != "all":
        df = df[df["major"] == major_filter]

    # stats
    avg_grade = round(df["grade"].mean(), 2) if len(df) else 0
    avg_hours = round(df["hours"].mean(), 2) if len(df) else 0

    correlation = df["hours"].corr(df["grade"]) if len(df) > 1 else 0
    if pd.isna(correlation):
        correlation = 0
    else:
        correlation = round(correlation, 2)

    stats = {
        "total": len(df),
        "avg_grade": avg_grade,
        "avg_hours": avg_hours,
        "correlation": correlation
    }

    levels = ["all", "L1", "L2", "L3"]
    majors = ["all"] + sorted(list(set([d["major"] for d in data])))

    # pas de crash si pas de graph
    charts = {}

    return render_template(
        "dashboard.html",
        empty=False,
        data=df.to_dict("records"),
        stats=stats,
        charts=charts,
        levels=levels,
        majors=majors,
        current_level=level_filter,
        current_major=major_filter
    )

if __name__ == "__main__":
    app.run(debug=True)