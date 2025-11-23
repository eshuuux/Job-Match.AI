import sqlite3 as sql
con=sql.connect("Jobmatch.db")
c=con.cursor()
c.execute("ALTER TABLE Support RENAME COLUMN Phone TO Message")