from Assembler import locctr, lookahead, tokenval, match, startLine, X, pass1or2, symtable
import instfile


def sic():
    header()
    body()
    tail()
    print("----done----")


def header():
    global locctr, tokenval
    # print('header : ID')
    match('ID')
    # print('header : START')
    match('START')
    locctr = tokenval
    # print('header : NUM')
    match('NUM')


def tail():
    # print('tail : END')
    match('END')
    # print('tail : ID')
    match('ID')


def body():
    global startLine
    # print(lookahead)

    if lookahead == 'ID':
        # print('BOODY1 : ID')
        match('ID')
        # print(locctr, lookahead)
        startLine = False
        rest1()
        body()
    elif lookahead == 'f3':
        # print('BOODY2')
        stmt()
        body()


def rest1():
    if lookahead == 'f3':
        stmt()
    else:
        data()


def stmt():
    global locctr, startLine
    locctr += 3
    X = 0
    # print(locctr, lookahead)
    if (pass1or2 == 2):
        X = instfile.opcode[tokenval] << 16

    match('f3')
    if pass1or2 == 2:
        X += symtable[tokenval].att
        print(format(X, '#06x'))

    match('ID')
    index()


def index():
    global locctr
    if lookahead == ",":
        # print('INDEX : ,')
        match(",")
        # print('INDEX : REGISTER')
        match('REG')


def data():
    global locctr
    if lookahead == "WORD":
        locctr += 3
        # print('DATA : WORD')
        match("WORD")
        # print(tokenval)
        match("NUM")
    elif lookahead == "RESW":
        locctr += 3
        # print('DATA : RESW')
        match("RESW")
        # print('DATA : NUM')
        match("NUM")
    elif lookahead == "RESB":
        locctr += 3
        # print('DATA : RESP')
        match("RESB")

        # print('DATA : NUM')

        match("NUM")
    else:
        # print('DATA : BYTE')
        match("BYTE")
        rest2()


def rest2():
    global X
    if lookahead == 'HEX':
        # print('REST2 : HEX')

        match("HEX")
    else:
        # print('REST2 : STRING')
        # locctr += len(tokenval)
        # print(len(tokenval))
        match("STRING")
        if pass1or2 == 2:
            print(format(symtable[tokenval].att, '#06x'))