from flask import *
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sqlite3 as sql
app = Flask(__name__)
app.secret_key = "super-secret-key-change-later"  # required for sessions + flash

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
    return render_template("apply.html")

# Function to connect to database
def get_connection():
    return sql.connect("Jobmatch.db")

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
    if request.method=="POST":
        name=request.form['name']
        email=request.form['email']
        message=request.form['message']
        con= get_connection()
        c=con.cursor()
        c.execute("INSERT INTO Support (name,email,message) values(?,?,?)",(name,email,message))
        con.commit()
        return redirect("/")
    else:
        return render_template("contact.html")
    
@app.route('/apply')
def no_job():
    return redirect('/jobs')


import sqlite3

@app.route('/apply/<int:job_id>')
def apply_job(job_id):
    conn = sqlite3.connect("Jobmatch.db")   # your DB file name
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Jobs WHERE id = ?", (job_id,))
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

    c.execute("""INSERT INTO applications (job_id, name, email, resume) VALUES (?, ?, ?, ?)""", (job_id, name, email, file_path))
    con.commit()
    con.close()
    return "Application Submitted Successfully!"

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
        c.execute("INSERT INTO users (name, email, password, skills, resume)VALUES (?, ?, ?, ?, ?)", (name, email, hashed_password, skills, resume_path))
        con.commit()
        flash("Registration successful! Please login.", "success")
    except:
        flash("Email already exists. Try another email.", "danger")

    con.close()
    return redirect(url_for("login"))

def get_connection():
    conn = sql.connect("Jobmatch.db")
    conn.row_factory = sql.Row
    return conn


@app.route("/loginform", methods=["GET", "POST"])
def loginform():
    if request.method == "POST":
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

            flash("Logged in successfully!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid email or password!", "danger")

    return render_template("login.html")


# ---------------- LOGOUT ROUTE ----------------
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect(url_for("login"))


# ---------------- PROTECTED ROUTE EXAMPLE ----------------
# @app.route("/dashboard")
# def dashboard():
#     if "user_id" not in session:
#         flash("Please login first.", "warning")
#         return redirect(url_for("login"))

#     return f"Welcome {session['user_name']}!"


if __name__ == "__main__":
    app.run(debug=True)
