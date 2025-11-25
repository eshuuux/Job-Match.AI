from flask import *
import os
import sqlite3 as sql

app = Flask(__name__)
app.secret_key = "super-secret-key-change-later"  # required for sessions + flash

# ---------------- DB CONNECTION ----------------
def get_connection():
    conn = sql.connect("jobmatch.db")
    conn.row_factory = sql.Row
    return conn

# ---------------- ROUTES ----------------
@app.route('/support')
def support():
    return render_template("contact.html")

@app.route("/change-password", methods=["GET", "POST"])
def change_password():
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    if request.method == "POST":
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if new_password != confirm_password:
            flash("Passwords do not match! Try again.", "danger")
            return redirect(url_for("change_password"))

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE users SET password = ? WHERE id = ?", (new_password, session["user_id"]))
        conn.commit()
        conn.close()

        flash("Password changed successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("change_password.html")



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

@app.route("/admin")
def admin():
    return render_template("admin.html")

# ---------------- MANAGE APPLICATIONS ----------------
@app.route("/admin/applications")
def admin_applications():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""SELECT applications.id, applications.name, applications.email, applications.resume,
                          jobs.title, jobs.company
                   FROM applications
                   JOIN jobs ON applications.job_id = jobs.id
                   ORDER BY applications.id DESC""")
    apps = cur.fetchall()
    conn.close()
    return render_template("admin_applications.html", apps=apps)


@app.route("/admin/applications/delete/<int:id>")
def delete_application(id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM applications WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash("Application removed successfully!", "danger")
    return redirect(url_for("admin_applications"))


# ---------------- MANAGE JOBS ----------------
@app.route('/admin/jobs')
def admin_jobs():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM jobs")
    jobs = cur.fetchall()
    conn.close()
    return render_template("admin_jobs.html", jobs=jobs)

@app.route('/admin/jobs/add', methods=['POST'])
def add_job():
    title = request.form['title']
    company = request.form['company']
    location = request.form['location']
    description = request.form['description']

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO jobs (title, company, location, description) VALUES (?,?,?,?)",
                (title, company, location, description))
    conn.commit()
    conn.close()

    flash("Job added successfully!", "success")
    return redirect(url_for('admin_jobs'))

@app.route('/admin/jobs/edit/<int:id>', methods=['POST'])
def edit_job(id):
    title = request.form['title']
    company = request.form['company']
    location = request.form['location']
    description = request.form['description']

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE jobs SET title=?, company=?, location=?, description=? WHERE id=?",
                (title, company, location, description, id))
    conn.commit()
    conn.close()
    flash("Job updated successfully!", "info")
    return redirect(url_for('admin_jobs'))

@app.route('/admin/jobs/delete/<int:id>')
def delete_job(id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM jobs WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash("Job deleted successfully!", "danger")
    return redirect(url_for('admin_jobs'))


# ---------------- MANAGE USERS ----------------
@app.route('/admin/users')
def admin_users():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    conn.close()
    return render_template("admin_users.html", users=users)

@app.route('/admin/users/edit/<int:id>', methods=['POST'])
def edit_user(id):
    name = request.form['name']
    email = request.form['email']
    skills = request.form['skills']

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET name=?, email=?, skills=? WHERE id=?", (name, email, skills, id))
    conn.commit()
    conn.close()
    flash("User updated successfully!", "info")
    return redirect(url_for('admin_users'))

@app.route('/admin/users/delete/<int:id>')
def delete_user(id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash("User deleted successfully!", "danger")
    return redirect(url_for('admin_users'))


# ---------------- SUBMIT APPLICATION ----------------
@app.route('/submit_application/<int:job_id>', methods=['POST'])
def submit_application(job_id):
    name = request.form.get('name')
    email = request.form.get('email')
    resume = request.files['resume']

    filename = resume.filename
    file_path = os.path.join("static/resumes", filename)
    resume.save(file_path)

    con = get_connection()
    c = con.cursor()
    c.execute("INSERT INTO applications (job_id, name, email, resume) VALUES (?, ?, ?, ?)",
              (job_id, name, email, filename))
    con.commit()
    con.close()

    flash("Application submitted successfully!", "success")
    return redirect("/dashboard")


# ---------------- REGISTER ----------------
@app.route("/registerform", methods=["POST"])
def registerform():
    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]   # simple
    skills = request.form["skills"]
    resume_file = request.files["resume"]

    filename = resume_file.filename
    resume_path = os.path.join("static/resumes", filename)
    resume_file.save(resume_path)

    con = get_connection()
    c = con.cursor()

    try:
        c.execute("INSERT INTO users (name, email, password, skills, resume) VALUES (?, ?, ?, ?, ?)",
                  (name, email, password, skills, filename))
        con.commit()
        flash("Registration successful! Please login.", "success")
    except:
        flash("Email already exists. Try another email.", "danger")

    con.close()
    return redirect(url_for("login"))


# ---------------- LOGIN ----------------
@app.route("/loginform", methods=["POST"])
def loginform():
    email = request.form.get("email")
    password = request.form.get("password")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cur.fetchone()
    conn.close()

    if user and user["password"] == password:   # direct compare
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
    cur.execute(
        "SELECT Jobs.title, Jobs.company FROM applications JOIN Jobs ON applications.job_id = Jobs.id WHERE applications.email = ?",
        (session.get("user_email"),))
    applications = cur.fetchall()
    con.close()
    return render_template("dashboard.html", applications=applications)


# ---------------- MAIN ----------------
if __name__ == "__main__":
    app.run(debug=True)