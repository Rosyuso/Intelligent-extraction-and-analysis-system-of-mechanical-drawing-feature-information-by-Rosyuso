import os 
import sys 
import re

def create_txt():
    '''制作gt.txt文件'''
    path = 'D:/ocrbenchmark/deep-text-recognition-benchmark-master/data_train/test1'
    #  {imagepath}\t{label}\n
    listmain = os.listdir(path)
    for i in range(len(listmain)):
        split_by_png = listmain[i].split('.p', 1)[0].split('_font')[0:-1] #生成列表并去掉最后一项数据增强的尾缀 例如['chuizhidu0.05','4X','3N','2H']
        # split_by_font = split_by_png[0].split('_font')[0:-1]
        splited = split_by_png[0]
        for j in range(len(split_by_png)-1):
            s = split_by_png[j + 1]
            string = re.sub(r'\d','',s)
            # print(string)
            splited += string
        # os.chdir(os.path.dirname(os.path.realpath(__file__)))
        # print(splited)
        f = open( 'D:/ocrbenchmark/deep-text-recognition-benchmark-master/data_validation/' + 'gt.txt', 'a')
        path_i = 'test/'+listmain[i]
        # f.write('{}\t{}\n'.format(path_i,split_by__[0]))
        content = '{}\t{}\n'.format(path_i,splited)
        f.write(content)
        f.close()

# import re
# s = 's_fontD_blockS_font4Y'
# x = re.compile(r'[A-Z]')
# X = x.findall(s)
# print(X)
# ['D', 'S', 'Y']

def create_txt2():
    '''制作gt.txt文件'''
    path = 'D:/ocrbenchmark/deep-text-recognition-benchmark-master/data_train/zhengfu_augmentation'
    #  {imagepath}\t{label}\n
    listmain = os.listdir(path)
    for i in range(len(listmain)):
        split_by_png = listmain[i].split('.p', 1)[0].split('_')[0] 
        f = open( 'D:/ocrbenchmark/deep-text-recognition-benchmark-master/data_train/' + 'gtzf.txt', 'a')
        path_i = 'test/'+listmain[i]
        # f.write('{}\t{}\n'.format(path_i,split_by__[0]))
        content = '{}\t{}\n'.format(path_i,split_by_png)
        f.write(content)
        f.close()

def create_txt3():
    '''制作gt.txt文件'''
    path = 'D:/ocrbenchmark/deep-text-recognition-benchmark-master/data_validation_new'
    #  {imagepath}\t{label}\n
    listmain = os.listdir(path)
    for i in range(len(listmain)):
        # Cpt = re.compile(r'[A-Z]Ⓜ')
        # Cpt_list = Cpt.findall(split_by_png)
        # split_by__ = split_by_png.split('_')[0]
        # for j in range(len(Cpt_list)):
        #     split_by__ += Cpt_list[j]
#         # if split_by__[0][:8] == 'chuizhidu':
#         #     split_by__1 = '⊥' + split_by__[0][9:]
#         #     split_by__[0] = split_by__1
        
#         # elif symbol == 'pingmiandu':
#         #     alter_symbol = '▱'
#         # elif symbol == 'duichendu':
#         #     alter_symbol = '⚍'
#         # elif symbol == 'yuantiaodong':
#         #     alter_symbol = '↗'  
#         # elif symbol == 'tongzhoudu':
#         #     alter_symbol = ''∅ ◎ 
#         # elif symbol == 'weizhidu':
#         #     alter_symbol = '☩' 
#         # elif symbol == 'qingxiedu':
#         #     alter_symbol = '∠'
#         # elif symbol == 'pingxingdu':
#         #     alter_symbol = '∥'
#         # elif symbol == 'quantiaodong':
#         #     alter_symbol = '⇉'
                # mianlunkuodu    ◚
                # xianlunkuodu    ◠
                # zhixiandu   ―
                # yuandu  ○
                # yuanzhudu   ⛙
        split_by_png = listmain[i].split('.p', 1)[0] #'chuizhidu0.05'
        split_by_png = re.sub(r'qM','Ⓜ',split_by_png)
        split_by_png = re.sub(r'qT','Ⓣ',split_by_png)
        split_by_png = re.sub(r'_saltandpepper','',split_by_png)
        split_by_png = re.sub(r'_SaltAndPepper','',split_by_png)
        split_by_png = re.sub(r'_color','',split_by_png)
        split_by_png = re.sub(r'_gasuss','',split_by_png)
        split_by_png = re.sub(r'_resize','',split_by_png)
        split_by_png = re.sub(r'_rotate','',split_by_png)
        split_by_png = re.sub(r'_shear','',split_by_png)
        split_by_png = re.sub(r'_color','',split_by_png)
        split_by__ = re.sub(r'fai','∅',split_by_png)
        split_by__ = re.sub(r'_font1','',split_by__)
        split_by__ = re.sub(r'_font2','',split_by__)
        split_by__ = re.sub(r'_font3','',split_by__)
        split_by__ = re.sub(r'_font4','',split_by__)
        split_by__ = re.sub(r'_font5','',split_by__)
        split_by__ = re.sub(r'_font6','',split_by__)
        split_by__ = re.sub(r'_block','',split_by__)
        split_by__ = re.sub(r'pingxingdu','∥',split_by__)
        split_by__ = re.sub(r'chuizhidu','⊥',split_by__)
        split_by__ = re.sub(r'pingmiandu','▱',split_by__)
        split_by__ = re.sub(r'duichendu','⚍',split_by__)
        split_by__ = re.sub(r'yuantiaodong','↗',split_by__)
        split_by__ = re.sub(r'tongzhoudu','◎',split_by__)
        split_by__ = re.sub(r'weizhidu','☩',split_by__)
        split_by__ = re.sub(r'qingxiedu','∠',split_by__)
        split_by__ = re.sub(r'quantiaodong','⇉',split_by__)
        split_by__ = re.sub(r'mianlunkuodu','◚',split_by__)
        split_by__ = re.sub(r'xianlunkuodu','◠',split_by__)
        split_by__ = re.sub(r'xianlunkuo','◠',split_by__)
        split_by__ = re.sub(r'zhixiandu','―',split_by__)
        split_by__ = re.sub(r'yuandu','○',split_by__)
        split_by__ = re.sub(r'yuanzhudu','⛙',split_by__)
        split_by__ = re.sub(r'pingxingdu','∥',split_by__)
        split_by__ = re.sub(r'jdu','°',split_by__)
        split_by__ = re.sub(r'zhengfu','±',split_by__)
        split_by__ = re.sub(r'slash','/',split_by__)
        split_by__ = re.sub(r'gc','贯穿',split_by__)
        split_by__ = re.sub(r'shen','深',split_by__)
        split_by__ = re.sub(r'chenkong','沉孔',split_by__)
        split_by__ = re.sub(r'tong','通',split_by__)
        split_by__ = re.sub(r'xia','↧',split_by__)
        split_by__ = re.sub(r'ping','∐',split_by__)
        split_by__ = re.sub(r'_','',split_by__)
        # split_by__ = re.sub(r"(2)",'',split_by__)



        f = open( 'D:/vs_python_opencv_tesseract/pics/testgt/' + 'gt.txt', 'a',encoding='utf-8')
        path_i = 'test/'+listmain[i]
        # f.write('{}\t{}\n'.format(path_i,split_by__[0]))
        content = '{}\t{}\n'.format(path_i,split_by__)
        f.write(content)
        f.close()

create_txt3()