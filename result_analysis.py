import xlsxwriter as xw


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

Cap_char = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
title = [['序号','数值','索引'], \
        ['序号','基本尺寸','偏差','索引'], \
        ['序号', '直径', '数量','索引'],\
        ['序号', '半径', '数量','索引'], \
        ['序号', '公差类型', '数值','第一基准','第二基准','第三基准','索引'], \
        ['序号','槽宽','偏差','索引'],\
        ['序号','基本尺寸','配合','索引'], \
        ['序号','螺纹','索引']]
head_name = ['普通尺寸','普通公差','直径尺寸','半径尺寸','形位公差','退刀槽尺寸','配合公差','螺纹尺寸']

Cap_charl = []
for i in Cap_char:
    Cap_charl.append(i)
for i in range(len(Cap_char)):
    Cap_charl.append('A'+Cap_char[i])

# print(Cap_charl)


def txt2list(opt=True):
    L_result = list()
    f = open('special_result.txt','r',encoding='utf-8')
    coor_list = f.readlines() #存成每一行数据的列表
    for i in range(1,len(coor_list)):
        L_result.append(coor_list[i].split('\t')[1])
    if opt == False:#直接识别特殊字符模式
        g = open('manual_result.txt','r',encoding='utf-8')
        coor_list_m = g.readlines() #存成每一行数据的列表
        # print(coor_list)
        for j in range(1,len(coor_list_m)):
            L_result.append(coor_list_m[j].split('\t')[1])
    # print(L_result)
    return L_result


def list2data(L_result):

    data_diameter, data_radius, data_tolerance,data_pm,data_normal,data_recess,data_match,data_thread = [],[],[],[],[],[],[],[]
    diameter_index, radius_index,tolerance_index,pm_index,n_index,recess_index,match_index,thread_index = 1,1,1,1,1,1,1,1

    for i in range(0,len(L_result)):
        if L_result[i][0] == '∅' and '±' not in L_result[i]: #单纯直径 ,形如∅16
            if L_result[i][-2] in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz':
            #先暂定两位数的直径
                data_match.append({"id": match_index, "basic": L_result[i][:3],"match": L_result[i][3:],"m_i":i})
                match_index += 1
            else:
                data_diameter.append({"id": diameter_index, "diameter": L_result[i], "amount": 1,"∅_i":i})
                diameter_index += 1
        elif L_result[i][0] == 'R': #单纯半径 ,形如R16
            data_radius.append({"id": radius_index, "radius": L_result[i], "amount": 1,"R_i":i})
            radius_index += 1
        elif L_result[i][1] == 'X' and L_result[i][2]:  #圆周阵列孔（相同孔），例如2X∅12,2-∅8
            if L_result[i][2] == '∅':
                data_diameter.append({"id": diameter_index, "diameter": L_result[i].split('X')[1], "amount": L_result[i].split('X')[0],"∅_i":i})
                diameter_index += 1
        elif L_result[i][1] in '-' and L_result[i][2]: #圆周阵列孔（相同孔），例如2X∅12,2-∅8
            if L_result[i][2] == '∅':
                data_diameter.append({"id": diameter_index, "diameter": L_result[i].split('-')[1], "amount": L_result[i].split('-')[0],"∅_i":i})
                diameter_index += 1
        elif L_result[i][1] == 'X' and L_result[i][2] == 'R': #圆周阵列孔（相同孔），例如2X∅12
            data_radius.append({"id": radius_index, "radius": L_result[i].split('X')[1], "amount": L_result[i].split('X')[0],"R_i":i})
            radius_index += 1
        # elif 
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
        elif '±' in L_result[i]: #带有正负号的公差
            data_pm.append({"id": pm_index, "basic": L_result[i].split('±')[0], "deviation": L_result[i].split('±')[1],"pm_i":i})
            pm_index += 1
            # print('bingo')
        elif L_result[i][0] == 'M': #螺纹
            data_thread.append({"id": thread_index, "thread": L_result[i], "th_i":i})
            thread_index += 1
            
        elif 'X' in L_result[i]: #退刀槽
            data_recess.append({"id": n_index, "width": L_result[i].split('X')[0],"deepth": L_result[i].split('X')[1],"re_i":i})
            recess_index += 1
   ######    ###### ###### ###### ###### ###### ###### ######   ######待添加：配合（∅50H8)，螺纹（M10） ###### ###### ###### ###### ###### ###### ###### ###### ###### ###### ###### ######
        # 一般大写表示孔的公差，小写表示轴的公差：∅30H7，表示直径30的孔，公差是+0.025/0，∅30h7，表示直径30的轴，公差是0/-0.025
        # 一般装配图才会用到∅30H7/h7,零件图一般用 ∅30 +0.025/0表示
       
            # if len(L_result[i]) > 5 and L_result[i][-5] in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz':#配合
            #      #先暂定两位数的直径
            #     data_match.append({"id": n_index, "basic": L_result[i][:3],"match": L_result[i][3:],"m_i":i})
            #     match_index += 1

        else: #其他普通尺寸
            data_normal.append({"id": n_index, "value": L_result[i],"n_i":i})
            n_index += 1

    return data_normal,data_pm,data_diameter, data_radius, data_tolerance,data_recess,data_match,data_thread


def xw_toExcel(data, fileName,title,head_name):  # xlsxwriter库储存数据到excel
    workbook = xw.Workbook(fileName)  # 创建工作簿
    bold_title = workbook.add_format({
        'bold':  True,  # 字体加粗
        # 'border': 1,  # 单元格边框宽度
        'align': 'center',  # 水平对齐方式
        'valign': 'vcenter',  # 垂直对齐方式
        'fg_color': '#F4B084',  # 单元格背景颜色
        'text_wrap': True,  # 是否自动换行
        'font_size': 11
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
    merge_format = workbook.add_format({
        'bold':     True,
        'border':   3,
        'align':    'center',#水平居中
        'valign':   'vcenter',#垂直居中
        'fg_color': '#D7E4BC',#颜色填充
        'font_size': 16
        })
    worksheet1 = workbook.add_worksheet("sheet1")  # 创建子表
    worksheet1.activate()  # 激活表
    # format_border = workbook.add_format({'border':1}) # 设置边框格式
    # worksheet1.conditional_format('A1:XFD1048576',{'type':'no_blanks', 'format': format_border}) # 这里是核心，根据条件来设置格式
    m_ind = []
    row_ind_l = ['A']
    for m in range(len(data)):
        i = 3  # 从第二行开始写入数据
        if data[m]:
            m_ind.append(m)
            if m_ind.index(m) == 0:
                row = 0
                row_ind = Cap_charl[row]
            elif m_ind.index(m) != 0:
                row += len(title[m_ind[-2]]) + 1
                row_ind = Cap_charl[row]
                row_ind_l.append(row_ind)
                # print(row_ind_l)
            worksheet1.write_row(row_ind[0] + str(i-1), title[m],bold_title)  # 从A2单元格开始写入表头

            for j in range(len(data[m])):
                if m == 0:
                    insertData = [data[m][j]["id"], data[m][j]["value"],data[m][j]["n_i"]]
                elif m == 1:
                    insertData = [data[m][j]["id"], data[m][j]["basic"], data[m][j]["deviation"],data[m][j]["pm_i"]]
                elif m == 2:
                    insertData = [data[m][j]["id"], data[m][j]["diameter"], data[m][j]["amount"],data[m][j]["∅_i"]]
                elif m == 3:
                    insertData = [data[m][j]["id"], data[m][j]["radius"], data[m][j]["amount"],data[m][j]["R_i"]]
                elif m == 4:
                    insertData = [data[m][j]["id"], data[m][j]["tolerance"], data[m][j]["value"],data[m][j]["1st datum"],data[m][j]["2nd datum"],data[m][j]["3rd datum"],data[m][j]["T_i"]]
                elif m == 5:
                    insertData = [data[m][j]["id"], data[m][j]["width"], data[m][j]["deepth"],data[m][j]["re_i"]]
                elif m == 6:
                    insertData = [data[m][j]["id"], data[m][j]["basic"], data[m][j]["match"],data[m][j]["m_i"]]
                elif m == 7:
                    insertData = [data[m][j]["id"], data[m][j]["thread"],data[m][j]["th_i"]]

                row_ind = row_ind[0] + str(i)
                worksheet1.write_row(row_ind, insertData,bold_body)
                i += 1
    # print(m_ind)
    
    # worksheet1.merge_range(1,row_ind_l[0],1,row_ind_l[Cap_charl.index(row_ind_l[1])-2], head_name[0])
    #设置表头格式
    for i in range(len(row_ind_l)):
        worksheet1.merge_range(0,Cap_charl.index(row_ind_l[i]),0,Cap_charl.index(row_ind_l[i]) + len(title[m_ind[i]]) -1, head_name[m_ind[i]],merge_format) #索引从0开始


    workbook.close()




def result2excel(fileName,opt):
    
    data = list2data(txt2list(opt))

    xw_toExcel(data,fileName,title,head_name)

# fileName = 'test.xlsx'
# result2excel(fileName)
# xw_toExcel(testData, fileName)