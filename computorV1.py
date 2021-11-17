import sys
import tokenize
import io
import re
from copy import deepcopy
import copy
import operator
import math


def sqroot(value):
    if value == 0:
        return 0.0
    val = 0
    increment = 1
    while val * val < value and increment > 0.000000000000001:
        if (val + increment) * (val + increment) >  value:
            increment *= 0.1
        else:
            val += increment
    return val

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
                try:
                    if value[0] != "X":
                        sys.exit("I only work with X, not \'" + value[0] + "\'")
                    self.value = 1;
                    if len(value) == 1:
                        self.pow = 1
                    else:
                        self.pow = float(value[2:])
                    self.type = "number"
                except ValueError:
                    sys.exit("There was a problem when parsing")


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
        #print(self.value, " ", other.value, " ", retval)
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
    def __init__(self, equation):
            self.splitEqual(equation)
            self.tokenization()
            self.simplify()
            self.moveLeft()
            print(self)
            self.fuseLeft()
            print(self)
            self.orderLeft()
            self.reduceLeft()
            if (self.left[0].pow < 0):
                self.cancelNegative(self.left[0].pow)
                self.orderLeft()
                self.reduceLeft()
            else:
                self.shouldReduce()
            self.addHelpers(self.left)
            self.orderLeft()
            self.lastReduction()
            self.printReduced()
            self.solve()

    def shouldReduce(self):
        highest = 0
        lowest = 0
        highest = self.left[0].pow
        lowest = self.left[0].pow
        for token in self.left:
            if token.value != 0:
                if token.pow < lowest:
                    lowest = token.pow
                if token.pow > highest:
                    highest = token.pow
        if highest <= 2:
            return
        elif highest - lowest <= 2:
            self.cancelNegative(lowest)

    def findDegree(self):
        highest = 0
        lowest = 0
        for token in self.left:
            if token.value != 0:
                if token.pow < lowest:
                    lowest = token.pow
                if token.pow > highest:
                    highest = token.pow
                if (isinstance(token.pow, int) is False) and token.pow.is_integer() is False:
                    sys.exit("Some power expression isn't an integer, I can't solve.")
        if lowest < 0:
            sys.exit("Polynomial degree lower than 0: " + str(lowest) + ", can't solve.")
        self.degree = highest
        print("Polynomial degree: " + str(int(highest)))
        if highest > 2:
            sys.exit("The polynomial degree is strictly greater than 2, I can't solve.")

    def getDegreeValue(self, power):
        for token in self.left:
            if token.pow == power:
                return token.value

    def solveZero(self):
        if self.getDegreeValue(0) == 0:
            print("All real numbers are the solution")
        else:
            print(self.getDegreeValue(0), "≠ 0, Impossible to solve")
            
    def solveOne(self):
        print("The solution is :")
        x = self.getDegreeValue(1)
        value = self.getDegreeValue(0)
        if x > 0:
            solution = ((-value) / x)
        else:
            solution = (value / (-x))
        if solution.is_integer():
            print(str(int(solution)))
        else:
            print(solution)

    def solveTwoPositive(self):
        print("Discriminant is strictly positive, the two solutions are:")
        root = sqroot(self.discriminant)
        solution1 = ((-self.b) - root) / (2 * self.a)
        solution2 = ((-self.b) + root) / (2 * self.a)
        print(int(solution1) if solution1.is_integer() else solution1)
        print(int(solution2) if solution2.is_integer() else solution2)
        return

    def solveTwoNegative(self):
        root = sqroot(-(self.discriminant))
        real = ((-self.b) / (2 * self.a))
        imaginary = root / (2 * self.a)
        print("Discriminant is strictly negative, the two complex solutions are:")
        print(int(real) if real.is_integer() else real, end=' + ')
        print(int(imaginary) if imaginary.is_integer() else imaginary, end='')
        print(" * i")

        print(int(real) if real.is_integer() else real, end=' - ')
        print(int(imaginary) if imaginary.is_integer() else imaginary, end='')
        print(" * i")
        return

    def solveTwo(self):
        self.a = self.getDegreeValue(2)
        self.b = self.getDegreeValue(1)
        self.c = self.getDegreeValue(0)
        self.discriminant = (self.b * self.b) - 4 * (self.a * self.c)
        if self.discriminant > 0:
            self.solveTwoPositive()
            return
        elif self.discriminant < 0:
            self.solveTwoNegative()
            return
        else:
            print("Discriminant is 0, the only solution is:")
            value = (-self.b) / (2 * self.a)
            string = str(int(value)) if value.is_integer() else str(value)
            print(value)
            
    def solve(self):
        self.findDegree()
        if self.degree == 0:
            self.solveZero()
        elif self.degree == 1:
            self.solveOne()
        else:
            self.solveTwo()

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
        if (len(self.left) == 0):
            self.left.append(Token(0, 0))


    def printReduced(self):
        print("Reduced form: ", end='')
        firstprinted = 0
        for token in self.left:
            if (token.value != 0):
                sign =  '- ' if token.value < 0 else '+ '
                if firstprinted == 0:
                    if sign == '+ ':
                        sign = ''
                    else:
                        sign = '-'
                value = abs(token.value)
                try:
                    if value.is_integer():
                        print(sign+str(int(value)), end='')
                    else:
                        print(sign+str(value), end='')
                except Exception as e:
                    print(sign+str(value), end='')

                value = token.pow
                if value != 0:
                    if value == 1:
                        print('X ', end='')
                    else:
                        print('X^', end='')
                        if isinstance(value, int) or value.is_integer():
                            print(str(int(value)), end=' ')
                        else:
                            print(value, end=' ')
                else:
                    print(' ', end='')


                #penser a ne pas print le .0 si c'est pas un float
                firstprinted = 1
        if firstprinted == 0:
            sys.exit("0 = 0\nAll numbers are solution")
        print ("= 0")

    def addHelpers(self, array):
        array.append(Token(0, 0))
        array.append(Token(0, 1))
        array.append(Token(0, 2))


    def cancelNegative(self, negValue):
        toadd = 0
        if (len(self.left) == 1):
            toadd = 1 # to not multiply by 0
        for index, token in enumerate(self.left):
            self.left[index] = self.left[index] * Token(1, -negValue + toadd)

    def reduceLeft(self):
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
            if not (token.value == 0 and token.pow == 0):
                self.left.append(token)
        if (len(self.left) == 0):
            self.left.append(Token(0, 0))

    def orderLeft(self):
        self.left.sort(key=operator.attrgetter('pow'))

    def splitEqual(self, equationString):
        try:
            equationString = equationString.strip().upper()
            splitted = equationString.split("=")
            if len(splitted) != 2:
                if len(splitted) == 1:
                    sys.exit("Didn't found any \'=\' sign.")
                else:
                    sys.exit("Found too many \'=\' signs: " + str(len(splitted) - 1) + " were found.")
            self.left = splitted[0].strip().split(' ')
            self.right = splitted[1].strip().split(' ')

        except Exception as e:
            sys.exit("Something went wrong when parsing the equation", e)

    def tokenization(self):
        tmp = []
        for value in self.left:
            tmp.append(Token(value))
        self.left = tmp.copy()
        tmp = []
        for value in self.right:
            tmp.append(Token(value))
        self.right = tmp

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
        self.right.append(Token(0, 0))

    def fuseLeft(self):
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

    def __str__(self):
        return "left:{\n\t" + "\n\t".join(str(x) for x in self.left) + "\n}\nright:{\n\t" +  "\n\t".join(str(x) for x in self.right) + "\n}"


def usage():
    sys.exit("python3 computorV1.py 'equation'")

def main(ac, av):
    if ac != 2:
        usage()
    equation = Equation(av[1])

if __name__ == "__main__":
        main(len(sys.argv), sys.argv)
