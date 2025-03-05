from db.database import getDatabase

def searchTermByName(term):
    db = getDatabase()
    cur = db.cursor()
    rowRaw = cur.execute(f'SELECT t.id FROM Terms t WHERE value=?;', (term,))
    row = rowRaw.fetchone()
    if row is None:
        return None
    return row[0]


def documentsWithTermSearch(term) -> dict:
    termId = searchTermByName(term)
    if termId is None:
        return {}
    db = getDatabase()
    cur = db.cursor()
    rowsRaw = cur.execute(f'SELECT w.documentId, w.weight  FROM Weights w WHERE w.termId=?;', (termId,))
    rows = rowsRaw.fetchall()
    result = {key: value for key, value in rows}
    return result

def documentsNot(ids: set, notValue: float) -> dict:
    db = getDatabase()
    cur = db.cursor()
    rowsRaw = cur.execute(f'SELECT d.id FROM Documents d;')
    rows = rowsRaw.fetchall()

    allIds = set([row[0] for row in rows])
    notted = allIds.difference(ids)
    return {key: notValue for key in notted}

def getDocumentById(id):
    db = getDatabase()
    cur = db.cursor()
    rowsRaw = cur.execute(f'SELECT d.name FROM Documents d WHERE d.id=?;', (id,))
    row = rowsRaw.fetchone()
    if row is None:
        return None
    return row[0]

