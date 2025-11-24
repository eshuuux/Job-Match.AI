import sqlite3 as sql
con=sql.connect("Jobmatch.db")
c=con.cursor()
c.execute("CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,email TEXT UNIQUE NOT NULL,password TEXT NOT NULL,skills TEXT,resume TEXT)")
con.commit()
con.close()