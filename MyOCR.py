import cv2
import numpy as np
import os 
import my_detector
import skew_correction
import re 
import shutil
import result_analysis
import matching


# # 清空上次识别的结果
# crop_list = [] #鼠标截取的坐标，形如[[(x1,y1),(x2,y2)],[(x3,y3),(x4,y4)]...]
# # img = cv2.imread('D:/vs_python_opencv_tesseract/package/figures/test4.png') #输入完整图纸
# path ='./' #存放截图的文件夹
# # print(os.path.realpath(__file__))
# detect_folder = ''  #存放检测到文本截图的文件夹
# result_txt = '' #存放识别结果的txt文件
rotate_path = './original_rotate'
# print(img.shape)
# cropped = img[100:500,400:500]
# cv2.imshow('cropped',cropped)
# cv2.waitKey(0)

def rotate(img_name,rotate_path):
    '''生成右旋90度的图片并保存'''
    img=cv2.imread(os.path.join(rotate_path,img_name))
    img90=np.rot90(img,3)
    h_90 = img90.shape[1]
    cv2.imwrite(os.path.join(rotate_path,img_name.split('.')[0] + '_90.png'), img90)
    return h_90
# rotate('test4.png','./original_rotate')

def get_h(img_name,rotate_path):
    '''获得图片的高'''
    img=cv2.imread(os.path.join(rotate_path,img_name),1)
    h = img.shape[0]
    return h


def detection(img_name,path):
    '''调用craft,返回整合好的横竖坐标列表,截取并保存每个坐标图'''
    img = cv2.imread(os.path.join(rotate_path,img_name))
    img_90 = cv2.imread(os.path.join(rotate_path,img_name.split('.')[0] + '_90.png'))
    normal_hori_block,normal_vert_block,skew_hori_block = my_detector.block_clean(img_90, os.path.join(rotate_path,'res_' + img_name.split('.')[0]+'.txt'), os.path.join(rotate_path,'res_' + img_name.split('.')[0]+'_90.txt'))
    print('倾斜文本坐标',skew_hori_block)
    # 两个列表都只含横框，截图识别后把纵检测的横框转换成横检测里的框，再展示
    # print('已处理'*10,normal_hori_block,'\n',normal_vert_block,skew_hori_block)
    #      [['537', '24', '571', '59'], ['143', '95', '195', '128'], ['191', '271', '225', '304'],
    #     ['371', '271', '405', '304'], ['569', '271', '606', '304'], ['63', '399', '114', '434'], 
    #     ['807', '411', '843', '445'], ['960', '415', '984', '445'], ['1032', '594', '1065', '631'],
    #     ['828', '602', '875', '642'], ['807', '774', '843', '808'], ['1137', '22', '1187', '59'],
    #      ['625', '365', '699', '397'], ['774', '569', '862', '613'], ['575', '765', '654', '798']]
    for i in normal_hori_block:
        # 对于每个坐标截图保存
        if int(i[0]) > img.shape[1] or int(i[2]) > img.shape[1] or int(i[1]) > img.shape[0] or int(i[3]) > img.shape[0]:
            continue
        print(i,'H已处理')
        hcropped_coor_img = img[int(i[1]):int(i[3]),int(i[0]):int(i[2])]
        cv2.imwrite(path+'H,'+str(i)[1:-1]+'.png',hcropped_coor_img)

    for m in skew_hori_block:
        result = skew_correction.skew_correction(img,m)
        if result is False:
            print('倾斜处理失败')
            continue
        else:
            cv2.imwrite(path+'HS,'+str(m)[1:-1]+'.png',result)
            print(m,'HS已处理')

    for j in normal_vert_block: #,skew_hori_block:
        print(j,'V已处理')
        # 对于每个坐标截图保存
        if int(j[0]) > img_90.shape[1] or int(j[2]) > img_90.shape[1] or int(j[1]) > img_90.shape[0] or int(j[3]) > img_90.shape[0]:
            continue
        vcropped_coor_img = img_90[int(j[1]):int(j[3]),int(j[0]):int(j[2])]
        
        cv2.imwrite(path+'V,'+str(j)[1:-1]+'.png',vcropped_coor_img)

# detection('test4.png')

# def eng_digits(img_name):
#     '''识别英文和数字'''
#     # cropped_img = img[cc[0][1]:cc[1][1],cc[0][0]:cc[1][0]] #截取图片
#     os.system('''D:/anaconda/envs/pytorch_/python.exe d:/vs_python_opencv_tesseract/package/normal_char.py \
#         --Transformation TPS \
#             --FeatureExtraction ResNet \
#                 --SequenceModeling BiLSTM \
#                     --Prediction Attn \
#                         --image_folder normal_cropped_img/ \
#                             --saved_model TPS-ResNet-BiLSTM-Attn-case-sensitive.pth \
#                                 --sensitive''') 



def recognition1():
    '''普通模式'''
    os.system("D:/anaconda/envs/pytorch_/python.exe d:/vs_python_opencv_tesseract/package/special_char.py \
        --Transformation TPS \
            --FeatureExtraction ResNet \
                --SequenceModeling BiLSTM \
                    --Prediction CTC \
                        --image_folder special_cropped_img/ \
                            --saved_model self_trained_6.pth") 


def recognition2():
    '''跳过检测直接识别公差框、孔特征等'''
    os.system("D:/anaconda/envs/pytorch_/python.exe d:/vs_python_opencv_tesseract/package/manual_char.py \
        --Transformation TPS \
            --FeatureExtraction ResNet \
                --SequenceModeling BiLSTM \
                    --Prediction Attn \
                        --image_folder manual_cropped_img \
                            --saved_model self_Attn.pth") 


def result_feedback(txt_name,img_name):
    '''把纵向检测的结果统一到横向图上，返回统一后的坐标列表'''
    h = get_h(img_name,rotate_path)
    f = open(txt_name,'r',encoding='utf-8')
    result_list = f.readlines()
    # 列表的元素是形如"special_cropped_img/H,'41', '233', '77', '250'.png\tR15                      \t0.9995\n" 的字符串
    # print(result_list)
    clean_list = []
    for i in range(1,len(result_list)):
        # print(result_list[i])
        if result_list[i].split(',')[0][-1] == 'V':
            trans_v = (int(result_list[i].split('\'')[3]),h - int(result_list[i].split('\'')[5]),int(result_list[i].split('\'')[7]),h - int(result_list[i].split('\'')[1]),result_list[i].split('\t')[1])
            # 以'分割字符串
            clean_list.append(trans_v)
        elif result_list[i].split(',')[0][-1] == 'H':
            clean_list.append((int(result_list[i].split('\'')[1]),int(result_list[i].split('\'')[3]),int(result_list[i].split('\'')[5]),int(result_list[i].split('\'')[7]),result_list[i].split('\t')[1]))
        elif result_list[i].split(',')[0].split('/')[-1] == 'HS':
            # print(result_list[i].split(','))
            # print(int(result_list[i].split(',')[8].split(']')[0]))
            clean_list.append((int(result_list[i].split(',')[1][1:]),int(result_list[i].split(',')[2][:-1]),int(result_list[i].split(',')[3][2:]),int(result_list[i].split(',')[4][:-1]),int(result_list[i].split(',')[5][2:]),int(result_list[i].split(',')[6][:-1]),int(result_list[i].split(',')[7][2:]),int(result_list[i].split(',')[8].split(']')[0]),result_list[i].split('\t')[1]))
        # print(clean_list)
    return clean_list


def Visualization(result_list,img_name):
    '''可视化：将检测结果显示在图片上'''
    img = cv2.imread(os.path.join(rotate_path,img_name))
    for i in result_list:
        if len(i) == 9:
            cv2.line(img,(i[0],i[1]),(i[2],i[3]),(0,255,0),1)
            cv2.line(img,(i[2],i[3]),(i[4],i[5]),(0,255,0),1)
            cv2.line(img,(i[4],i[5]),(i[6],i[7]),(0,255,0),1) 
            cv2.line(img,(i[6],i[7]),(i[0],i[1]),(0,255,0),1)
            # cv2.putText(img,i[8],(i[0]-5,i[1]-5),cv2.FONT_ITALIC,0.5,(255,0,0),1)
            continue
            # cv2.drawContours(img, [i], 0, (255, 0, 0),1)
        cv2.rectangle(img,(i[0],i[1]),(i[2],i[3]),(0,0,255),1)
        # cv2.putText(img,i[4],(i[0]-5,i[1]-5),cv2.FONT_ITALIC,0.5,(255,0,0),1)
        cv2.namedWindow('recg_result',cv2.WINDOW_NORMAL)
    cv2.imshow('recg_result',img)
    cv2.waitKey(0)


def res2excel(filename,opt):
    '''将识别结果写入Excel表中'''
    result_analysis.result2excel(filename,opt)


def myocr(opt, shaft=False):
    list_pic = os.listdir('./original_rotate')
    img_name = list_pic[0]
    img = cv2.imread(os.path.join(rotate_path,img_name))
    h_90 = rotate(img_name,rotate_path)
    if opt == 0: #普通模式
        shutil.rmtree('./special_cropped_img')
        os.mkdir('special_cropped_img')
        detection(img_name,'./special_cropped_img/') #生成裁剪后的文本截图
        recognition1()
        clean_list = result_feedback('special_result.txt',img_name)
        Visualization(clean_list,img_name)
        coor,text = result_analysis.result2excel('test.xlsx',True, h_90)
        # 轴类
        if shaft == True:
            cleansed_img = matching.get_cleansed(img)
            cv2.imshow('cleansed_img', cleansed_img)
            cv2.waitKey(0)
            rect, shaft_length = matching.split_rect(cleansed_img)
            # corner = matching
            matching.text_match_coor(coor, text, rect, shaft_length)
            print('文本->',text)
            print('坐标->', coor)
            print('矩形阶梯截面->', rect)
    elif opt == 1: #跳过检测直接识别
        # shutil.rmtree('./manual_cropped_img')
        # os.mkdir('manual_cropped_img')
        recognition2()
        # clean_list = result_feedback('manual_result.txt',img_name)
        # Visualization(clean_list,img_name)
        result_analysis.result2excel('test.xlsx',False, h_90) #把手动截取的放入识别结果中




#改名字！！！
'''Traceback (most recent call last):
  File "d:/vs_python_opencv_tesseract/package/MyOCR.py", line 135, in <module>
    main('465.png',True)
  File "d:/vs_python_opencv_tesseract/package/MyOCR.py", line 115, in main
    h_90 = rotate(img_name,rotate_path)
  File "d:/vs_python_opencv_tesseract/package/MyOCR.py", line 29, in rotate
    img90=np.rot90(img,3)
  File "<__array_function__ internals>", line 5, in rot90
  File "D:\anaconda\envs\pytorch_\lib\site-packages\numpy\lib\function_base.py", line 125, in rot90
    raise ValueError("Axes={} out of range for array of ndim={}."
ValueError: Axes=(0, 1) out of range for array of ndim=0.'''


# print(list_pic)
if __name__ == '__main__':
    myocr(0,shaft=True)
    shutil.rmtree('./original_rotate')
    os.mkdir('original_rotate')




