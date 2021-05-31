import cv2
import sys
import numpy as np
import os 
import my_detector
import re 
import shutil


# 清空上次识别的结果
crop_list = [] #鼠标截取的坐标，形如[[(x1,y1),(x2,y2)],[(x3,y3),(x4,y4)]...]
# img = cv2.imread('D:/vs_python_opencv_tesseract/package/figures/test4.png') #输入完整图纸
path ='./' #存放截图的文件夹
# print(os.path.realpath(__file__))
detect_folder = ''  #存放检测到文本截图的文件夹
result_txt = '' #存放识别结果的txt文件
rotate_path = './original_rotate'
# print(img.shape)
# cropped = img[100:500,400:500]
# cv2.imshow('cropped',cropped)
# cv2.waitKey(0)

def rotate(img_name,rotate_path):
    '''生成右旋90度的图片并保存'''
    img=cv2.imread(os.path.join(rotate_path,img_name))
    img90=np.rot90(img,3)
    h_90 = img90.shape[0]
    cv2.imwrite(os.path.join(rotate_path,img_name.split('.')[0] + '_90.png'), img90)
    return h_90
# rotate('test4.png','./original_rotate')

def get_h(img_name,rotate_path):
    img=cv2.imread(os.path.join(rotate_path,img_name),1)
    h = img.shape[0]
    return h


def detection(img_name,path):
    '''调用craft,返回整合好的横竖坐标列表,截取并保存每个坐标图'''
    img = cv2.imread(os.path.join(rotate_path,img_name))
    img_90 = cv2.imread(os.path.join(rotate_path,img_name.split('.')[0] + '_90.png'))
    final_hori_block,final_vert_block = my_detector.block_clean(img_90, os.path.join(rotate_path,'res_' + img_name.split('.')[0]+'.txt'), os.path.join(rotate_path,'res_' + img_name.split('.')[0]+'_90.txt'))
    print(final_hori_block,'\n',final_vert_block)
    #      [['537', '24', '571', '59'], ['143', '95', '195', '128'], ['191', '271', '225', '304'],
    #     ['371', '271', '405', '304'], ['569', '271', '606', '304'], ['63', '399', '114', '434'], 
    #     ['807', '411', '843', '445'], ['960', '415', '984', '445'], ['1032', '594', '1065', '631'],
    #     ['828', '602', '875', '642'], ['807', '774', '843', '808'], ['1137', '22', '1187', '59'],
    #      ['625', '365', '699', '397'], ['774', '569', '862', '613'], ['575', '765', '654', '798']]
    for i in final_hori_block:
        # 对于每个坐标截图保存
        if int(i[0]) > img.shape[1] or int(i[2]) > img.shape[1] or int(i[1]) > img.shape[0] or int(i[3]) > img.shape[0]:
            continue
        print(i)
        hcropped_coor_img = img[int(i[1]):int(i[3]),int(i[0]):int(i[2])]
        cv2.imwrite(path+'H,'+str(i)[1:-1]+'.png',hcropped_coor_img)
    for j in final_vert_block:
        print(j)
        # 对于每个坐标截图保存
        if int(j[0]) > img_90.shape[1] or int(j[2]) > img_90.shape[1] or int(j[1]) > img_90.shape[0] or int(j[3]) > img_90.shape[0]:
            continue
        vcropped_coor_img = img_90[int(j[1]):int(j[3]),int(j[0]):int(j[2])]
        
        cv2.imwrite(path+'V,'+str(j)[1:-1]+'.png',vcropped_coor_img)

# detection('test4.png')

def eng_digits(img_name):
    '''识别英文和数字'''
    # cropped_img = img[cc[0][1]:cc[1][1],cc[0][0]:cc[1][0]] #截取图片
    os.system('''D:/anaconda/envs/pytorch_/python.exe d:/vs_python_opencv_tesseract/package/normal_char.py \
        --Transformation TPS \
            --FeatureExtraction ResNet \
                --SequenceModeling BiLSTM \
                    --Prediction Attn \
                        --image_folder normal_cropped_img/ \
                            --saved_model TPS-ResNet-BiLSTM-Attn-case-sensitive.pth \
                                --sensitive''') 

# eng_digits()

def special_char():
    '''识别公差框、孔特征等'''
    os.system("D:/anaconda/envs/pytorch_/python.exe d:/vs_python_opencv_tesseract/package/special_char.py \
        --Transformation TPS \
            --FeatureExtraction ResNet \
                --SequenceModeling BiLSTM \
                    --Prediction CTC \
                        --image_folder special_cropped_img/ \
                            --saved_model self_trained_2.pth") 
# special_char()

def result_feedback(txt_name,img_name):
    '''把纵向检测的结果统一到横向图上'''
    h = get_h(img_name,rotate_path)
    f = open(txt_name,'r',encoding='utf-8')
    result_list = f.readlines()
    clean_list = []
    for i in range(len(result_list)):
        if result_list[i].split(',')[0][-1] == 'V':
            trans_v = (int(result_list[i].split('\'')[3]),h - int(result_list[i].split('\'')[5]),int(result_list[i].split('\'')[7]),h - int(result_list[i].split('\'')[1]),result_list[i].split('\t')[1])
            clean_list.append(trans_v)
        elif result_list[i].split(',')[0][-1] == 'H':
            clean_list.append((int(result_list[i].split('\'')[1]),int(result_list[i].split('\'')[3]),int(result_list[i].split('\'')[5]),int(result_list[i].split('\'')[7]),result_list[i].split('\t')[1]))
        else:
            pass
    return clean_list
    
def Visualization(result_list,img_name):
    img = cv2.imread(os.path.join(rotate_path,img_name))
    for i in result_list:
        cv2.rectangle(img,(i[0],i[1]),(i[2],i[3]),(0,0,255),1)
        cv2.putText(img,i[4],(i[0]-5,i[1]-5),cv2.FONT_ITALIC,0.5,(255,0,0),1)
    cv2.imshow('recg_result',img)
    cv2.waitKey(0)


def main(img_name, normal=True):
    h_90 = rotate(img_name,rotate_path)
    if normal: #英文和数字
        shutil.rmtree('./normal_cropped_img')
        os.mkdir('normal_cropped_img')
        detection(img_name,'./normal_cropped_img/') #生成裁剪后的文本截图
        eng_digits(img_name)
        clean_list = result_feedback('normal_result.txt',img_name)
        Visualization(clean_list,img_name)
        
    else: #特殊字符
        shutil.rmtree('./special_cropped_img')
        os.mkdir('special_cropped_img')
        detection(img_name,'./special_cropped_img/') #生成裁剪后的文本截图
        special_char()
        clean_list = result_feedback('special_result.txt',img_name)
        Visualization(clean_list,img_name)

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

list_pic = os.listdir('./original_rotate')
# print(list_pic)
if __name__ == '__main__':
    main(list_pic[0],False)
    shutil.rmtree('./original_rotate')
    os.mkdir('original_rotate')




