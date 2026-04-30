@app.route("/dashboard")
def dashboard():

    if not data:
        return render_template("dashboard.html", empty=True)

    df = pd.DataFrame(data)

    # SAFE FILTER
    level_filter = request.args.get("level")
    if level_filter and level_filter != "all":
        df = df[df["level"] == level_filter]

    avg_grade = round(df["grade"].mean(), 2)
    avg_hours = round(df["hours"].mean(), 2)

    correlation = df["hours"].corr(df["grade"])
    if pd.isna(correlation):
        correlation = 0
    else:
        correlation = round(correlation, 2)

    # SAFE GRAPH
    import matplotlib.pyplot as plt
    import os
    os.makedirs("static", exist_ok=True)

    plt.figure()
    df["major"].value_counts().plot(kind="bar")
    plt.savefig("static/bar.png")
    plt.close()

    plt.figure()
    plt.scatter(df["hours"], df["grade"])
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