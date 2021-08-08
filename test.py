import sys
import parser
import tokenize
import io
import re
from enum import Enum
from copy import deepcopy


"""
def usage():
    sys.exit("usage: ./computor \"equation to solve\"")

class ParsingToken:
    def __init__(self, tokType, value):
        self.value = value
        self.type = tokType

    def __str__(self):
        return 'type : {}\tvalue : {}'.format(self.type, self.value)
        #print(f'type : {self.type}\tvalue : {self.value}')


def opList():
    for name in tokenize.tok_name:
        print("number: ", name, " value: ", tokenize.tok_name[name])

def parsing(string):
    splitted = string.split("=")
    if len(splitted) != 2:
        sys.exit("Wrong Format")
    #ici rajouter la * avant les ( et rajouter les ^ 1 apres les X solo
    tmp = splitted[0].replace('X', '1')
    print(tmp)
#    try:
    print(eval(tmp))
#    except Exception as exc:
#        sys.exit("Equation is incorrect")
    #check we have only 1 equal
    
#    pattern = re.compile("^((\s*([0-9X])?|[\.\(\)\+\-\\\*\^])\s?)*$")
    pattern = re.compile("(([+-]?(?:[0-9]*[.])?[0-9]+)|(?:\s*)|([\+\-\*\\\^])|(X)|([\(\)]))+")
    if pattern.search(splitted[0]) is None or pattern.search(splitted[1]) is None:
        sys.exit("Wrong Format")
    list = pattern.search(splitted[0])
    print(list)

    try:
        left = tokenize.generate_tokens(io.StringIO(splitted[0]).readline)
        right = tokenize.generate_tokens(io.StringIO(splitted[1]).readline)
        leftVal = []
        rightVal = []
        #opList()
        for tokType, tokVal, _, _, _  in left:
            leftVal.append(ParsingToken(tokType, tokVal))
            print(tokType, tokVal)
        for tokType, tokVal, _, _, _  in right:
            rightVal.append(ParsingToken(tokType, tokVal))

    except Exception as exc:
        print("There was an error while parsing : ", exc)
        sys.exit()
#    for token in leftVal:
#        print(token)
    return left
"""
#recommence c'est trop complique ton truc

class Token:
    def __init__(self, value, power = 0):
        try :
            self.value = float(value)
            self.pow = power
            self.type = "number"
        except ValueError:
            if value == '+' or value == '-' or value == '/' or value == '*':
                self.value = value
                self.type = "operation"
            else:
                self.value = 1;
                self.pow = int(value[2:])
                self.type = "number"
    def __mul__(self, other):
        retval = Token(self.value * other.value)
        retval.type = "number"
        retval.pow = self.pow + other.pow
        return (retval)
    def __truediv__(self, other):
        retval = Token(self.value / other.value)
        retval.type = "number"
        retval.pow = self.pow - other.pow
        return (retval)

    def __str__(self):
        if self.type != "operation":
            return 'value : {}\tpower :{}\ttype : {}'.format(self.value, self.pow, self.type)
        return 'value : {}\ttype : {}'.format(self.value, self.type)
        

class Equation:
    def initialParsing(self, equationString):
        equationString = equationString.upper()
        splitted = equationString.split("=")
        self.left = splitted[0].split(' ')
        self.right = splitted[1].split(' ')
        self.left.remove("")
        self.right.remove("")

    def tokenization(self):
        tmp = []
        for value in self.left:
            tmp.append(Token(value))
        self.left = tmp.copy()
        tmp = []
        for value in self.right:
            tmp.append(Token(value))
        self.right = tmp

    def addHelpers(self, array):
        array.append(Token("+"))
        array.append(Token(0, 0))
        array.append(Token("+"))
        array.append(Token(0, 1))
        array.append(Token("+"))
        array.append(Token(0, 2))

    def simplifyPart(self, array):
        tmp = []
        for count, token in enumerate(array):
            if token.type == "operation" and token.value == "*":
                tmptok = tmp[-1] * array[count + 1] 
                tmp.pop()
                tmp.append(tmptok)
                array.remove(array[count + 1])
            elif token.type == "operation" and token.value == "/":
                if array[count + 1].value == 0:
                    sys.exit("Division par 0")
                else:
                    tmptok = tmp[-1] / array[count + 1] 
                    tmp.pop()
                    tmp.append(tmptok)
                    array.remove(array[count + 1])
            else:
                tmp.append(token)
        array.clear()
        for token in tmp:
            array.append(token)



    def simplify(self):
        self.simplifyPart(self.left)
        self.simplifyPart(self.right)
        return
                 
    def __init__(self, equation):
        self.initialParsing(equation)
        self.tokenization()
        self.simplify()
#       self.addHelpers(self.left) #add helpers to help calculate after
#       self.addHelpers(self.right)
        self.dump()

    def dump(self):
        print("Left :")
        for token in self.left:
            print(token)
        print("\nRight :")
        for token in self.right:
            print(token)



    def __str__(self):
        return 'left : {}\tright : {}'.format(self.left, self.right)

def parsing(string):
    equation = Equation(string)
#    print(equation)
 

def main(ac, av):
    if ac != 2:
        usage()
    equation = parsing(av[1])


if __name__ == "__main__":
        main(len(sys.argv), sys.argv)
