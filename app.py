from flask import *
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sqlite3 as sql

app = Flask(__name__)
app.secret_key = "super-secret-key-change-later"  # required for sessions + flash


# ---------------- DB CONNECTION ----------------
def get_connection():
    conn = sql.connect("Jobmatch.db")
    conn.row_factory = sql.Row
    return conn


# ---------------- ROUTES ----------------
@app.route('/support')
def support():
    return render_template("contact.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/register')
def register():
    return render_template("register.html")

@app.route('/apply')
def apply():
    return redirect('/jobs')


@app.route("/")
def home():
    con = get_connection()
    c = con.cursor()
    c.execute("SELECT id, title, company, location FROM jobs ORDER BY id DESC LIMIT 6")
    jobs = c.fetchall()
    con.close()
    return render_template("home.html", jobs=jobs)


@app.route("/jobs")
def browse_jobs():
    con = get_connection()
    c = con.cursor()
    c.execute("SELECT id, title, company, location, type, salary FROM jobs ORDER BY id DESC")
    jobs = c.fetchall()
    con.close()
    return render_template("browsejobs.html", jobs=jobs)


@app.route('/supportform', methods=["POST"])
def supportform():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']

    con = get_connection()
    c = con.cursor()
    c.execute("INSERT INTO Support (name,email,message) VALUES (?, ?, ?)", (name, email, message))
    con.commit()
    con.close()
    flash("Message sent successfully!", "success")
    return redirect("/")


@app.route('/apply/<int:job_id>')
def apply_job(job_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
    job = cursor.fetchone()
    conn.close()
    return render_template("apply.html", job=job)


@app.route('/submit_application/<int:job_id>', methods=['POST'])
def submit_application(job_id):
    name = request.form.get('name')
    email = request.form.get('email')
    resume = request.files['resume']

    file_path = f"applied/{resume.filename}"
    resume.save(file_path)

    con = get_connection()
    c = con.cursor()
    c.execute("""INSERT INTO applications (job_id, name, email, resume) VALUES (?, ?, ?, ?)""",
              (job_id, name, email, file_path))
    con.commit()
    con.close()
    flash("Application submitted successfully!", "success")
    return redirect("/jobs")


@app.route("/registerform", methods=["POST"])
def registerform():
    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]
    skills = request.form["skills"]
    resume_file = request.files["resume"]

    filename = resume_file.filename
    resume_path = os.path.join("users", filename)
    resume_file.save(resume_path)

    hashed_password = generate_password_hash(password)

    con = get_connection()
    c = con.cursor()

    try:
        c.execute("INSERT INTO users (name, email, password, skills, resume) VALUES (?, ?, ?, ?, ?)",
                  (name, email, hashed_password, skills, resume_path))
        con.commit()
        flash("Registration successful! Please login.", "success")
    except:
        flash("Email already exists. Try another email.", "danger")

    con.close()
    return redirect(url_for("login"))


@app.route("/loginform", methods=["POST"])
def loginform():
    email = request.form.get("email")
    password = request.form.get("password")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cur.fetchone()
    conn.close()

    if user and check_password_hash(user["password"], password):
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        session["user_email"] = user["email"]
        session["skills"] = user["skills"]
        session["resume"] = user["resume"]

        flash("Logged in successfully!", "success")
        return redirect(url_for("home"))
    else:
        flash("Invalid email or password!", "danger")
        return redirect(url_for("login"))




# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect(url_for("login"))


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user_email" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        SELECT Jobs.title, Jobs.company
        FROM applications
        JOIN Jobs ON applications.job_id = Jobs.id
        WHERE applications.email = ?
    """, (session.get("user_email"),))
    applications = cur.fetchall()
    con.close()

    return render_template("dashboard.html", applications=applications)


@app.route("/change-password", methods=["GET", "POST"])
def change_password():
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    if request.method == "POST":
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT password FROM users WHERE id = ?", (session["user_id"],))
        user_pass = cur.fetchone()[0]

        if not check_password_hash(user_pass, current_password):
            flash("Incorrect current password", "danger")
        elif new_password != confirm_password:
            flash("New passwords do not match", "danger")
        else:
            hashed = generate_password_hash(new_password)
            cur.execute("UPDATE users SET password = ? WHERE id = ?", (hashed, session["user_id"]))
            conn.commit()
            flash("Password updated successfully!", "success")

        conn.close()
        return redirect(url_for("dashboard"))

    return render_template("change_password.html")



# ---------------- MAIN ----------------
if __name__ == "__main__":
    app.run(debug=True)
