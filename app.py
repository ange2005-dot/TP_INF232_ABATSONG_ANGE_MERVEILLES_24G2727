from flask import Flask, render_template, request, redirect, send_file
import pandas as pd
import matplotlib.pyplot as plt
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)

data = []

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("index.html")

# ---------------- FORM ----------------
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

# ---------------- DELETE FILTER ----------------
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

    # FILTRE
    level_filter = request.args.get("level")
    if level_filter and level_filter != "all":
        df = df[df["level"] == level_filter]

    avg_grade = round(df["grade"].mean(), 2)
    avg_hours = round(df["hours"].mean(), 2)
    correlation = round(df["hours"].corr(df["grade"]), 2)

    # ---------------- GRAPH PNG ----------------
    plt.figure()
    df["major"].value_counts().plot(kind="bar", color="blue")
    plt.title("Répartition des filières")
    plt.tight_layout()
    plt.savefig("static/bar.png")
    plt.close()

    plt.figure()
    plt.scatter(df["hours"], df["grade"], color="green")
    plt.title("Heures vs Notes")
    plt.xlabel("Heures")
    plt.ylabel("Notes")
    plt.tight_layout()
    plt.savefig("static/scatter.png")
    plt.close()

    return render_template(
        "dashboard.html",
        avg_grade=avg_grade,
        avg_hours=avg_hours,
        correlation=correlation,
        data=df.to_dict(orient="records"),
        levels=["all","L1","L2","L3"]
    )

# ---------------- PDF EXPORT ----------------
@app.route("/export/pdf")
def export_pdf():

    file = "dashboard.pdf"
    doc = SimpleDocTemplate(file)
    styles = getSampleStyleSheet()

    elements = []
    elements.append(Paragraph("Dashboard Etudiants", styles["Title"]))
    elements.append(Spacer(1,12))

    df = pd.DataFrame(data)

    elements.append(Paragraph(f"Moyenne note: {df['grade'].mean():.2f}", styles["Normal"]))
    elements.append(Paragraph(f"Moyenne heures: {df['hours'].mean():.2f}", styles["Normal"]))
    elements.append(Paragraph(f"Corrélation: {df['hours'].corr(df['grade']):.2f}", styles["Normal"]))

    doc.build(elements)

    return send_file(file, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)