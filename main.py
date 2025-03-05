import sys
from parser.main_parser import is_parsed, parse, analyze
from retrieval.dbsearch import documentsWithTermSearch
from retrieval.parse import parseExpression
from retrieval.resolver import Resolver
from retrieval.server import createServer

if __name__== "__main__":
    if len(sys.argv) < 2:
        print("Not enough parameters. Please use 'analyze', 'force-analyze', 'test', 'server'.")
        exit(1)
    match sys.argv[1]:
        case "analyze":
            if not is_parsed():
                parse()
            analyze()
        case 'force-analyze':
            parse()
            analyze()
        case 'test':
            if len(sys.argv) < 3:
                print("Not enough parameters. Please enter text to analyze.")
                exit(1)

            parsed = parseExpression(sys.argv[2])
            print(parsed if parsed is not None else 'Error parsing')

            if parsed is not None:
                res1 = Resolver(parsed, defaultNotValue=0.1)
                res1.print()
                print(res1.solve())
        case 'server':
            createServer()
        case _:
            print("Unknown parameter")
            exit(1)
