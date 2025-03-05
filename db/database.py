import sqlite3

def getDatabase():
    con = sqlite3.connect("database.db")
    return con

def addOptimization(cur: sqlite3.Cursor):
    cur.execute("CREATE INDEX IF NOT EXISTS weigthsOptimization ON Weights(termId);")
    return

def removeOptimization(cur: sqlite3.Cursor):
    cur.execute("DROP INDEX IF EXISTS weigthsOptimization;")
    return

