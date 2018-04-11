# coding: utf-8
import re
from lxml import etree
import jieba
from Fatiao import FaTiao
import os
from  tools import *
def readLaw(name):
    RAWFILE = open(name,'r',encoding='utf-8')
    Dic = {}
    R_Bian = None
    R_Zhang = None
    R_Tiao = None
    count = 0
    cl = 0
    # 正常的换行排版形式 法条
    title = ''
    year = ''
    for line in RAWFILE:
        count +=1
        if count ==1:
            titleYear = re.findall('^(.*?)\((.*?)\)', line)

            if len(titleYear) > 0:
                title = titleYear[0][0]
                year = titleYear[0][1]
            else:

                print('Title analyse error ')
                break
            continue
        else:
            sp = re.split('第(.*?)条',line)

            for term in sp :
                r = covTrCharNumber(term)
                if r == cl+1:
                    cl = cl+1
                    R_Tiao = FaTiao('第' + term + '条', '', r, title, year, '', '')
                    Dic['第' + term + '条'] = R_Tiao
                    pass
                #elif r == cl:
                    #当前法律的计数和上一次相同
                else:
                    if R_Tiao is not None:
                        cont = re.sub('第.*?[章编节]','',term)
                        if len(cont)>2:
                            R_Tiao.addContent(cont)
    return Dic
def generateXML(Dic,name):
    root = etree.Element('FaLvQieFen',nsmap={'xmlns':'nju.software.edu.com'})
    root.set('version','1.2')
    root.set('tag','XingFa')
    lawclause = etree.Element('FT_collection',attrib={'name':'XingFa'})
    root.append(lawclause)
    for i in Dic:
        Dic[i].analysisContent()
        Dic[i].generateXML(lawclause)
    tree = etree.ElementTree(root)
    tree.write(name if name.endswith('.xml') else name+'.xml',pretty_print=True,xml_declaration = True,encoding='utf-8')
def wordStatistic(Dic,fq_threshold):
    word_dic_QT = {}
    word_dic_HC = {}
    for k in Dic:
        ft = Dic[k]
        for rule in ft.rules:
            qts = rule['QianTi']
            for qt in qts:
                words = jieba.lcut(qt)
                for word in words:
                    if word  not in word_dic_QT:
                        word_dic_QT[word] = []
                    word_dic_QT[word].append(ft.name)
            hcs = rule['HouCheng']
            for hc in hcs:
                words = jieba.lcut(hc)
                for word in words:
                    if word  not in word_dic_HC:
                        word_dic_HC[word] = []
                    word_dic_HC[word].append(ft.name)
    for k in word_dic_QT:
        if len(word_dic_QT[k])<fq_threshold:
            for ft in word_dic_QT[k]:
                Dic[ft].addKeyWord(k,True)
    for k in word_dic_HC:
        if len(word_dic_HC[k])<fq_threshold:
            for ft in word_dic_HC[k]:
                Dic[ft].addKeyWord(k,False)
    for k in Dic:
        ft = Dic[k]
        print(ft.name)
        print(ft.kw_qt)


def explaination():  # 处理司法解释的相关问题
    base = './laws/jieshi/'
    files = os.listdir(base)
    for file in files:

        dic = readLaw(base+file)
        for ft in dic:
            dic[ft].findLinkState()

explaination()