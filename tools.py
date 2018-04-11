import re


def covTrCharNumber(traditionString):
    TraditionDic = {
        '零':0,
        '一':1,
        '二':2,
        '三':3,
        '四':4,
        '五':5,
        '六':6,
        '七':7,
        '八':8,
        '九':9,
        '十':0,
        '百':0
    }
    hc = re.search(r'(.??)百',traditionString)
    tc = re.search(r'(.??)十',traditionString)
    sc = re.search(r'(.??)$',traditionString)
    num = 0
    if hc is None and tc is None and sc is None:
        return -1
    try:
        if hc is not None:
            num = TraditionDic[hc.group()[0]]
        num *=10
        if tc is not None:
            if tc.group()[0].startswith('十'):
                num += 1
            else:
                num += TraditionDic[tc.group()[0]]
        num*=10
        if sc is not None:
            num += TraditionDic[sc.group()[0]]
    except KeyError :
        return -1
    except IndexError :
        return -1

    return num
def covNumberTrChar(number):
    NumDic = [
        '零',
        '一',
        '二',
        '三',
        '四',
        '五',
        '六',
        '七',
        '八',
        '九',
        '十',
        '百'
    ]
    str = ''
    hun = (int)(number/100)
    ten = (int)(number/10)%10
    sin = (int)(number%10)

    if hun!= 0:
        str = NumDic[hun]+'百'
    if ten!= 0:
        str+= NumDic[ten]+'十'
    elif sin !=0 and hun!= 0:
        str += '零'
    if sin !=0:
        str+= NumDic[sin]
    return  str

def findNum(instr):

    def getClass(char):
        N = [
            '一',
            '二',
            '三',
            '四',
            '五',
            '六',
            '七',
            '八',
            '九',
        ]
        B = '百'
        S = '十'
        L = '零'
        if char in N:
            return 'N'
        elif char == B:
            return 'B'
        elif char == L:
            return 'L'
        elif char == S:
            return 'S'
        else:
            return 'O'

    state ={
        0:{
            'N':1,
            'A':0
        },
        1:{
            'B':2,
            'S':5,
            'A':1
        },
        2:{
            'L':3,
            'N':4,
            'A': 1
        },
        3:{
            'N':6,
            'A': 0
        },
        4:{
            'S':5,
            'A': 0
        },
        5:{
            'N':6,
            'A': 1
        },
        6:{
            'A': 1
        },
    }
    ns = state[0]
    result = []
    resstr = ''

    index = 0
    while index<len(instr):
        char = instr[index]
        k = getClass(char)
        if k not in ns:
            if ns['A'] == 1:
                result.append(covTrCharNumber(resstr))
                ns = state[0]
                resstr = ''
                continue
            else:
                resstr = ''
                index += 1
                ns = state[0]

        else:
            nexts = ns[k]
            if nexts not in state:
                print('error:' +str(k)+' '+str(nexts))
            else:
                resstr += char
                index += 1
                ns = state[nexts]
    if ns['A'] == 1:
        result.append(covTrCharNumber(resstr))
    print(result)