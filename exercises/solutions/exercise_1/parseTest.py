#!/usr/bin/python3
import sys

def parse(calculation):
    global operator,operand1,operand2
    tokenIndex = 0
    tokens = ["","",""]
    
    i=0
    while i < len(calculation):
        print("Token index: ",tokenIndex,"character[",i,": ]",calculation[i])
        if calculation[i] == " ":
            print("space")
            i+=1
            # A number consists of characters between 0 and 9 or the decimal point
        elif calculation[i] >= '0' and calculation[i] <= '9':
            print("number: ",calculation[i])
            tokens[tokenIndex]=tokens[tokenIndex]+calculation[i]
            i += 1
        
            # check that the decimal point was not already given, no 2 decimal points allowed
        elif calculation[i] == '.':
            print("dot")
            if tokens[tokenIndex].find('.') == -1:
                tokens[tokenIndex]= tokens[tokenIndex]+calculation[i]
                i += 1
            else:
                return False

                    
        # It can still be an operator. In this case the first operand must be non null 
        elif tokenIndex == 0 and not tokens[0] == "": 
            if calculation[i] == '+' or calculation[i] == '-' or calculation[i] == '*' or calculation[i] == '/' :
                print("Found operator: ",calculation[i])
                tokens[1]=tokens[1]+calculation[i]
                tokenIndex += 2
                i += 1
            else:
                return False
        else:
            return False
        
    print("First operand: ",tokens[0])
    print("Second operand: ",tokens[2])
    print("Operator: ",tokens[1])
    operand1 = float(tokens[0])
    operand2 = float(tokens[2])
    operator = tokens[1]
    return True

print(parse("4.3 + 5.3"))    
