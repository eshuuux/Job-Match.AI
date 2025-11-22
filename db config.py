import sqlite3 as sql

con=sql.connect("Jobmatch.db")
c=con.cursor()
c.execute('''INSERT INTO jobs (title, company, location, skills_required, experience, description)
VALUES ("Python Developer", "TCS", "Pune", "python, flask, sql", "0-1 Year", "Looking for Python fresher with Flask experience.")''')
con.commit()
con.close()