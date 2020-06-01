#!/usr/bin/python3
import sys

def parse(calculation):
    global operator,operand1,operand2
    calc = calculation.split()
#    print(calc, len(calc))
    if (len(calc) != 3):
        print("Wrong calculation string, please repeat!")
        return False
    operand1 = float(calc[0])
    operand2 = float(calc[2])

    operator = calc[1]
    if operator != '+' and operator != '-' and operator != '/' and operator != '*':
        return False
    return True

def plus():
    print(operand1,' + ',operand2,' = ',operand1+operand2)
    
def minus():
    print(operand1,' - ',operand2,' = ',operand1-operand2)     
    
def multiply():
    print(operand1,' * ',operand2,' = ',operand1*operand2)     
    
def divide():
    try:
        print(operand1,' / ',operand2,' = ',operand1/operand2)
    except ZeroDivisionError:
        print('Cannot divide by zero')

operations= {'+' : plus,
             '-' : minus,
             '*' : multiply,
             '/' : divide,}

global operator,operand1,operand2
while True:
    print ('Enter the calculation to be performed in the form: "operand1 operator operand2"')
    print ('Example: "5.3 + 4.2" or "1.4 * 7.9"');
    print ('Operation: ',end='')
    calculation = input()

#    print(calculation)

    if parse(calculation):
        print("String ok");
        operations[operator]()
        sys.exit()
           
