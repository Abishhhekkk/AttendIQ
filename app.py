from flask import Flask, render_template, request, redirect, url_for
import json
from datetime import datetime

app = Flask(__name__)

# -----------------------------
# Teacher Credentials
# -----------------------------
USERNAME = "admin"
PASSWORD = "admin123"

# -----------------------------
# Helper Functions
# -----------------------------
def load_data():
    with open("attendance.json", "r") as file:
        return json.load(file)

def save_data(data):
    with open("attendance.json", "w") as file:
        json.dump(data, file, indent=4)

# -----------------------------
# Home Page
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html")

# -----------------------------
# Teacher Login Page
# -----------------------------
@app.route("/teacher")
def teacher():
    return render_template("teacher.html")

# -----------------------------
# Login Validation
# -----------------------------
@app.route("/login", methods=["POST"])
def login():

    username = request.form.get("username")
    password = request.form.get("password")

    if username == USERNAME and password == PASSWORD:
        return redirect(url_for("dashboard"))

    return render_template(
        "teacher.html",
        error="Invalid Username or Password"
    )

# -----------------------------
# Teacher Dashboard
# -----------------------------
@app.route("/dashboard")
def dashboard():

    data = load_data()

    present = len(data["today"])

    return render_template(
        "dashboard.html",
        present=present
    )

# -----------------------------
# Student Attendance Page
# -----------------------------
@app.route("/student")
def student():
    return render_template("student.html")

# -----------------------------
# Submit Attendance
# -----------------------------
@app.route("/submit", methods=["POST"])
def submit():

    name = request.form["name"]
    roll = request.form["roll"]

    data = load_data()

    # Check if student exists
    if roll not in data["students"]:
        return "<h2>❌ Student not found.</h2>"

    # Prevent duplicate attendance
    for student in data["today"]:
        if student["roll"] == roll:
            return "<h2>⚠ Attendance already marked.</h2>"

    # Save today's attendance
    data["today"].append({
        "name": name,
        "roll": roll,
        "time": datetime.now().strftime("%H:%M:%S")
    })

    # Increase attendance count
    data["students"][roll]["attended"] += 1

    save_data(data)

    return redirect(url_for("analytics", roll=roll))

# -----------------------------
# AI Analytics Page
# -----------------------------
@app.route("/analytics")
def analytics():

    roll = request.args.get("roll")

    if roll is None:
        return redirect(url_for("student"))

    data = load_data()

    if roll not in data["students"]:
        return "<h2>❌ Student not found.</h2>"

    student = data["students"][roll]

    attended = student["attended"]
    total = student["total"]

    attendance = round((attended / total) * 100, 2)

    # Calculate how many classes can still be missed
    max_absences = total - int(total * 0.75)
    current_absences = total - attended
    remaining = max(0, max_absences - current_absences)

    # Attendance if one more class is missed
    attendance_if_miss = round((attended / (total + 1)) * 100, 2)

    # AI Recommendation
    if attendance >= 90:
        message = "Excellent attendance! Keep it up."
    elif attendance >= 80:
        message = "Good attendance. Stay consistent."
    elif attendance >= 75:
        message = "Be careful. Avoid missing more classes."
    else:
        message = "Warning! Your attendance is below the required 75%."

    return render_template(
        "analytics.html",
        student=student,
        attendance=attendance,
        remaining=remaining,
        attendance_if_miss=attendance_if_miss,
        message=message
    )

# -----------------------------
# Run Application
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)