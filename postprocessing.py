import cv2
import sys
import numpy as np
import os 
import my_detector


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
    img=cv2.imread(os.path.join(rotate_path,img_name),1)
    img90=np.rot90(img,axes=(1,0))
    cv2.imwrite(os.path.join(rotate_path,img_name.split('.')[0] + '_90.png'), img90)

# rotate('test4.png','./original_rotate')


def detection(img_name,path):
    '''调用craft,返回整合好的横竖坐标列表,截取并保存每个坐标图'''
    img = cv2.imread(img_name)
    img_90 = cv2.imread(img_name.split('.')[0] + '_90.png')
    final_hori_block,final_vert_block = my_detector.block_clean(img_name,'res_' + img_name.split('.')[0]+'.txt','res_' + img_name.split('.')[0]+'_90.txt')
    # 形如：
    #      [['537', '24', '571', '59'], ['143', '95', '195', '128'], ['191', '271', '225', '304'],
    #     ['371', '271', '405', '304'], ['569', '271', '606', '304'], ['63', '399', '114', '434'], 
    #     ['807', '411', '843', '445'], ['960', '415', '984', '445'], ['1032', '594', '1065', '631'],
    #     ['828', '602', '875', '642'], ['807', '774', '843', '808'], ['1137', '22', '1187', '59'],
    #      ['625', '365', '699', '397'], ['774', '569', '862', '613'], ['575', '765', '654', '798']]
    for i in final_hori_block:
        # 对于每个坐标截图保存
        hcropped_coor_img = img[int(i[1]):int(i[3]),int(i[0]):int(i[2])]
        cv2.imwrite(path+'H,'+str(i)[1:-1]+'.png',hcropped_coor_img)
    for j in final_vert_block:
        # 对于每个坐标截图保存
        vcropped_coor_img = img_90[int(j[1]):int(j[3]),int(j[0]):int(j[2])]
        cv2.imwrite(path+'V,'+str(j)[1:-1]+'.png',vcropped_coor_img)

# detection('test4.png')

def eng_digits():
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
        --Transformation None \
            --FeatureExtraction ResNet \
                --SequenceModeling BiLSTM \
                    --Prediction CTC \
                        --image_folder special_cropped_img/ \
                            --saved_model self_trained.pth") 
# special_char()



def main(img_name, normal=True):
    if normal: #英文和数字
        img = cv2.imread(img_name)
        rotate(img_name,rotate_path) #生成旋转后的图
        detection(img_name,'./normal_cropped_img') #生成裁剪后的文本截图
    else: #特殊字符
        img = cv2.imread(img_name)
        rotate(img_name,rotate_path) #生成旋转后的图
        detection(img_name,'./special_cropped_img') #生成裁剪后的文本截图








# rotate('res_test4_90.jpg',path)

