import re
# I'm sorry for this. It just works.

def parseExpression(expression: str):
    expressionPreValidation = prevalidationChanges(expression)
    if not isExpressionValid1(expressionPreValidation):
        # print("Expression is not valid 1")
        return None
    prettified = prettifyExpression(expressionPreValidation)
    if not isExpressionValid2(prettified):
        # print("Expression is not valid 2")
        return None
    bracketed = bracketsPriorities(prettified)
    return bracketed

def prevalidationChanges(expression: str) -> str:
    loweredExpression = expression.lower()
    extraSpaces1 = re.sub('\\(', ' ( ', loweredExpression)
    extraSpaces2 = re.sub('\\)', ' ) ', extraSpaces1)
    removedMultipleSpaces = re.sub(' +', ' ', extraSpaces2)
    return removedMultipleSpaces


def isExpressionValid1(expression: str) -> bool:
    result = re.search('^[a-z\\ \\(\\)]*$', expression)
    if result is None:
        return False
    parentheses = 0
    for x in expression:
        if x == "(":
            parentheses += 1
        elif x == ")":
            parentheses -= 1
            if parentheses < 0:
                return False
    if parentheses != 0:
        return False
    if ' and and ' in expression or ' and or ' in expression or ' or or ' in expression or ' or and ' in expression:
        return False
    return True

def isExpressionValid2(expression: str) -> bool:
    if ' ' in expression:
        return False
    if '(&' in expression or '(|' in expression or '&)' in expression or '|)' in expression:
        return False
    if re.search('[a-z]\\(', expression) is not None:
        return False
    if re.search('\\)[a-z]', expression) is not None:
        return False
    return True

def prettifyExpression(expression: str) -> str:
    replaced1 = expression\
        .replace(' not ', ' !')\
        .replace(' not(',' !(')\
        .replace(' and ','&')\
        .replace(' or ', '|')\
        .replace(' (' ,'(')\
        .replace('( ', '(')\
        .replace(' )', ')')\
        .replace(') ', ')')
    replaced2 = re.sub(r'^not\ ', '!', replaced1)
    replaced3 = re.sub(r'^not\(', '!(', replaced2)
    return replaced3

# I refuse to comment on this, it just works :D
def bracketsPriorities(expression: str) -> str:
    changedExpression = "(" + expression + ")"
    maxDepth = changedExpression.count('(') + 1
    for targetDepth in reversed(range(0, maxDepth)):
        currentDepth = 0
        startOfCurrent = -1
        i = 0
        while i < len(changedExpression):
            if changedExpression[i] == '(':
                currentDepth += 1
                if targetDepth == currentDepth:
                    startOfCurrent = i + 1
            elif changedExpression[i] == ')':
                if targetDepth == currentDepth:
                    changedExpression = changedExpression[:startOfCurrent] + "(" + changedExpression[startOfCurrent:i] + ")" + changedExpression[i:]
                    i += 2
                    startOfCurrent = -1
                currentDepth -= 1
            elif changedExpression[i] == "|":
                if targetDepth == currentDepth:
                    changedExpression = changedExpression[:startOfCurrent] + "(" + changedExpression[startOfCurrent:i] + ")" + changedExpression[i:]
                    i += 2
                    startOfCurrent = i + 1
            i += 1
    bracketed = re.sub('([a-z]+)','(\\1)', changedExpression)
    return bracketed
