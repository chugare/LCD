from jieba.analyse import ChineseAnalyzer
from whoosh.fields import *
from whoosh.index import create_in
from whoosh.index import open_dir
import jieba
import json
import os
import FaLvQieFen
import shutil
import re
def buildIndex():
    analyzer = ChineseAnalyzer()

    schema =Schema(title=TEXT(analyzer=analyzer,stored=True),path=ID(stored=False),content=TEXT(analyzer,stored=True))
    if not os.path.exists('index'):
        os.mkdir('index')


    ix = create_in('index',schema=schema)


    writer = ix.writer()
    dirs = os.listdir('./laws')
    base = './laws/'
    count = 100
    #id = 0
    for dir2 in dirs:
        if count==0:
            break
        count -=1
        files = os.listdir(base+dir2)
        for file in files:
            Dic = FaLvQieFen.readLaw('laws/'+dir2+'/'+file)
            for k in Dic:
                title = Dic[k].Fa+Dic[k].name
                content = Dic[k].content

                print(title)
                print(content)
                id = dir2+'/'+file+'/'+str(Dic[k].No)

                writer.add_document(title=title,content = content,path=id)
                #id += 1
        writer.commit()
def main():
    ix = open_dir('index')
    with ix.searcher() as searcher:
        res = searcher.find('title',u'第二十条')
        if len(res)!=0:
            for r in res:
                print(r)


def packName():
    base = './laws/'
    dirs = os.listdir('./laws')
    def cpyf(base,dir2,Ddir):
        if not os.path.exists(base + Ddir):
            os.mkdir(base + Ddir)
        try:
            shutil.copy(base + dir2 + '/' + file, base + Ddir+'/')
        except shutil.SameFileError:
            pass
    count = 100
    # id = 0
    kind = {}
    for dir2 in dirs:
        try:
            files = os.listdir(base + dir2)
        except NotADirectoryError:
            continue
        for file in files:
            name = file.split('(')
            if len(name)<=1:
                name = file.split('（')[0]
            else:
                name = name[0]
            if name.endswith('法'):
                cpyf(base,dir2,'fa')
                pass
            elif name.endswith('条例'):
                cpyf(base, dir2, 'tiaoli')
                pass
            elif name.endswith('规则'):
                cpyf(base, dir2, 'guize')
                pass
            elif name.endswith('规定'):
                cpyf(base, dir2, 'guiding')
                pass
            elif name.endswith('决议'):
                cpyf(base, dir2, 'jueyi')
                pass
            elif name.endswith('决定'):
                cpyf(base, dir2, 'jueding')
                pass
            elif name.endswith('通则'):
                cpyf(base, dir2, 'tongze')
                pass
            elif name.endswith('通知'):
                cpyf(base, dir2, 'tongzhi')
                pass
            elif name.endswith('答复'):
                cpyf(base, dir2, 'dafu')
                pass
            elif name.endswith('复函'):
                cpyf(base, dir2, 'fuhan')
                pass
            elif name.endswith('批复'):
                cpyf(base, dir2, 'pifu')
                pass
            elif name.endswith('解释'):
                cpyf(base, dir2, 'jieshi')
                pass
            else:
                end = jieba.cut(name)
                k = ''

                for e in end:
                    k = e
                if k not in kind:
                    kind[k] = 0
                kind[k] +=1
    for k in kind:
        print(k+':'+str(kind[k]))

