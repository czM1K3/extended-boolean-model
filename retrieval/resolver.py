from math import sqrt
import re
from nltk.stem import PorterStemmer, WordNetLemmatizer
from retrieval.dbsearch import documentsNot, documentsWithTermSearch

porter=PorterStemmer() 
lemmatizer=WordNetLemmatizer()

class Resolver:
    def __init__(self, expression: str, isNot=False, defaultNotValue=0.5) -> None:
        self.parts = []
        self.isNot = isNot
        self.defaultNotValue = defaultNotValue

        if re.search('^[\\(!]', expression) is None:
            self.type = 'final'
            self.word = expression
            return

        self.type = 'wrapper'
        nextNot = False
        indexOfStart = 0
        depth = 0
        for i in range(len(expression)):
            if expression[i] == '(':
                if depth == 0:
                    indexOfStart = i + 1
                depth += 1
            elif expression[i] == ')':
                depth -= 1
                if depth == 0:
                    self.parts.append(Resolver(expression[indexOfStart:i], nextNot, defaultNotValue))
                    nextNot = False
            elif expression[i] == '!':
                if depth == 0:
                    nextNot = True
            elif expression[i] == '|' and depth == 0:
                self.type = 'or'
            elif expression[i] == '&' and depth == 0:
                self.type = 'and'
        return

    def solve(self):
        aboutToSend: dict = {}
        global lemmatizer
        global porter
        if self.type == 'final':
            word = porter.stem(lemmatizer.lemmatize(self.word,'v'))
            aboutToSend = documentsWithTermSearch(word)
        elif self.type == 'or':
            all = []
            setIds = set()
            for x in self.parts:
                solved = x.solve()
                all.append(solved)
                for key in solved:
                    setIds.add(key)
            result = {}
            for id in setIds:
                sum = 0
                for doc in all:
                    value = 0
                    if id in doc:
                        value = doc[id]
                    sum += pow(value, 2)
                sum /= len(all)
                value = sqrt(sum)
                result[id] = value
            aboutToSend = result
        elif self.type == 'and':
            all = []
            allKeys = list()
            for x in self.parts:
                solved = x.solve()
                all.append(solved)
                allKeys.append(solved.keys())
            setIds = allKeys[0]
            for x in range(1, len(allKeys)):
                setIds &= allKeys[x]
            result = {}
            for id in setIds:
                sum = 0
                for doc in all:
                    value = doc[id]
                    sum += pow(1 - value, 2)
                sum /= len(all)
                value = 1 - sqrt(sum)
                result[id] = value
            aboutToSend = result
        else:
            aboutToSend = self.parts[0].solve()

        if self.isNot:
            keyList = set(aboutToSend.keys())
            return documentsNot(keyList, self.defaultNotValue)
        return aboutToSend

    def print(self, prefix=''):
        print(prefix + '-' + self.type + ' ' + str(len(self.parts)) + (' NOT' if self.isNot else ''))
        if self.type == 'final':
            print(prefix + ' ' + self.word)
            return
        for x in self.parts:
            x.print(prefix + ' ')

