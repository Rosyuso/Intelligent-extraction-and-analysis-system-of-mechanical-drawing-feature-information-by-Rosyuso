import xlsxwriter as xw
import re 
import xlrd

f = open('special_result.txt','r',encoding='utf-8')
g = open('manual_result.txt','r',encoding='utf-8')
coor_list = f.readlines() #存成每一行数据的列表
coor_list_m = g.readlines() #存成每一行数据的列表
Cap_char = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
# print(coor_list)
L_result = list()
for i in coor_list:
    L_result.append(i.split('\t')[1])
for j in coor_list_m:
    L_result.append(j.split('\t')[1])
'''形如：
manual_cropped_img\1.png	⊥0.01B	0.9936
manual_cropped_img\2.png	☩∅0.2B	0.9823
manual_cropped_img\3.png	▱0.01	0.9948
manual_cropped_img\4.png	11.25±0.5	0.4134
manual_cropped_img\5.png	☩∅0.02A	0.4861
manual_cropped_img\1.png	∥∅0.01B	0.9936
manual_cropped_img\2.png	☩∅0.2B	0.9823
manual_cropped_img\3.png	▱0.01	0.9948
manual_cropped_img\4.png	11.25±0.02	0.4134
manual_cropped_img\5.png	☩∅0.02A	0.4861
manual_cropped_img\1.png	◠0.01	0.9936
manual_cropped_img\2.png	☩∅0.2B	0.9823
manual_cropped_img\3.png	▱0.01	0.9948
manual_cropped_img\4.png	11.25±0.02	0.4134
manual_cropped_img\5.png	◎∅0.02C	0.4861
manual_cropped_img\1.png	☩∅0.01B	0.9936
manual_cropped_img\2.png	⛙0.2B	0.9823
manual_cropped_img\3.png	▱0.01	0.9948
manual_cropped_img\4.png	11±0.02	0.4134
manual_cropped_img\5.png	☩∅0.02A	0.4861
'''

data_diameter, data_radius, data_tolerance= [],[],[]
diameter_index, radius_index,tolerance_index= 1,1,1

for i in range(1,len(L_result)):
    if L_result[i][0] == '∅' and '±' not in L_result[i]: #单纯直径 ,形如∅16
        data_diameter.append({"id": diameter_index, "diameter": L_result[i], "amount": 1,"∅_i":i})
        diameter_index += 1
    elif L_result[i][0] == 'R': #单纯半径 ,形如R16
        data_radius.append({"id": radius_index, "radius": L_result[i], "amount": 1,"R_i":i})
        radius_index += 1
    elif L_result[i][1] == 'X' and L_result[i][2] == '∅': #圆周阵列孔（相同孔），例如2X∅12
        data_diameter.append({"id": diameter_index, "diameter": L_result[i].split('X')[1], "amount": L_result[i].split('X')[0],"∅_i":i})
        diameter_index += 1
    elif L_result[i][1] == 'X' and L_result[i][2] == 'R': #圆周阵列孔（相同孔），例如2X∅12
        data_radius.append({"id": radius_index, "radius": L_result[i].split('X')[1], "amount": L_result[i].split('X')[0],"R_i":i})
        radius_index += 1
    elif L_result[i][0] in '☩⊥∥▱⚍↗◎∠⇉◚◠―○⛙↧∐': #形位公差框
        if L_result[i][-1] in Cap_char and L_result[i][-2] in Cap_char and L_result[i][-3] in Cap_char: #有基准,三基准
            data_tolerance.append({"id": tolerance_index, "tolerance":L_result[i][0], \
                 "value": L_result[i][1:-3], \
                     '1st datum':L_result[i][-3], \
                        '2nd datum':L_result[i][-2],\
                            '3rd datum':L_result[i][-1], \
                                 "T_i":i})
            tolerance_index += 1
        elif L_result[i][-1] in Cap_char and L_result[i][-2] in Cap_char: #有基准,两基准
            data_tolerance.append({"id": tolerance_index, "tolerance": L_result[i][0], \
                 "value": L_result[i][1:-2], \
                     '1st datum':L_result[i][-2], \
                        '2nd datum':L_result[i][-1],\
                            '3rd datum':'', \
                                 "T_i":i})
            tolerance_index += 1
        elif L_result[i][-1] in Cap_char: #有基准,一基准
            data_tolerance.append({"id": tolerance_index, "tolerance": L_result[i][0], \
                 "value": L_result[i][1:-1], \
                     '1st datum':L_result[i][-1], \
                        '2nd datum':'',\
                            '3rd datum':'', \
                                 "T_i":i})
            tolerance_index += 1
        else: #无基准
            data_tolerance.append({"id": tolerance_index, "tolerance": L_result[i][0], \
                 "value": L_result[i][1:], \
                     '1st datum':'', \
                        '2nd datum':'',\
                            '3rd datum':'', \
                                 "T_i":i})
            tolerance_index += 1



def xw_toExcel(data, fileName,title,heading):  # xlsxwriter库储存数据到excel
    workbook = xw.Workbook(fileName)  # 创建工作簿
    bold_title = workbook.add_format({
        'bold':  True,  # 字体加粗
        # 'border': 1,  # 单元格边框宽度
        'align': 'center',  # 水平对齐方式
        'valign': 'vcenter',  # 垂直对齐方式
        'fg_color': '#F4B084',  # 单元格背景颜色
        'text_wrap': True,  # 是否自动换行
        'font_size': 12
         })
    bold_body = workbook.add_format({
        # 'bold':  True,  # 字体加粗
        'border': 1,  # 单元格边框宽度
        'align': 'center',  # 水平对齐方式
        'valign': 'vcenter',  # 垂直对齐方式
        # 'fg_color': '#F4B084',  # 单元格背景颜色
        'text_wrap': True,  # 是否自动换行
        'font_size': 14
         })
    worksheet1 = workbook.add_worksheet("sheet1")  # 创建子表
    worksheet1.activate()  # 激活表
    # format_border = workbook.add_format({'border':1}) # 设置边框格式
    # worksheet1.conditional_format('A1:XFD1048576',{'type':'no_blanks', 'format': format_border}) # 这里是核心，根据条件来设置格式
    for m in range(len(data)):
        worksheet1.write_row(heading[m], title[m],bold_title)  # 从A1单元格开始写入表头
        i = 2  # 从第二行开始写入数据
        for j in range(len(data[m])):
            if m == 0:
                insertData = [data[m][j]["id"], data[m][j]["diameter"], data[m][j]["amount"],data[m][j]["∅_i"]]
            elif m == 1:
                insertData = [data[m][j]["id"], data[m][j]["radius"], data[m][j]["amount"],data[m][j]["R_i"]]
            elif m == 2:
                insertData = [data[m][j]["id"], data[m][j]["tolerance"], data[m][j]["value"],data[m][j]["1st datum"],data[m][j]["2nd datum"],data[m][j]["3rd datum"],data[m][j]["T_i"]]
            row = heading[m][0] + str(i)
            print(insertData)
            worksheet1.write_row(row, insertData,bold_body)
            i += 1
    
    workbook.close()


data = [data_diameter,data_radius,data_tolerance]
title = [['序号', '直径', '数量','索引'],['序号', '半径', '数量','索引'],['序号', '公差类型', '数值','第一基准','第二基准','第三基准','索引']]
heading = ['A1','F1','K1']

def result2excel():
    xw_toExcel(data,fileName,title,heading)

fileName = '测试.xlsx'
result2excel()
# xw_toExcel(testData, fileName)