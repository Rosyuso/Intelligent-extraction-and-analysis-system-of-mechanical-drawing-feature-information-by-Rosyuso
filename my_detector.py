import numpy as np
import cv2
import os


pixel_threshold = 5 
hw_threshold = 1.2 #高宽比



def clean_coor(coor_list):
    res=[]
    coor_normal_cleansed = []
    coor_skew_cleansed = []
    for x in range(len(coor_list)):
        if x%2==0:
            res.append(coor_list[x])
    print('-0-0-0-0',res)
    for i in res:
        tmp = i.split(',')
        if int(tmp[0]) != int(tmp[6]) or int(tmp[1]) != int(tmp[3]) or  int(tmp[2]) != int(tmp[4]) or int(tmp[5])!= int(tmp[7]):
            #判定为倾斜框
            L_skew = list()
            L_skew.extend([[int(tmp[0]),int(tmp[1])],[int(tmp[2]),int(tmp[3])],[int(tmp[4]),int(tmp[5])],[int(tmp[6]),int(tmp[7])]])
            coor_skew_cleansed.append(L_skew)
        else:
            L_normal = list()
            L_normal.extend([i.split(',')[0],i.split(',')[1],i.split(',')[4],i.split(',')[5]])
            coor_normal_cleansed.append(L_normal)
    print('倾斜',coor_skew_cleansed)
    print('垂直',coor_normal_cleansed)

    return coor_normal_cleansed, coor_skew_cleansed


def integration_check(coor_cleansed, rotate, w=None, h=None):
    '''判定准则
    1.若两框中心x或y方向距离小于边长相交的距离（或者很接近），则判定为一个框，以大框为主扩展；
    2.横竖检测后先合并框，再将两次检测到的竖框互换；
    2.返回元组：修改后的坐标列表与需要旋转后检测的列表
    '''
    # center_coor = []
    # for i in coor_cleansed:
    #     center = (0.5 * (int(i[2])+int(i[0])), 0.5 * (int(i[3])+int(i[1])))
    #     center_coor.append(center) #得到框中心点坐标的列表

    # index = []
    # new_block_list = []
    # for j in range(len(coor_cleansed)): #合并框
    #     for k in range(j+1,len(coor_cleansed)):
    #         # print(j,k)
    #         center_dis_x = abs(center_coor[j][0]-center_coor[k][0])
    #         center_dis_y = abs(center_coor[j][1]-center_coor[k][1])
    #         crit_dis_x = 0.5*(int(coor_cleansed[j][2])-int(coor_cleansed[j][0]))+0.5*(int(coor_cleansed[k][2])-int(coor_cleansed[k][0]))
    #         crit_dis_y = 0.5*(int(coor_cleansed[j][3])-int(coor_cleansed[j][1]))+0.5*(int(coor_cleansed[k][3])-int(coor_cleansed[k][1]))
            
    #         if (abs(int(coor_cleansed[j][3]) - int(coor_cleansed[k][3])) <= pixel_threshold or abs(int(coor_cleansed[j][1]) - int(coor_cleansed[k][1])) <= pixel_threshold or center_dis_y <= pixel_threshold ) and center_dis_x <= crit_dis_x :
    #             # 两框处于同一水平线且中心x方向距离小于临界距离,生成新的大框
    #             new_block = [min(coor_cleansed[j][0],coor_cleansed[k][0]),min(coor_cleansed[j][1],coor_cleansed[k][1]),max(coor_cleansed[j][2],coor_cleansed[k][2]),max(coor_cleansed[j][3],coor_cleansed[k][3])] 
    #             new_block_list.append(new_block) #将新框的坐标写入列表中
    #             index.append(j) #记录索引号 
    #             index.append(k)
    #         elif (abs(int(coor_cleansed[j][2]) - int(coor_cleansed[k][2])) <= pixel_threshold or abs(int(coor_cleansed[j][0]) - int(coor_cleansed[k][0])) <= pixel_threshold or center_dis_x <= pixel_threshold ) and center_dis_y <= crit_dis_y :
    #             # 两框处于同一竖直线且中心y方向距离小于临界距离,生成新的大框
    #             new_block = [min(coor_cleansed[j][0],coor_cleansed[k][0]),min(coor_cleansed[j][1],coor_cleansed[k][1]),max(coor_cleansed[j][2],coor_cleansed[k][2]),max(coor_cleansed[j][3],coor_cleansed[k][3])]
    #             new_block_list.append(new_block) #将新框的坐标写入列表中
    #             index.append(j) #记录索引号 
    #             index.append(k)

    # coor_cleansed = [coor_cleansed[i] for i in range(len(coor_cleansed)) if (i not in index)] #删除选中的框

    # for l in new_block_list:
    #     coor_cleansed.append(l) #将新生成的大框写入框坐标列表中
    '''vert_block = []
    vert_index = []
    for m in coor_cleansed: #在正常检测情况下，如果检测到竖框，则识别右旋90度对应位置的内容
        # 判断竖框
        width = int(m[2]) - int(m[0])
        height = int(m[3]) - int(m[1])
        # print(m,width)
        if width == 0  or height == 0:
            coor_cleansed.index(m)
            continue
        elif height / width >= hw_threshold:
            if rotate == 90:  #当前检测为横向，生成右旋90度的坐标
                if (h - int(m[3]) < 0):
                    vert_index.append(coor_cleansed.index(m)) #把竖框的索引放到index列表中
                else:
                    vert_block.append([str(h - int(m[3])),m[0],str(h - int(m[1])),m[2]])
                    vert_index.append(coor_cleansed.index(m)) #把竖框的索引放到index列表中
                # print(vert_block,'h_v')
            elif rotate == -90 and w - int(m[2]) > 0 and w - int(m[0]) > 0: #当前检测为纵向，生成左旋90度的坐标
                vert_block.append([m[1],str(w - int(m[2])),m[3],str(w - int(m[0]))])
                vert_index.append(coor_cleansed.index(m)) #把竖框的索引放到index列表中

            else:
                raise Exception('invalid rotation parameter')

    
    coor_cleansed = [coor_cleansed[i] for i in range(len(coor_cleansed)) if (i not in vert_index)] #删除选中的框
    # 已合并完成，并剔除竖框（竖框存到对应右旋90度的图片坐标里）
    '''
    vert_index = []
    for m in coor_cleansed: #在正常检测情况下，如果检测到竖框，则识别右旋90度对应位置的内容
        # 判断竖框
        # print(m)
        width = int(m[2]) - int(m[0])
        height = int(m[3]) - int(m[1])
        if height / width >= hw_threshold:
            if rotate == 90:  #当前检测为横向，生成右旋90度的坐标
                # vert_block.append([str(h - int(m[3])),m[0],str(h - int(m[1])),m[2]])
                vert_index.append(coor_cleansed.index(m)) #把竖框的索引放到index列表中
                # print(vert_block,'h_v')
            elif rotate == -90: #当前检测为纵向，直接删除竖框文本，剩下的横框截图识别后再转换到横检测的坐标
                # vert_block.append([m[1],str(w - int(m[2])),m[3],str(w - int(m[0]))])
                vert_index.append(coor_cleansed.index(m)) #把竖框的索引放到index列表中
                # print(vert_block,'v_h')

    
    coor_cleansed = [coor_cleansed[i] for i in range(len(coor_cleansed)) if (i not in vert_index)] #删除选中的框
    # 已合并完成，并剔除竖框（竖框存到对应右旋90度的图片坐标里）

    return coor_cleansed #,vert_block #返回一个元组 （coor_cleansed,vert_block）


def similariity_check():
    '''比较横竖两次检测的相同框'''

    pass

def del_sim(block_list):
    '''
    1.删除同位置的框：以（两次检测中的长方形）为准
    2.若出现大框套小框的情况，删除其中的小框
    '''
    index = []
    for i in range(len(block_list)):
        for j in range(i+1, len(block_list)):
            # print(block_list[j])
            if (abs((int(block_list[i][0]) - int(block_list[j][0]))) <= pixel_threshold) and \
               (abs((int(block_list[i][1]) - int(block_list[j][1]))) <= pixel_threshold) and \
               (abs((int(block_list[i][2]) - int(block_list[j][2]))) <= pixel_threshold) and \
               (abs((int(block_list[i][3]) - int(block_list[j][3]))) <= pixel_threshold) :
               index.append(j)
            elif int(block_list[i][0]) < 0 or int(block_list[i][1]) < 0 or int(block_list[i][2]) < 0 or int(block_list[i][3]) < 0 : #出现负坐标也删除
                index.append(j)
    # print(index)      
    block_list = [block_list[i] for i in range(len(block_list)) if (i not in index)] #删除选中的框
    return block_list


def block_clean(img_vert,hori_txt,vert_txt):
    # img_hori = cv2.imread('./figures/'+ hori_path)
    # img_vert = np.rot90(img_hori,axes=(1,0)) #右旋90度
    # img_vert = cv2.imread(os.path.join(rotate_path,img_name.split('.')[0] + '_90.png'))#右旋90度
    # 调用craft,生成定位的坐标TXT文件
    os.system("D:/anaconda/envs/pytorch_/python.exe D:/vs_python_opencv_tesseract/package/craft_test.py ") #python 后面需要接绝对路径，生成txt文件
    f = open(hori_txt,'r') #图片的检测结果txt
    coor_list = f.readlines() #存成每一行数据的列表
    # print('-原始横'*10,coor_list)
    f_90 = open(vert_txt,'r') #右转90图片的检测结果txt
    coor_list_90 = f_90.readlines() #存成每一行数据的列表
    # h, w, d = img_vert.shape
    w, h = img_vert.shape[:-1]
    coor_cleansed,hori_skew_cleansed = clean_coor(coor_list)
    
    # print('-未处理横'*10,coor_cleansed)
    coor_cleansed_90 = clean_coor(coor_list_90)[0]
    # print('-未处理竖'*10,coor_cleansed)
    new_block_hori = integration_check(coor_cleansed,90, h=h)
    new_block_vert = integration_check(coor_cleansed_90,-90,w=w)
    # final_hori_block = del_sim(new_block_hori[0] + new_block_vert[1])
    # final_vert_block = del_sim(new_block_vert[0] + new_block_hori[1])
    # final_block = final_hori_block + final_vert_block
    # print(final_block)
    return new_block_hori,new_block_vert,hori_skew_cleansed

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