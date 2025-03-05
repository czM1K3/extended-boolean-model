import math
import fitz
from os import listdir
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer
from collections import Counter
from progress.bar import Bar

from db.database import addOptimization, getDatabase, removeOptimization

PROGRESS_SUFFIX='%(index)d/%(max)d - %(eta)ds'

# Parses pages of PDF to separate TXT files. Yes, it would be better to save them to database
def parse ():
    doc = fitz.open('data/harry_potter.pdf')
    num = 0
    bar = Bar("Parse PDF", max=len(doc), suffix=PROGRESS_SUFFIX)
    for page in doc:
        text_page=page.get_text() # pyright: ignore
        num += 1
        if len(text_page)>100:
            f = open(f"data/part_{num}.txt","w")
            f.write(text_page)
            f.close()
        bar.next()
    bar.finish()

# Checks if there are any txt files in data folder
def is_parsed():
    txt_files = [f for f in listdir("data") if f.endswith('.txt')]
    return bool(txt_files)

# Main analyzation of txt files
def analyze():
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')
    stop_words = set(stopwords.words('english'))
    porter=PorterStemmer()
    lemmatizer=WordNetLemmatizer()

    db = getDatabase()
    # db.set_trace_callback(print)
    cur = db.cursor()
    # Reset database. Yes, it would be better to have it in separate file
    cur.execute("DROP INDEX IF EXISTS termName")
    removeOptimization(cur)
    cur.execute("DROP TABLE IF EXISTS Documents;")
    cur.execute("DROP TABLE IF EXISTS Terms;")
    cur.execute("DROP TABLE IF EXISTS Weights;")
    cur.execute("CREATE TABLE Documents (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL);")
    cur.execute("CREATE TABLE Terms (id INTEGER PRIMARY KEY AUTOINCREMENT, value TEXT NOT NULL);");
    cur.execute("CREATE TABLE Weights (documentId INTEGER NOT NULL, termId INTEGER NOT NULL, weight REAL, count INTEGER NOT NULL, PRIMARY KEY(documentId, termId));")
    cur.execute("CREATE INDEX termName ON Terms(value);")


    files=listdir('data')
    bar1 = Bar("Processing", max=len(files), suffix=PROGRESS_SUFFIX)
    for file in files:
        if file.endswith('.txt'):
            cur.execute(f'INSERT INTO Documents (name) VALUES(?);', (file,))
            db.commit()
            documentId = cur.lastrowid

            f=open(f'data/{file}','r')
            text=f.read().lower()
            word_tokens = word_tokenize(text)
            filtered_sentence = [lemmatizer.lemmatize(word,'v') for word in word_tokens]
            filtered_sentence = [w for w in filtered_sentence if not w.lower() in stop_words]
            filtered_sentence = [w.lower() for w in filtered_sentence if w.isalpha()]
            filtered_sentence = [porter.stem(word) for word in filtered_sentence]

            values = Counter(filtered_sentence)
            for value, count in values.items():
                id = 0
                firstRaw = cur.execute(f'SELECT id FROM Terms WHERE value=?;', (value,))
                first = firstRaw.fetchone()
                if first is None:
                    cur.execute(f'INSERT INTO Terms (value) VALUES(?);', (value,))
                    id = cur.lastrowid
                else:
                    id = first[0]
                cur.execute(f'INSERT INTO Weights (documentId, termId, count) VALUES(?,?,?);', (documentId, id, count,))
        bar1.next()
    bar1.finish()

    db.commit()
    addOptimization(cur)
    db.commit()
    documentsRaw = cur.execute('SELECT COUNT(*) FROM Documents;')
    documentsCount = documentsRaw.fetchone()[0]

    weightsRaw = cur.execute('SELECT documentId, termId, count FROM Weights;')
    weights = weightsRaw.fetchall()
    bar2 = Bar("Calculating", max=len(weights), suffix=PROGRESS_SUFFIX)
    for weight in weights:
        documentId = weight[0]
        termId = weight[1]
        count = weight[2]

        maxDocumentRaw = cur.execute(f'SELECT MAX(count) FROM Weights WHERE termId=?;', (termId,))
        maxDocument = maxDocumentRaw.fetchone()[0]
        tf = count / maxDocument

        dfRaw = cur.execute(f'SELECT COUNT(*) FROM Weights WHERE termId=?;', (termId,))
        df = dfRaw.fetchone()[0]

        idf = math.log2(documentsCount / df)
        w = tf * idf
        cur.execute(f'UPDATE Weights SET weight=? WHERE documentId=? AND termId=?;', (w, documentId, termId,))
        # print(f'{documentId} {termId} {w}')
        bar2.next()
    bar2.finish()

    cur.execute('UPDATE Weights SET weight = CAST(weight AS REAL) / (SELECT MAX(weight) FROM Weights w);')

    db.commit()
