from flask import Flask, render_template, request, redirect, send_file
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io
import base64
import numpy as np

app = Flask(__name__)
PORT = int(os.environ.get('PORT', 5000))

# Stockage des données
data = []

# Créer les dossiers nécessaires
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

@app.route("/")
def home():
    stats = {}
    if data:
        df = pd.DataFrame(data)
        stats = {
            'total': len(data),
            'avg_grade': round(df['grade'].mean(), 2),
            'avg_hours': round(df['hours'].mean(), 2),
            'majors': df['major'].nunique()
        }
    return render_template("index.html", stats=stats)

@app.route("/form")
def form():
    return render_template("form.html")

@app.route("/submit", methods=["POST"])
def submit():
    new_entry = {
        "name": request.form.get("name", ""),
        "age": int(request.form.get("age", 0)),
        "hours": float(request.form.get("hours", 0)),
        "grade": float(request.form.get("grade", 0)),
        "level": request.form.get("level", ""),
        "major": request.form.get("major", "")
    }
    data.append(new_entry)
    return redirect("/dashboard")

@app.route("/delete/<int:i>")
def delete(i):
    if 0 <= i < len(data):
        data.pop(i)
    return redirect("/dashboard")

@app.route("/dashboard")
def dashboard():
    if not data:
        return render_template("dashboard.html", empty=True, data=[], stats={}, charts={})
    
    df = pd.DataFrame(data)
    level_filter = request.args.get("level", "all")
    major_filter = request.args.get("major", "all")
    
    filtered_df = df.copy()
    if level_filter != "all":
        filtered_df = filtered_df[filtered_df["level"] == level_filter]
    if major_filter != "all":
        filtered_df = filtered_df[filtered_df["major"] == major_filter]
    
    if len(filtered_df) > 0:
        stats = {
            'total': len(filtered_df),
            'avg_grade': round(filtered_df["grade"].mean(), 2),
            'avg_hours': round(filtered_df["hours"].mean(), 2),
            'correlation': round(filtered_df["hours"].corr(filtered_df["grade"]), 2) if len(filtered_df) > 1 else 0,
            'min_grade': round(filtered_df["grade"].min(), 2),
            'max_grade': round(filtered_df["grade"].max(), 2),
            'avg_age': round(filtered_df["age"].mean(), 2)
        }
    else:
        stats = {'total': 0, 'avg_grade': 0, 'avg_hours': 0, 'correlation': 0, 'min_grade': 0, 'max_grade': 0, 'avg_age': 0}
    
    charts = generate_charts(filtered_df) if len(filtered_df) > 0 else {}
    levels = ["all", "L1", "L2", "L3", "M1", "M2"]
    majors = ["all"] + sorted(df["major"].unique().tolist()) if len(df) > 0 else ["all"]
    
    return render_template("dashboard.html", 
                         stats=stats, 
                         data=filtered_df.to_dict(orient="records"), 
                         levels=levels, 
                         majors=majors, 
                         current_level=level_filter, 
                         current_major=major_filter, 
                         charts=charts)

def generate_charts(df):
    charts = {}
    
    try:
        plt.figure(figsize=(10, 6))
        major_counts = df["major"].value_counts()
        colors_bar = plt.cm.Blues(np.linspace(0.4, 0.9, len(major_counts)))
        major_counts.plot(kind="bar", color=colors_bar, edgecolor='navy', linewidth=2)
        plt.title("Répartition des Filières", fontsize=16, fontweight='bold', pad=20)
        plt.xlabel("Filières", fontsize=12)
        plt.ylabel("Nombre d'étudiants", fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        charts['bar_chart'] = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
    except Exception as e:
        print(f"Erreur graphique bar: {e}")
    
    try:
        if len(df) > 1:
            plt.figure(figsize=(10, 6))
            plt.scatter(df["hours"], df["grade"], s=100, alpha=0.6, c='#ff6b9d', edgecolors='darkblue', linewidth=1.5)
            z = np.polyfit(df["hours"], df["grade"], 1)
            p = np.poly1d(z)
            plt.plot(df["hours"].sort_values(), p(df["hours"].sort_values()), "b--", alpha=0.8, label='Tendance')
            plt.title("Relation Heures vs Notes", fontsize=16, fontweight='bold', pad=20)
            plt.xlabel("Heures de travail par semaine", fontsize=12)
            plt.ylabel("Notes (/20)", fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.legend()
            plt.tight_layout()
            
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            charts['scatter_chart'] = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
    except Exception as e:
        print(f"Erreur graphique scatter: {e}")
    
    return charts

@app.route("/export/pdf")
def export_pdf():
    if not data:
        return redirect("/dashboard")
    
    df = pd.DataFrame(data)
    filename = f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    try:
        doc = SimpleDocTemplate(filename)
        styles = getSampleStyleSheet()
        elements = []
        elements.append(Paragraph("Dashboard Universitaire", styles["Title"]))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles["Normal"]))
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(f"Nombre d'étudiants: {len(df)}", styles["Normal"]))
        elements.append(Paragraph(f"Note moyenne: {df['grade'].mean():.2f}/20", styles["Normal"]))
        elements.append(Paragraph(f"Heures moyennes: {df['hours'].mean():.1f}h/semaine", styles["Normal"]))
        if len(df) > 1:
            elements.append(Paragraph(f"Corrélation: {df['hours'].corr(df['grade']):.2f}", styles["Normal"]))
        doc.build(elements)
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return f"Erreur PDF: {e}"

@app.route("/health")
def health():
    return {"status": "ok", "students": len(data)}

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=PORT, debug=False)