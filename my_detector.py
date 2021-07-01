import numpy as np
import cv2
import os


pixel_threshold = 5 
hw_threshold_hori = 1.1 #横检测高宽比
hw_threshold_vert = 1 #纵检测高宽比
area_threshold = 2 #面积检测比


def clean_coor(coor_list):
    '''对craft检测以后的坐标进行清洗，返回正常框和倾斜框的坐标列表（左上和右下）'''
    res=[]
    coor_normal_cleansed = []
    coor_skew_cleansed = []
    for x in range(len(coor_list)):
        if x%2==0:
            res.append(coor_list[x])
    # print('-0-0-0-0',res)
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
    # print('垂直',coor_normal_cleansed)

    return coor_normal_cleansed, coor_skew_cleansed


def get_mode(list):
    '''获得列表里的众数'''
    counts = np.bincount(list)
    mode = np.argmax(counts)  #获得高度的众数
    return mode


def integration_check(coor_cleansed, rotate,hw_threshold,X):
    '''
    对横检测和纵检测的两次识别结果进行整合。
    
    ##判定准则
    1.若两框中心x或y方向距离小于边长相交的距离（或者很接近），则判定为一个框，以大框为主扩展；
    2.横竖检测后先合并框，再将两次检测到的竖框互换；
    3.返回元组：修改后的坐标列表与需要旋转后检测的列表;
    4. 若某个框的面积（？）大于平均值若干倍，则是重复选取的大框，删掉此框;
    5. 若只有一个竖排数字，横检测时保留检测，但无法识别；竖检测时被当做竖框删除。 
            解决办法：因为大部分横框的高都为字符高度，基本固定，若高度小于此高度且宽度等于字符高度，判定为单个竖排字符，在竖图上截图，在横图上显示
    '''


    '''center_coor = []
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
    vert_index = [] #用于存放要删除框的索引
    vert_block = []
    area = []
    hori_height,hori_width = [],[]


    for m in coor_cleansed:
        width = int(m[2]) - int(m[0])
        height = int(m[3]) - int(m[1])
        hori_height.append(height)
        hori_width.append(width) 
        area.append(width*height)

    print('总平均面积',np.mean(area))
    area.remove(max(area))
    area.remove(min(area))
    mode= get_mode(hori_height) 

    for m in coor_cleansed: #在正常检测情况下，如果检测到竖框，则识别右旋90度对应位置的内容
 
        if not m[1] and not m[2] and not m[3] and not m[0]: #遇到全0的直接删除
            vert_index.append(coor_cleansed.index(m))
            continue
        
        width = int(m[2]) - int(m[0])
        height = int(m[3]) - int(m[1])
        #删除单个竖排字符-------------------------------------------------
        if len(hori_height) >= 5:
            # print('字符高度众数：', mode)
            if rotate == 90:
                if width == mode and height < width: #该框的宽等于高度众数且高度小于宽度,判定为单个竖排字符
                    print('横检测竖排单个字符？',m,width,mode,height)
                    if abs(height-mode) <= 2:
                        continue
                    vert_block.append([str(X - int(m[3])),m[0],str(X - int(m[1])),m[2]])
                    print(vert_block)
                    vert_index.append(coor_cleansed.index(m))

            elif rotate == -90:
                if abs(width-mode) <= 2 and height < width: #该框的宽等于高度众数且高度小于宽度,判定为单个竖排字符
                    print('纵检测竖排单个字符？',m,width,mode,height)
                    if abs(height-mode) <= 2:
                        continue
                    vert_block.append([m[1],str(X - int(m[2])),m[3],str(X - int(m[0]))])
                    # vert_index.append(coor_cleansed.index(m))
        
        #删除竖框-------------------------------------------------
        if rotate == 90:  #当前检测为横向，生成右旋90度的坐标
            if height and width and height / width >= hw_threshold: #直接删除竖；框文本
                # if abs(height-mode) <= 3: # and height / width >= 1.2:
                #     print('检测到单个竖排字符(H)', m[0],height,mode)
                #     continue
                vert_index.append(coor_cleansed.index(m)) #把竖框的索引放到index列表中
                print('横检测要删除的竖框：',m[0])
            # if abs(width-mode) <= 2 and height < width: #该框的宽等于高度众数且高度小于宽度,判定为单个竖排字符
            # if width == mode and height < width: #该框的宽等于高度众数且高度小于宽度,判定为单个竖排字符
            #     print('横检测竖排文本？',m,width,mode,height)
            #     if abs(height-mode) <= 2:
            #         continue
            #     vert_block.append([str(X - int(m[3])),m[0],str(X - int(m[1])),m[2]])
            #     print(vert_block)
            #     vert_index.append(coor_cleansed.index(m))
            # print(vert_block,'h_v')
        elif rotate == -90: #当前检测为纵向，，剩下的横框截图识别后再转换到横检测的坐标
            if height and width and height / width >= hw_threshold:#直接删除竖框文本
                vert_index.append(coor_cleansed.index(m)) #把竖框的索引放到index列表中
                print('纵检测要删除的竖框：',m[0])

            # if abs(width-mode) <= 2 and height < width: #该框的宽等于高度众数且高度小于宽度,判定为单个竖排字符
            #     print('纵检测竖排文本？',m,width,mode,height)
            #     if abs(height-mode) <= 2:
            #         continue
            #     vert_block.append([m[1],str(X - int(m[2])),m[3],str(X - int(m[0]))])
            #     vert_index.append(coor_cleansed.index(m))

            # print(np.mean(area))
        #去掉最大面积和最小面积求平均面积-----------------------------------
        #待添加倾斜框面积的判定
        if len(area) > 2:
            new_mean = np.mean(area) if len(area) else None
            # print('去掉极值后的平均面积',new_mean)
            if new_mean:
                # if width*height > area_threshold*new_mean or width*height < new_mean/area_threshold:#面积太大或太小框删除
                if width*height > area_threshold*new_mean: # or width*height < new_mean/area_threshold:#面积太大框删除
                    if height / width < 0.5:
                        continue
                    print('面积太大，删除：',m[0])
                    vert_index.append(coor_cleansed.index(m)) #把竖框的索引放到index列表中
            
                    # print('面积-》',m[0],width*height)
            

    vert_index = list(set(vert_index)) #去除重复的项
    print('需要删除的索引',vert_index)
    coor_cleansed = [coor_cleansed[i] for i in range(len(coor_cleansed)) if (i not in vert_index)] #删除选中的框
    # 已合并完成，并剔除竖框（竖框存到对应右旋90度的图片坐标里）

    return coor_cleansed #,vert_block #返回一个元组 （coor_cleansed,vert_block）


def similariity_check(hori_block,vert_block,X):
    '''
    对两次检测中的位置相同的框进行整合

    ##判定准则
    1.如果框是正方形，以横检测为主；
    2.如果两次检测的框中心坐标距离小于一定值，以横检测为主，删除纵检测的框
    ##待添加：
     纵检测检测到的竖框和横检测同位置的倾斜框，横检测检测到的竖框和纵检测同位置的倾斜框，如何合并？
     若两框接近，一个框完全包含另一个框，则删除小框？还是大框？ 待定
    计算交并比！！ 中心接近并且交并比大于一定的值视为重叠框
    '''
    del_index = []

    for i in hori_block:
        for j in vert_block: 
            # [m[1],str(X - int(m[2])),m[3],str(X - int(m[0]))]
            rect_center_i = ((int(i[0])+int(i[2]))/2,(int(i[1])+int(i[3]))/2)
            rect_center_j = ((int(j[1])+int(j[3]))/2, (int(X - int(j[2]))+int(X - int(j[0])))/2)
            # print(rect_center_i,rect_center_j)
            #  ((int(i[0])+int(i[2]))/2, (int(i[1])+int(i[3]))/2),( (int(i[1])+int(i[3]))/2))
            if (rect_center_i[0]-rect_center_j[0])**2 + (rect_center_i[1]-rect_center_j[1])**2 < 100:
                print('bingo',i,j)
                del_index.append(vert_block.index(j))
            # if 

    vert_block = [vert_block[i] for i in range(len(vert_block)) if (i not in del_index)] #删除选中的框

    return vert_block

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
    '''读取检测后的TXT文件，生成处理后两次检测的框坐标列表，以及倾斜框'''
    os.system("D:/anaconda/envs/pytorch_/python.exe D:/vs_python_opencv_tesseract/package/craft_test.py ") #python 后面需要接绝对路径，生成txt文件
    f = open(hori_txt,'r') #图片的检测结果txt
    coor_list = f.readlines() #存成每一行数据的列表
    # print('-原始横'*10,coor_list)
    f_90 = open(vert_txt,'r') #右转90图片的检测结果txt
    coor_list_90 = f_90.readlines() #存成每一行数据的列表
    # h, w, d = img_vert.shape
    h,w = img_vert.shape[:-1]
    coor_cleansed,hori_skew_cleansed = clean_coor(coor_list) #只对横检测
    # print('-未处理横'*10,coor_cleansed)
    coor_cleansed_90 = clean_coor(coor_list_90)[0]
    # print('-未处理竖'*10,coor_cleansed)
    final_hori_block = integration_check(coor_cleansed,90, hw_threshold_hori,h)
    final_vert_block = integration_check(coor_cleansed_90,-90,hw_threshold_hori,w)
    # final_hori_block = final_hori_block[0] + final_vert_block[1]
    # final_vert_block = final_vert_block[0] + final_hori_block[1]
    final_vert_block = similariity_check(final_hori_block,final_vert_block,w)
    # final_block = final_hori_block + final_vert_block
    # print(final_block)
    return final_hori_block,final_vert_block,hori_skew_cleansed

