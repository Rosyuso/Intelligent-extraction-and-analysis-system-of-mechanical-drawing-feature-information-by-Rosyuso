f = open('special_result.txt','r',encoding='utf-8')
coor_list = f.readlines() #存成每一行数据的列表
# print(coor_list)
L_result = list()
for i in coor_list:
    L_result.append(i.split('\t')[1])


print(L_result)
diameter_dict = dict()
D_ind_L = list()
R_ind_L = list()

index = 1
for i in range(1,len(L_result)):
    if L_result[i][0] == '∅': #单纯直径 ,形如∅16
        diameter_dict["D_" + str(i)] = L_result[i][1:]
        D_ind_L.append(i)
    elif L_result[i][0] == 'R': #单纯半径 ,形如R16
        diameter_dict["R_" + str(i)] = L_result[i][1:]
        R_ind_L.append(i)
    elif L_result[i][1] == 'X' and L_result[i][2] == '∅': #圆周阵列孔（相同孔），例如2X∅12
        diameter_dict["Ds_num_" + L_result[i].split('X')[0]] = L_result[i].split('∅')[1]
    elif L_result[i][1] == 'X' and L_result[i][2] == 'R': #圆周阵列孔（相同孔），例如2X∅12
        diameter_dict["Rs_num_" + L_result[i].split('X')[0]] = L_result[i].split('R')[1]
print(diameter_dict)
