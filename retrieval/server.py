from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
from urllib.parse import parse_qs
from nltk.corpus.reader import json
from retrieval.dbsearch import documentsNot, getDocumentById
from retrieval.parse import parseExpression
from retrieval.resolver import Resolver
from db.database import addOptimization, removeOptimization, getDatabase

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        match parsed.path:
            case "/query":
                try:
                    captured_value = parse_qs(parsed.query)['query'][0]
                    parsed = parseExpression(captured_value)

                    if parsed is not None:
                        resolver = Resolver(parsed, defaultNotValue=0.1)
                        res = resolver.solve()
                        arr = []
                        for key in res:
                            arr.append({'documentId': key, 'weight': res[key]})
                        self.send_response(200)
                        self.send_header( "Access-Control-Allow-Origin", "*")
                        self.end_headers()
                        self.wfile.write(bytes(json.dumps(arr), "utf-8"))
                    else:
                        self.send_response(400)
                        self.send_header( "Access-Control-Allow-Origin", "*")
                        self.end_headers()
                        self.wfile.write(bytes("Expression is not valid", "utf-8"))
                except:
                    self.send_response(400)
                    self.send_header( "Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(bytes("Something went wrong", "utf-8"))
            case "/get":
                try:
                    captured_value = int(parse_qs(parsed.query)['documentId'][0])

                    documentName = getDocumentById(captured_value)
                    if documentName is None:
                        self.send_response(400)
                        self.send_header( "Access-Control-Allow-Origin", "*")
                        self.end_headers()
                        self.wfile.write(bytes("Document not found", "utf-8"))
                        return

                    f=open(f'data/{documentName}','r')
                    text=f.read()

                    self.send_response(200)
                    self.send_header( "Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(bytes(text, "utf-8"))
                except:
                    self.send_response(400)
                    self.send_header( "Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(bytes("Something went wrong", "utf-8"))
        pass

    def do_POST(self):
        parsed = urlparse(self.path)
        match parsed.path:
            case "/optimization-on":
                db = getDatabase()
                cur = db.cursor()
                addOptimization(cur)
                self.send_response(200)
                self.send_header( "Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(bytes("OK", "utf-8"))
            case "/optimization-off":
                db = getDatabase()
                cur = db.cursor()
                removeOptimization(cur)
                self.send_response(200)
                self.send_header( "Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(bytes("OK", "utf-8"))
        pass


def createServer():
    httpd = HTTPServer(('0.0.0.0', 8000), MyHandler)
    print("Server is listening at http://localhost:8000")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Quiting server")
