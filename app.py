
import sqlite3
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "campusflow-change-this-secret-key"

DB_NAME = "database.db"


# DATABASE SETUP
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'student'
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            location TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # Create a default administrator
    admin = conn.execute(
        "SELECT id FROM users WHERE email = ?",
        ("admin@campusflow.com",)
    ).fetchone()

    if not admin:
        conn.execute("""
            INSERT INTO users (name, email, password, role)
            VALUES (?, ?, ?, ?)
        """, (
            "Administrator",
            "admin@campusflow.com",
            generate_password_hash("Admin@123"),
            "admin"
        ))

    conn.commit()
    conn.close()


# LOGIN REQUIRED DECORATOR
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first.", "error")
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return wrapper


def admin_required(func):
    @wraps(func)
    @login_required
    def wrapper(*args, **kwargs):
        if session.get("role") != "admin":
            flash("Admin access required.", "error")
            return redirect(url_for("student_dashboard"))
        return func(*args, **kwargs)
    return wrapper


# HOME PAGE
@app.route("/")
def home():
    return render_template("index.html")


# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or len(password) < 8:
            flash("Enter all details. Password must be at least 8 characters.", "error")
            return redirect(url_for("register"))

        conn = get_db()

        try:
            conn.execute("""
                INSERT INTO users (name, email, password, role)
                VALUES (?, ?, ?, 'student')
            """, (name, email, generate_password_hash(password)))

            conn.commit()
            flash("Registration successful. Please login.", "success")
            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            flash("This email is already registered.", "error")

        finally:
            conn.close()

    return render_template("register.html")


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["name"] = user["name"]
            session["role"] = user["role"]

            if user["role"] == "admin":
                return redirect(url_for("admin_dashboard"))

            return redirect(url_for("student_dashboard"))

        flash("Invalid email or password.", "error")

    return render_template("login.html")


# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))


# STUDENT DASHBOARD
@app.route("/student")
@login_required
def student_dashboard():
    if session.get("role") != "student":
        return redirect(url_for("admin_dashboard"))

    conn = get_db()
    user_id = session["user_id"]

    stats = {
        "total": conn.execute(
            "SELECT COUNT(*) FROM complaints WHERE user_id=?",
            (user_id,)
        ).fetchone()[0],
        "pending": conn.execute(
            "SELECT COUNT(*) FROM complaints WHERE user_id=? AND status='Pending'",
            (user_id,)
        ).fetchone()[0],
        "progress": conn.execute(
            "SELECT COUNT(*) FROM complaints WHERE user_id=? AND status='In Progress'",
            (user_id,)
        ).fetchone()[0],
        "resolved": conn.execute(
            "SELECT COUNT(*) FROM complaints WHERE user_id=? AND status='Resolved'",
            (user_id,)
        ).fetchone()[0]
    }

    complaints = conn.execute("""
        SELECT * FROM complaints
        WHERE user_id=?
        ORDER BY id DESC LIMIT 5
    """, (user_id,)).fetchall()

    conn.close()

    return render_template(
        "student_dashboard.html",
        stats=stats,
        complaints=complaints
    )


# SUBMIT COMPLAINT
@app.route("/submit", methods=["GET", "POST"])
@login_required
def submit_complaint():
    if session.get("role") != "student":
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "")
        location = request.form.get("location", "").strip()
        priority = request.form.get("priority", "")

        if not all([title, description, category, location]):
            flash("Please fill in all fields.", "error")
            return redirect(url_for("submit_complaint"))

        if category not in ["Electrical", "Cleanliness", "Wi-Fi", "Furniture", "Other"]:
            flash("Invalid category.", "error")
            return redirect(url_for("submit_complaint"))

        if priority not in ["Low", "Medium", "High"]:
            flash("Invalid priority.", "error")
            return redirect(url_for("submit_complaint"))

        conn = get_db()
        conn.execute("""
            INSERT INTO complaints
            (user_id, title, description, category, location, priority)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            session["user_id"], title, description,
            category, location, priority
        ))
        conn.commit()
        conn.close()

        flash("Your complaint has been submitted!", "success")
        return redirect(url_for("my_complaints"))

    return render_template("submit_complaint.html")


# MY COMPLAINTS
@app.route("/complaints")
@login_required
def my_complaints():
    if session.get("role") != "student":
        return redirect(url_for("admin_dashboard"))

    status = request.args.get("status", "")

    conn = get_db()

    if status in ["Pending", "In Progress", "Resolved"]:
        complaints = conn.execute("""
            SELECT * FROM complaints
            WHERE user_id=? AND status=?
            ORDER BY id DESC
        """, (session["user_id"], status)).fetchall()
    else:
        complaints = conn.execute("""
            SELECT * FROM complaints
            WHERE user_id=?
            ORDER BY id DESC
        """, (session["user_id"],)).fetchall()

    conn.close()

    return render_template(
        "my_complaints.html",
        complaints=complaints
    )


# ADMIN DASHBOARD
@app.route("/admin")
@admin_required
def admin_dashboard():
    conn = get_db()

    stats = {
        "total": conn.execute(
            "SELECT COUNT(*) FROM complaints"
        ).fetchone()[0],
        "pending": conn.execute(
            "SELECT COUNT(*) FROM complaints WHERE status='Pending'"
        ).fetchone()[0],
        "progress": conn.execute(
            "SELECT COUNT(*) FROM complaints WHERE status='In Progress'"
        ).fetchone()[0],
        "resolved": conn.execute(
            "SELECT COUNT(*) FROM complaints WHERE status='Resolved'"
        ).fetchone()[0]
    }

    status = request.args.get("status", "")
    search = request.args.get("search", "").strip()

    query = """
        SELECT complaints.*, users.name AS student_name,
        users.email AS student_email
        FROM complaints
        JOIN users ON complaints.user_id = users.id
        WHERE 1=1
    """
    params = []

    if status in ["Pending", "In Progress", "Resolved"]:
        query += " AND complaints.status=?"
        params.append(status)

    if search:
        query += """ AND (
            complaints.title LIKE ? OR
            complaints.location LIKE ? OR
            users.name LIKE ?
        )"""
        term = f"%{search}%"
        params.extend([term, term, term])

    query += " ORDER BY complaints.id DESC"

    complaints = conn.execute(query, params).fetchall()
    conn.close()

    return render_template(
        "admin_dashboard.html",
        stats=stats,
        complaints=complaints
    )


# ADMIN UPDATES COMPLAINT STATUS
@app.route("/update/<int:complaint_id>", methods=["POST"])
@admin_required
def update_status(complaint_id):
    status = request.form.get("status")

    if status not in ["Pending", "In Progress", "Resolved"]:
        flash("Invalid status.", "error")
        return redirect(url_for("admin_dashboard"))

    conn = get_db()
    conn.execute(
        "UPDATE complaints SET status=? WHERE id=?",
        (status, complaint_id)
    )
    conn.commit()
    conn.close()

    flash("Complaint status updated.", "success")
    return redirect(url_for("admin_dashboard"))


# START APPLICATION
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
