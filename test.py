import sys
import parser
import tokenize
import io
import re
from enum import Enum
from copy import deepcopy
import copy
import operator


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
    def reverse(self):
        if self.type == "number":
            self.value *= -1
        else:
            if self.value == '-':
                self.value = '+'
            elif self.value == '+':
                self.value = '-'
        return (self)

    def fuse(self, other):
        if other is None or other.value == '+':
            return (copy.deepcopy(self))
        else:
            return(copy.deepcopy(self.reverse()))

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

    def __add__(self, other):
        retval = Token(self.value + other.value, self.pow)
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

    def moveLeft(self):
        if self.right:
            if self.right[0].value < 0:
                self.left.append(Token('+'))
            else:
                self.left.append(Token('-'))
            self.left.append(copy.deepcopy(self.right[0]))
            self.right.pop(0)
        for token in self.right:
            if token.type == 'number':
                self.left.append(token)
            else:
                self.left.append(token.reverse())
        self.right.clear()

    def fuseAll(self):
        tmp = []
        for count, token in enumerate(self.left):
            if (token.type == "number"):
                if (count > 0):
                    tmp.append(token.fuse(self.left[count - 1]))
                else:
                    tmp.append(token)
        self.left.clear()
        for token in tmp:
            self.left.append(token)

    def order(self):
        self.left.sort(key=operator.attrgetter('pow'))

    def lastReduction(self):
        tmp = []
        actual = copy.deepcopy(self.left[0])
        self.left.pop(0);
        for token in self.left:
            if (actual.pow == token.pow):
                actual = actual + token
            else:
                tmp.append(actual)
                actual = token
        tmp.append(actual)
        self.left.clear()
        for token in tmp:
            self.left.append(token)

    def printReduced(self):
        for token in self.left:
            if (token.value != 0):
                sign =  '- ' if token.value < 0 else '+ '
                print(sign+str(abs(token.value)) + " * X^"+ str(token.pow), end = ' ')
        print ("= 0")

    def reduce(self):
        self.simplify()
        self.moveLeft()
        self.addHelpers(self.left)
        self.fuseAll()
        self.order()
        self.lastReduction()
                 
    def __init__(self, equation):
        self.initialParsing(equation)
        self.tokenization()
        self.reduce()
        self.printReduced()

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
