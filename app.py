from flask import *
import sqlite3 as sql
app = Flask(__name__)

@app.route('/support')
def support():
    return render_template("contact.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/contact')
def about():
    return render_template("contact.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/register')
def register():
    return render_template("register.html")

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

if __name__ == "__main__":
    app.run(debug=True)
