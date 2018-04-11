import re
from lxml import etree
import jieba
import pymongo
from tools import covTrCharNumber,covNumberTrChar,findNum

class FaTiao:
    def __init__(self, name, content, No, Fa, Year, Bian, Zhang):
        self.name = name
        self.No = No
        self.content = content
        self.Year = Year
        self.curKuan = ''
        self.KuanXiang = []
        if content.endswith('：'):
            self.curKuan = content
        else:
            self.addContent(content)
        self.Bian = Bian
        self.Zhang = Zhang
        self.Fa = Fa
        self.rules = []
        self.kw_qt = []
        self.kw_hc = []

    def addContent(self, contents):
        if len(contents) < 2:
            return
        if contents.startswith('（'):
            self.curKuan += '\n' + contents;
        else:
            if self.curKuan is not '':
                self.KuanXiang.append(self.curKuan)
                self.curKuan = ''
                self.KuanXiang.append(contents)
            else:
                self.KuanXiang.append(contents)

        self.content = self.content + contents

    def addQianTi(self, content):
        if hasattr(self, QT):
            self.QT.append[content]
        else:
            self.QT = []
            self.QT.append(content)

    def addHouCheng(self, content):
        if not hasattr(self, HC):
            self.HC = []
        self.HC.append(content)

    def addKeyWord(self, word, isQT):
        if isQT:
            if word not in self.kw_qt:
                self.kw_qt.append(word)
        else:
            if word not in self.kw_hc:
                self.kw_hc.append(word)

    def generateXML(self, root):
        attribute = {
            'name': self.name,
            'content': self.content,
            'No': str(self.No),
            'Fa': self.Fa,
            'year': self.Year
        }
        ft = etree.Element('FT', attrib=attribute)

        for kuan in self.KuanXiang:
            index = self.KuanXiang.index(kuan) + 1
            k = etree.Element('Kuan', {'name': '第' + covNumberTrChar(index) + '款'})
            k.text = kuan
            ft.append(k)

        for line in self.rules:
            lt = etree.Element('Rule')

            qtc = etree.Element('QT_collection')
            hcc = etree.Element('HC_collection')

            for qt in line['QianTi']:
                qt_l = etree.Element('QT')
                qt_l.text = qt
                qtc.append(qt_l)
            for hc in line['HouCheng']:
                hc_l = etree.Element('HC')
                hc_l.text = hc
                hcc.append(hc_l)
            lt.append(qtc)
            lt.append(hcc)
            ft.append(lt)
        root.append(ft)
        pass

    def findLinkState(self):
        ct = self.content

        reference = []
        pattern = {
            '依据(.*?)第(.*?)[条款]': 1,
            '根据(.*?)第(.*?)[条款]': 1,
            '依照(.*?)第(.*?)[条款]': 1,
            '按照(.*?)第(.*?)[条款]': 1,
            '属于(.*?)第(.*?)[条款]': 2,
            '指(.*?)第(.*?)[条款]': 2,
            '认定为(.*?)第(.*?)[条款]': 2,
            '[；，。](.*?)第(.*?)[条款]': 99

        }
        pattern2 = {
            '依据(.+?法)(.*?[条款])':1,
            '根据(.+?法)(.*?[条款])':1,
            '依照(.+?法)(.*?[条款])':1,
            '按照(.+?法)(.*?[条款])':1,
            '属于(.+?法)(.*?[条款])':2,
            '指(.+?法)(.*?[条款])':2,
            '认定为(.+?法)(.*?[条款])':2,
            '(.+?法)(.*?)规定的':3,
            '[；，。](.+?法)(.*?[条款])':99

        }
        Jus = re.split('[，。；\n]',ct)
        for ju in Jus:
            for p in pattern2:
                ref = re.findall(p,ju)
                for ri in ref:
                    print(ri[0]+'  --  '+ri[1] +' -- '+str(pattern2[p]))
                    findNum(ri[1])
                if len(ref)>0:
                    print(ju)
                    break

        pass

    def storeIntoMongo(self):
        pass

    def analysisContent(self):
        Hangs = self.content.split('\n')
        Hangs = [self.content] if len(Hangs) < 1 else Hangs

        SENTENCE_STATE = {
            'qianjian_f': 1,
            'qianjian_c': 2,
            'houcheng_f': 3,
            'houcheng_c': 4
        }

        parttens = {
            '(.*?)的$':0,
            '^对于*(.*?)$':1,
            '为了(.*)':2,
            '^除(.*)以外$':3,

            '^(.*?)适用(.*)$':4,  # 4
            '^(.*?)可以(.*)':5,
            '^(.*?)应当(.*)':6,
            '^(.*?)依照(.*)':7,
            '^(.*?)按照(.*)':8,
            '^(.*?)不得(.*)':9,
            '^都(.*)$':10,
            '为(.*)':11,
            '属于(.*)':12,
            '^(.*)是(.*)$':13,
    }
        for Hang in Hangs:
            if (len(Hang) <= 1):
                continue
            Duans = re.split('[；。]', Hang)

            Duans = [Hang] if len(Duans) < 1 else Duans

            for Duan in Duans:
                if (len(Duan) <= 1):
                    continue
                Jus = Duan.split('，')

                Jus = [Duan] if len(Jus) < 1 else Jus
                QianTi = []
                HouCheng = []
                last = ''
                for Ju in Jus:

                    if len(Ju) <= 1:
                        continue
                    MatchFlag = False
                    for p in parttens:
                        mat = re.match(p, Ju)
                        if mat is not None:
                            MatchFlag = True
                            if parttens[p] == 0:  # 。。。的 情况

                                if last.endswith('2'):
                                    line = {
                                        'QianTi': QianTi,
                                        'HouCheng': HouCheng
                                    }
                                    self.rules.append(line)
                                    QianTi = []
                                    HouCheng = []
                                QianTi.append(mat.group(0))

                                last = '1'
                                break

                            elif parttens[p] == 1:  # 对于。。。 情况
                                QianTi.append(mat.group(0))
                                last = last + '1'
                                break

                            elif parttens[p] == 2:  # 为了。。。 情况
                                QianTi.append(mat.group(0))
                                last = last + '1'
                                break

                            elif parttens[p] == 3:  # 为了。。。 情况
                                QianTi.append(mat.group(0))
                                last = last + '1'
                                break

                            elif parttens[p] >= 4:  #
                                if p.startswith('^(.*?)应当(.*)'):
                                    pass
                                if p.startswith('^(.*)是(.*)$'):
                                    if len(mat.group()) >= 2:
                                        QianTi.append(mat.group())
                                        HouCheng.append(mat.group(1))
                                        last = last + '2';
                                        break

                                    pass

                                HouCheng.append(mat.group(0))
                                last = '2'
                                break
                    if not MatchFlag:
                        if len(HouCheng) > 0:
                            HouCheng.append(Ju)
                        else:
                            QianTi.append(Ju)

                line = {
                    'QianTi': QianTi,
                    'HouCheng': HouCheng
                }
                self.rules.append(line)


'''
                            if parttens.index(p) == 3:#。。是。。 情况
                                HouCheng += mat.group(1)
                                print (HouCheng+'-判定结果，对象为—'+QianTi)
                                pass

                            if parttens.index(p) == 4:#可以。。 情况
                                HouCheng += mat.group(1)
                                print(HouCheng + '-判定结果，对象为—' + QianTi)
                                pass

                            if parttens.index(p) == 5:#应当。。 情况
                                HouCheng += mat.group(1)
                                print(HouCheng + '-判定结果，对象为—' + QianTi)
                                pass
'''

