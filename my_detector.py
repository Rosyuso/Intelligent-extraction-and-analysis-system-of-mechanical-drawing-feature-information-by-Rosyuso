import numpy as np
import cv2
import os


pixel_threshold = 5 
hw_threshold = 1.3 #高宽比



def clean_coor(coor_list):
    res=[]
    coor_cleansed = []
    for x in range(len(coor_list)):
        if x%2==0:
            res.append(coor_list[x])
        else:
            pass
    for i in res:
        L = []
        L.append(i.split(',')[0])
        L.append(i.split(',')[1])
        L.append(i.split(',')[4])
        L.append(i.split(',')[5])
        coor_cleansed.append(L)
    return coor_cleansed


def integration_check(coor_cleansed, rotate, w=None, h=None):
    '''判定准则
    1.若两框中心x或y方向距离小于边长相交的距离（或者很接近），则判定为一个框，以大框为主扩展；
    2.横竖检测后先合并框，再将两次检测到的竖框互换；
    2.返回元组：修改后的坐标列表与需要旋转后检测的列表
    '''
    center_coor = []
    for i in coor_cleansed:
        center = (0.5 * (int(i[2])+int(i[0])), 0.5 * (int(i[3])+int(i[1])))
        center_coor.append(center) #得到框中心点坐标的列表

    index = []
    new_block_list = []
    for j in range(len(coor_cleansed)): #合并框
        for k in range(j+1,len(coor_cleansed)):
            # print(j,k)
            center_dis_x = abs(center_coor[j][0]-center_coor[k][0])
            center_dis_y = abs(center_coor[j][1]-center_coor[k][1])
            crit_dis_x = 0.5*(int(coor_cleansed[j][2])-int(coor_cleansed[j][0]))+0.5*(int(coor_cleansed[k][2])-int(coor_cleansed[k][0]))
            crit_dis_y = 0.5*(int(coor_cleansed[j][3])-int(coor_cleansed[j][1]))+0.5*(int(coor_cleansed[k][3])-int(coor_cleansed[k][1]))
            
            if (abs(int(coor_cleansed[j][3]) - int(coor_cleansed[k][3])) <= pixel_threshold or abs(int(coor_cleansed[j][1]) - int(coor_cleansed[k][1])) <= pixel_threshold or center_dis_y <= pixel_threshold ) and center_dis_x <= crit_dis_x :
                # 两框处于同一水平线且中心x方向距离小于临界距离,生成新的大框
                new_block = [min(coor_cleansed[j][0],coor_cleansed[k][0]),min(coor_cleansed[j][1],coor_cleansed[k][1]),max(coor_cleansed[j][2],coor_cleansed[k][2]),max(coor_cleansed[j][3],coor_cleansed[k][3])] 
                new_block_list.append(new_block) #将新框的坐标写入列表中
                index.append(j) #记录索引号 
                index.append(k)
            elif (abs(int(coor_cleansed[j][2]) - int(coor_cleansed[k][2])) <= pixel_threshold or abs(int(coor_cleansed[j][0]) - int(coor_cleansed[k][0])) <= pixel_threshold or center_dis_x <= pixel_threshold ) and center_dis_y <= crit_dis_y :
                # 两框处于同一竖直线且中心y方向距离小于临界距离,生成新的大框
                new_block = [min(coor_cleansed[j][0],coor_cleansed[k][0]),min(coor_cleansed[j][1],coor_cleansed[k][1]),max(coor_cleansed[j][2],coor_cleansed[k][2]),max(coor_cleansed[j][3],coor_cleansed[k][3])]
                new_block_list.append(new_block) #将新框的坐标写入列表中
                index.append(j) #记录索引号 
                index.append(k)

    coor_cleansed = [coor_cleansed[i] for i in range(len(coor_cleansed)) if (i not in index)] #删除选中的框

    for l in new_block_list:
        coor_cleansed.append(l) #将新生成的大框写入框坐标列表中
    vert_block = []
    vert_index = []
    for m in coor_cleansed: #在正常检测情况下，如果检测到竖框，则识别右旋90度对应位置的内容
        # 判断竖框
        width = int(m[2]) - int(m[0])
        height = int(m[3]) - int(m[1])
        if height / width >= hw_threshold:
            if rotate == 90:  #当前检测为横向，生成右旋90度的坐标
                vert_block.append([str(h - int(m[3])),m[0],str(h - int(m[1])),m[2]])
                vert_index.append(coor_cleansed.index(m)) #把竖框的索引放到index列表中
                # print(vert_block,'h_v')
            elif rotate == -90: #当前检测为纵向，生成左旋90度的坐标
                vert_block.append([m[1],str(w - int(m[2])),m[3],str(w - int(m[0]))])
                vert_index.append(coor_cleansed.index(m)) #把竖框的索引放到index列表中
                # print(vert_block,'v_h')

    
    coor_cleansed = [coor_cleansed[i] for i in range(len(coor_cleansed)) if (i not in vert_index)] #删除选中的框
    # 已合并完成，并剔除竖框（竖框存到对应右旋90度的图片坐标里）

    return coor_cleansed,vert_block #返回一个元组 （coor_cleansed,vert_block）


def similariity_check():
    '''比较横竖两次检测的相同框'''
    pass

def del_sim(block_list):
    '''删除同位置的框'''
    index = []
    for i in range(len(block_list)):
        for j in range(i+1, len(block_list)):
            # print(block_list[j])
            if (abs((int(block_list[i][0]) - int(block_list[j][0]))) <= pixel_threshold) and \
               (abs((int(block_list[i][1]) - int(block_list[j][1]))) <= pixel_threshold) and \
               (abs((int(block_list[i][2]) - int(block_list[j][2]))) <= pixel_threshold) and \
               (abs((int(block_list[i][3]) - int(block_list[j][3]))) <= pixel_threshold):
               index.append(j)
    # print(index)      
    block_list = [block_list[i] for i in range(len(block_list)) if (i not in index)] #删除选中的框
    return block_list


def block_clean(hori_path,hori_txt,vert_txt):
    # img_hori = cv2.imread('./figures/'+ hori_path)
    # img_vert = np.rot90(img_hori,axes=(1,0)) #右旋90度
    img_vert = cv2.imread('test4_90.png')#右旋90度
   
    # 调用craft,生成定位的坐标TXT文件
    os.system("D:/anaconda/envs/pytorch_/python.exe D:/vs_python_opencv_tesseract/package/craft_test.py ") #python 后面需要接绝对路径，生成txt文件
    f = open(hori_txt,'r') #图片的检测结果txt
    coor_list = f.readlines() #存成每一行数据的列表
    f_90 = open(vert_txt,'r') #右转90图片的检测结果txt
    coor_list_90 = f_90.readlines() #存成每一行数据的列表
    h, w, d = img_vert.shape
    coor_cleansed = clean_coor(coor_list)
    coor_cleansed_90 = clean_coor(coor_list_90)
    new_block_hori = integration_check(coor_cleansed,90, h=h)
    new_block_vert = integration_check(coor_cleansed_90,-90,w=w)
    final_hori_block = del_sim(new_block_hori[0] + new_block_vert[1])
    final_vert_block = del_sim(new_block_vert[0] + new_block_hori[1])
    # final_block = final_hori_block + final_vert_block
    # print(final_block)
    return final_hori_block,final_vert_block

# final_hori_block,final_vert_block = block_clean('res_test4.jpg','res_test4.jpg'.split('.')[0]+'.txt','res_test4.jpg'.split('.')[0]+'_90.txt')

# print(final_hori_block,final_hori_block)

# img_hori = cv2.imread('res_test4.jpg')
# img_vert = np.rot90(img_hori,axes=(1,0)) #右旋90度
# f = open('res_test4.txt','r') #图片的检测结果txt
# coor_list = f.readlines() #存成每一行数据的列表
# f_90 = open('res_test4_90.txt','r') #右转90图片的检测结果txt
# coor_list_90 = f_90.readlines() #存成每一行数据的列表
# h, w, d = img_vert.shape

# coor_cleansed = clean_coor(coor_list)
# print(len(coor_cleansed))
# new_block_hori = similarity_criterion(coor_cleansed,rotate=90)
# new_block_vert = similarity_criterion(coor_cleansed,rotate=-90,w=w)
# final_hori_block = new_block_hori[0] + new_block_vert[1]
# final_vert_block = new_block_vert[0] + new_block_hori[1]
# print(final_hori_block,final_hori_block)
# print(new_block,len(new_block[0]))
# print(img.shape)
# imgtes = cv2.rectangle(img,(166,22),(240,57),(255,0,0),1)
# cv2.imshow('test',imgtes)
# cv2.waitKey(0)