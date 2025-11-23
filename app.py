from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

# Function to connect to database
def get_connection():
    return sqlite3.connect("Jobmatch.db")

# ---------------- HOME PAGE ---------------- #
@app.route("/")
def home():
    con = get_connection()
    cur = con.cursor()
    
    # Get latest 6 jobs from database
    cur.execute("SELECT id, title, company, location FROM jobs ORDER BY id DESC LIMIT 6")
    jobs = cur.fetchall()

    con.close()
    
    # Send jobs to HTML page
    return render_template("homepage.html", jobs=jobs)

@app.route("/jobs")
def browse_jobs():
    con = get_connection()
    cur = con.cursor()
    
    cur.execute("SELECT id, title, company, location, type, salary FROM jobs ORDER BY id DESC")
    jobs = cur.fetchall()
    con.close()

    return render_template("browsejobs.html", jobs=jobs)


# ---------------- RUN APP ---------------- #
if __name__ == "__main__":
    app.run(debug=True)
