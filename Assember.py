import re
import instfile


class Entry:
    def __init__(self, string, token, attribute):
        self.string = string
        self.token = token
        self.att = attribute



symtable = []


# print(symtable[12].string + ' ' + str(symtable[12].token) + ' ' + str(symtable[12].att))

def lookup(s):
    for i in range(0, symtable.__len__()):
        if s == symtable[i].string:
            return i
    return -1


def insert(s, t, a):
    symtable.append(Entry(s, t, a))
    return symtable.__len__() - 1


def init():
    for i in range(0, instfile.inst.__len__()):
        insert(instfile.inst[i], instfile.token[i], instfile.opcode[i])
    for i in range(0, instfile.directives.__len__()):
        insert(instfile.directives[i], instfile.dirtoken[i], instfile.dircode[i])


file = open('input.sic', 'r')
filecontent = []
bufferindex = 0
tokenval = 0
lineno = 1
pass1or2 = 1
locctr = 0
lookahead = ''
defID = True
startLine = True
idindex = 0
startAddres = 1
totalSize = 0
inst = 0
formatAddress = 0

Xbit4set = 0x800000
Bbit4set = 0x400000
Pbit4set = 0x200000
Ebit4set = 0x100000

Nbitset = 2
Ibitset = 1

Xbit3set = 0x8000
Bbit3set = 0x4000
Pbit3set = 0x2000
Ebit3set = 0x1000


def is_hex(s):
    if s[0:2].upper() == '0X':
        try:
            int(s[2:], 16)
            return True
        except ValueError:
            return False
    else:
        return False


def lexan():
    global filecontent, tokenval, lineno, bufferindex, locctr, startLine

    while True:
        # if filecontent == []:
        if len(filecontent) == bufferindex:
            return 'EOF'
        elif filecontent[bufferindex] == '%':
            startLine = True
            while filecontent[bufferindex] != '\n':
                bufferindex = bufferindex + 1
            lineno += 1
            bufferindex = bufferindex + 1
        elif filecontent[bufferindex] == '\n':
            startLine = True
            # del filecontent[bufferindex]
            bufferindex = bufferindex + 1
            lineno += 1
        else:
            break
    if filecontent[bufferindex].isdigit():
        tokenval = int(filecontent[bufferindex])  # all number are considered as decimals
        # del filecontent[bufferindex]
        bufferindex = bufferindex + 1
        return ('NUM')
    elif is_hex(filecontent[bufferindex]):
        tokenval = int(filecontent[bufferindex][2:], 16)  # all number starting with 0x are considered as hex
        # del filecontent[bufferindex]
        bufferindex = bufferindex + 1
        return ('NUM')
    elif filecontent[bufferindex] in ['+', '#', ',', '@', '=']:
        c = filecontent[bufferindex]
        # del filecontent[bufferindex]
        bufferindex = bufferindex + 1
        return (c)
    else:
        # check if there is a string or hex starting with C'string' or X'hex'
        if (filecontent[bufferindex].upper() == 'C') and (filecontent[bufferindex + 1] == '\''):
            bytestring = ''
            bufferindex += 2
            while filecontent[bufferindex] != '\'':  # should we take into account the missing ' error?
                bytestring += filecontent[bufferindex]
                bufferindex += 1
                if filecontent[bufferindex] != '\'':
                    bytestring += ' '
            bufferindex += 1
            bytestringvalue = "".join("%02X" % ord(c) for c in bytestring)
            bytestring = '_' + bytestring
            p = lookup(bytestring)
            if p == -1:
                p = insert(bytestring, 'STRING', bytestringvalue)  # should we deal with literals?
            tokenval = p
        elif (filecontent[bufferindex] == '\''):  # a string can start with C' or only with '
            bytestring = ''
            bufferindex += 1
            while filecontent[bufferindex] != '\'':  # should we take into account the missing ' error?
                bytestring += filecontent[bufferindex]
                bufferindex += 1
                if filecontent[bufferindex] != '\'':
                    bytestring += ' '
            bufferindex += 1
            bytestringvalue = "".join("%02X" % ord(c) for c in bytestring)
            bytestring = '_' + bytestring
            p = lookup(bytestring)
            if p == -1:
                p = insert(bytestring, 'STRING', bytestringvalue)  # should we deal with literals?
            tokenval = p
        elif (filecontent[bufferindex].upper() == 'X') and (filecontent[bufferindex + 1] == '\''):
            bufferindex += 2
            bytestring = filecontent[bufferindex]
            bufferindex += 2
            # if filecontent[bufferindex] != '\'':# should we take into account the missing ' error?

            bytestringvalue = bytestring
            if len(bytestringvalue) % 2 == 1:
                bytestringvalue = '0' + bytestringvalue
            bytestring = '_' + bytestring
            p = lookup(bytestring)
            if p == -1:
                p = insert(bytestring, 'HEX', bytestringvalue)  # should we deal with literals?
            tokenval = p
        else:
            p = lookup(filecontent[bufferindex].upper())
            if p == -1:
                if startLine == True:
                    p = insert(filecontent[bufferindex].upper(), 'ID', locctr)  # should we deal with case-sensitive?
                else:
                    p = insert(filecontent[bufferindex].upper(), 'ID', -1)  # forward reference
            else:
                if (symtable[p].att == -1) and (startLine == True):
                    symtable[p].att = locctr
            tokenval = p
            # del filecontent[bufferindex]
            bufferindex = bufferindex + 1
        return (symtable[p].token)


def error(s):
    global lineno
    print('line ' + str(lineno) + ': ' + s)


def match(token):
    global lookahead
    if lookahead == token:
        lookahead = lexan()
    else:
        error('Syntax error')


def checkindex():
    global bufferindex, symtable, tokenval
    if lookahead == ',':
        match(',')
        if symtable[tokenval].att != 1:
            error('index regsiter should be X')
        match('REG')
        return True
    return False


def parse():
    header()
    body()
    tail()


def header():
    global startAddres, locctr, tokenval, totalSize, symtable, idindex, pass1or2, lookahead, startLine
    startLine = True
    lookahead = lexan()
    idindex = tokenval
    match('ID')
    match('START')
    startAddres = locctr = symtable[idindex].att = tokenval
    match('NUM')
    if pass1or2 == 2:
        print('H ', symtable[idindex].string, format(tokenval, '06X'), format(totalSize, '06X'))
        # print("H ", symtable[idindex].string, (format(startAddres, '06X')), format(totalSize, '06X'))


def tail():
    global totalSize, locctr, startAddres, tokenval, idindex
    idindex = tokenval
    match('END')
    totalSize = locctr - startAddres
    if pass1or2 == 2:
        print('E ', format(symtable[tokenval].att,'06X'))
    match('ID')


def body():
    global inst, pass1or2, lookahead, startLine
    startLine = True
    if lookahead == 'ID':
        if pass1or2 == 2:
            inst = 0
        match('ID')
        startLine = False
        rest1()
        body()
    if lookahead == 'f3':
        startLine = False
        if pass1or2 == 2:
            inst = 0
        stmt()
        body()


def rest1():
    global lookahead
    if lookahead == 'f3':
        stmt()
    else:
        data()


def stmt():
    global locctr, inst, idindex, symtable, pass1or2, lookahead
    token = tokenval
    match('f3')
    locctr += 3
    if pass1or2 == 2:
        inst = symtable[token].att << 16

    if not (symtable[token].string == 'RSUB'):
        if pass1or2 == 2:
            inst += symtable[tokenval].att
        match('ID')
        index()

    if pass1or2 == 2:
        print('T ', format(locctr - 3, '06X'), '03', format(inst, '06X'))


def index():
    global pass1or2, inst, lookahead
    if lookahead == ',':
        match(",")
        match('REG')
        if pass1or2 == 2:
            inst += Xbit3set


def data():
    global locctr, lookahead, inst, tokenval

    if lookahead == 'WORD':
        match('WORD')
        inst = tokenval
        locctr += 3
        match('NUM')
        if pass1or2 == 2: ###
            print('T ', format(locctr - 3, '06X'), '03', format(inst, '06X'))

    elif lookahead == 'RESW':
        match('RESW')
        inst = symtable[tokenval].att
        locctr += tokenval*3
        match('NUM')
        if pass1or2 == 2: ###
            print(int('T ', format(locctr - 3, '06X'), '03', format(inst, '06X')))

    elif lookahead == 'RESB':
        match('RESB')
        inst = symtable[tokenval].att
        locctr += tokenval
        match('NUM')
        if pass1or2 == 2: ###
            print('T ', format(locctr - 3, '06X'), '03', format(inst, '06X'))
    elif lookahead == 'BYTE':
        match('BYTE')
        rest2()
    else:
        error("Syntax error")


def rest2():
    global locctr
    if lookahead == 'STRING':
        match('STRING')
        locctr += len(symtable[tokenval].string)
    elif lookahead == 'HEX':
        locctr += int(len(symtable[tokenval].string) / 2)
        match('HEX')

    else:
        error('Syntax error')


def main():
    global file, filecontent, locctr, pass1or2, bufferindex, lineno
    init()
    w = file.read()
    filecontent = re.split("([\W])", w)
    i = 0
    while True:
        while (filecontent[i] == ' ') or (filecontent[i] == '') or (filecontent[i] == '\t'):
            del filecontent[i]
            if len(filecontent) == i:
                break
        i += 1
        if len(filecontent) <= i:
            break
    if filecontent[len(filecontent) - 1] != '\n':  # to be sure that the content ends with new line
        filecontent.append('\n')
    for pass1or2 in range(1, 3):
        parse()
        bufferindex = 0
        locctr = 0
        lineno = 1

    file.close()


main()
