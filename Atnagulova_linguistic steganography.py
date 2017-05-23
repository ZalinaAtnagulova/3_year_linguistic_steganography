import requests
import queue
import re
from pymystem3 import Mystem

def sketch_engine(word):
    dic = {}
    short_dic = {}
    short = []
    payload={'username':'olgaleshchenko1', 'password':'hF8eC72pn9'}
    with requests.Session() as s:
        p = s.post('https://the.sketchengine.co.uk/login/', data=payload)
        link = 'https://the.sketchengine.co.uk/bonito/corpus/thes?corpname=preloaded%2Frutenten11_8&reload=&lemma='+word+'&lpos=&maxthesitems=60&minthesscore=0.0&includeheadword=0&clusteritems=0&minsim=0.15'
        r = s.get(link).text
        piece = re.search('var thes_words = \[\n(.*?)\n  \]', r, flags=re.DOTALL)
        if piece != None:
            words_dirty = piece.group(1)
            words_dirty = words_dirty.split('\n')
            for a in words_dirty:
                a = re.sub('  ', '', a)
                a = a.strip('{')
                a = re.sub('\*\(Math.pow(.*?)\)},', '', a)
                a = re.sub('\'', '', a)
                bvc = dict(item.split(': ') for item in a.split(', '))
                if bvc['word'] not in dic:
                    dic[bvc['word']] = float(bvc['size'])
    for one in sorted(dic, key=lambda n: dic[n], reverse=True):
        if dic[one] >= 0.35:
            short.append((dic[one], one))
    return short

class HuffmanNode(object):
    def __init__(self, left=None, right=None, root=None):
        self.left = left
        self.right = right
        self.root = root
    def children(self):
        return((self.left, self.right))

def create_tree(frequencies):
    p = queue.PriorityQueue()
    for value in frequencies:
        p.put(value)
    while p.qsize() > 1:
        try:
            l, r = p.get(), p.get()
            node = HuffmanNode(l, r)
            p.put((l[0]+r[0], node))
        except:
            TypeError
    return p.get()

def walk_tree(node, prefix="", code={}):
    if isinstance(node[1].left[1], HuffmanNode):
        walk_tree(node[1].left,prefix+"0", code)
    else:
        code[node[1].left[1]]=prefix+"0"
    if isinstance(node[1].right[1],HuffmanNode):
        walk_tree(node[1].right,prefix+"1", code)
    else:
        code[node[1].right[1]]=prefix+"1"
    return(code)

def dic_bin_codes(freq):
    node = create_tree(freq)
    code = walk_tree(node)
    dic = {}
    for i in sorted(freq, reverse=True):
        try:
            dic[i[1]]=code[i[1]]
        except:
            KeyError
    return dic
    
def codes():
    f = open('code2diff.txt', 'r', encoding='utf-8')
    table = f.read().split('\n')
    f.close()
    dic = {}
    for line in table:
        line = line.split(';')
        dic[line[0]] = line[2]
    return dic

def hd_msg(message, alph):
    res = []
    for a in message:
        a = alph[a]
        res.append(a)
    return res

def mystem_new(file, msg):
    bigdata = {}
    f = open(file, 'r', encoding = 'utf-8')
    text = f.read()
    f.close()
    capitals = ['Й','Ц','У','К','Е','Н','Г','Ш','Щ','З','Х','Ф','Ы','В','А','П','Р','О','Л','Д','Ж','Э','Я','Ч','С','М','И',
                'Т','Б','Ю'] 
    m = Mystem()
    f1 = open(file[:-4]+'_output.txt', 'w', encoding = 'utf-8')
    analyse = m.analyze(text)
    pos = ['A','S','V']
    for one in analyse:
        if len(msg)>0:
            if 'analysis' in one and len(one['analysis'])!= 0 and one['analysis'][0]['gr'][0] in pos:
                if one['text'][0] not in capitals:
                    sub_dic = one['analysis']
                    for value in sub_dic:
                        if 'lex' in value:
                            short = sketch_engine(value['lex'])
                            if len(short)>1:
                                tr_text = dic_bin_codes(short)
                                for smt in tr_text:
                                    if len(msg)>0:
                                        if tr_text[smt] == msg[0]:
                                            print(one['text'])
                                            print(smt)
                                            one['text'] = phpmorphy(smt, one)
                                            msg.remove(msg[0])
                                            break
        f1.write(one['text'])
    f1.close()

def grr(one):
    gram = one['analysis'][0]['gr']
    if '(' in gram:
        srch = re.search('=\((.*)\)', gram)
    else:
        srch = re.search('=(.*)', gram, flags=re.DOTALL)
    if srch != None:
        gram = srch.group(1).split('|')
        for a in range(0, len(gram)):
            gram[a] = gram[a].split(',')
        print(gram)
    return gram

def phpmorphy(smt, one):
    srch = ''
    form = ''
    line = ''
    table = []
    cases = {'им':'им', 'род':'рд', 'дат':'дт', 'вин':'вн', 'твор':'тв',
             'пр':'пр', 'зват':'зв', 'прош':'прш', 'непрош':'нст', 'инф':'',
             'ед':'ед', 'мн':'мн', 'жен':'жр', 'муж':'мр', 'сред':'ср',
             'кр':'КР', '1-л':'1л', '2-л':'2л', '3-л':'3л', 'пов':'пвл',
             'несов':'нс', 'сов':'св'}
    adr1 = 'http://phpmorphy.sourceforge.net/dokuwiki/demo?word='
    adr2 = '&dict_type=aot&enable_predict_by_suffix=1&enable_predict_by_db=1'
    gr = grr(one)
    with requests.Session() as s:
        link = adr1+smt+adr2
        r = s.get(link).text
        r = str(r)
        br = re.findall('<table.*?>(.*?)</table>', r, flags=re.DOTALL)
        for a in br[:2]:
            razb = re.findall('<span.*?>.*?</span>', a, flags=re.DOTALL)
            for b in razb:
                table.append(b)
        base = re.search('(<span class="base-form">\n(.*?)</span>)', r, flags=re.DOTALL)
        if base != None:
            cases['инф']=base.group(2).lower()
    for lines in table:
        gr_p = re.search("title='(.*?)'", lines)
        if gr_p != None:
            line = gr_p.group(1)
        if len(gr[0]) in [2,3]:
            if 'кр' in gr[0] and cases[gr[0][0]] in line and cases[gr[0][1]] in line and cases[gr[0][2]] in line:
                word = re.search('>([а-яё]+)<', lines)
                if word != None:
                    form = word.group(1)
            if 'кр' not in gr[0] and cases[gr[0][0]] in line and cases[gr[0][1]] in line:
                word = re.search('>([а-яё]+)<', lines)
                if word != None:
                    form = word.group(1)
        if len(gr[0])>3:
            if cases[gr[0][0]] in line and cases[gr[0][1]] in line and cases[gr[0][3]] in line:
                word = re.search('>([а-яё]+)<', lines)
                if word != None:
                    form = word.group(1)
        if len(gr[0])<=1:
            if one['analysis'][0]['gr'][:3] == 'ADV' and 'прилагательное' in r:
                if 'КР' in line and 'ср' in line:
                    word = re.search('>([а-яё]+)<', lines)
                    if word != None:
                        form = word.group(1)
            else:
                form = cases['инф']
    if len(table)==0 or len(form)==0:
            form = cases['инф']
    if 'отсутствует в словаре' in r:
            form = smt
    print('Ответ')
    print(form)
    return form

alphabete = [(0.175, ' '), (0.10983, 'о'), (0.08483, 'е'), (0.07998, 'а'), (0.07367, 'и'),
             (0.067, 'н'), (0.06318, 'т'), (0.05473, 'с'), (0.04746, 'р'), (0.04533, 'в'),
             (0.04343, 'л'), (0.03486, 'к'), (0.03203, 'м'), (0.02977, 'д'), (0.02804, 'п'),
             (0.02615, 'у'), (0.02001, 'я'), (0.01898, 'ы'), (0.01735, 'ь'), (0.01687, 'г'),
             (0.01641, 'з'), (0.01592, 'б'), (0.0145, 'ч'), (0.01208, 'й'), (0.00966, 'х'),
             (0.0094, 'ж'), (0.00718, 'ш'), (0.00639, 'ю'), (0.00486, 'ц'), (0.00361, 'щ'),
             (0.00331, 'э'), (0.00267, 'ф'), (0.00037, 'ъ'), (0.00013, 'ё')]
alp_cl = dic_bin_codes(alphabete)
print(alp_cl)
msg = hd_msg(input('Введите сообщение, которое хотите зашифровать: '), alp_cl)
txtfile = input('Введите название файла с текстом-контейнейром: ')
mystem_new(txtfile, msg)
