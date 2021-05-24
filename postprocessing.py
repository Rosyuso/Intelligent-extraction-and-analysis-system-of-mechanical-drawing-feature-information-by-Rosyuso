import cv2
import sys
import easyocr
import numpy as np
import os 
import detector

crop_list = [] #鼠标截取的坐标，形如[[(x1,y1),(x2,y2)],[(x3,y3),(x4,y4)]...]
# img = cv2.imread('D:/vs_python_opencv_tesseract/package/figures/test4.png') #输入完整图纸

path ='./' #存放截图的文件夹
# print(os.path.realpath(__file__))
detect_folder = ''  #存放检测到文本截图的文件夹
result_txt = '' #存放识别结果的txt文件
# print(img.shape)
# cropped = img[100:500,400:500]
# cv2.imshow('cropped',cropped)
# cv2.waitKey(0)

def rotate(img_name,path):
    '''生成右旋90度的图片并保存'''
    img=cv2.imread(img_name,1)
    img90=np.rot90(img,axes=(1,0))
    cv2.imwrite(os.path.join(path,img_name.split('.')[0] + '_90.png'), img90)

# rotate('res_test4.jpg','./')


def detection(img_name):
    '''调用craft,返回整合好的横竖坐标列表,截取并保存每个坐标图'''
    # os.system("python D:/vs_python_opencv_tesseract/package/test.py") #python 后面需要接绝对路径，生成txt文件
    img = cv2.imread(img_name)
    img_90 = cv2.imread(img_name.split('.')[0] + '_90.png')
    final_hori_block,final_vert_block = detector.block_clean(img_name,img_name.split('.')[0]+'.txt',img_name.split('.')[0]+'_90.txt')
    final_hori_block,final_vert_block = detector.detection_postprocessing(final_hori_block,final_vert_block)
    # 形如：
    #      [['537', '24', '571', '59'], ['143', '95', '195', '128'], ['191', '271', '225', '304'],
    #     ['371', '271', '405', '304'], ['569', '271', '606', '304'], ['63', '399', '114', '434'], 
    #     ['807', '411', '843', '445'], ['960', '415', '984', '445'], ['1032', '594', '1065', '631'],
    #     ['828', '602', '875', '642'], ['807', '774', '843', '808'], ['1137', '22', '1187', '59'],
    #      ['625', '365', '699', '397'], ['774', '569', '862', '613'], ['575', '765', '654', '798']]
    for i in final_hori_block:
        # 对于每个坐标截图保存
        hcropped_coor_img = img[int(i[1]):int(i[3]),int(i[0]):int(i[2])]
        cv2.imwrite('./cropped/'+'H,'+str(i)[1:-1]+'.png',hcropped_coor_img)
    for j in final_vert_block:
        # 对于每个坐标截图保存
        vcropped_coor_img = img_90[int(j[1]):int(j[3]),int(j[0]):int(j[2])]
        cv2.imwrite('./cropped/'+'V,'+str(j)[1:-1]+'.png',vcropped_coor_img)

detection('res_test4.jpg')



# def eng_digits():
    # '''识别英文和数字'''
    # cropped_img = img[cc[0][1]:cc[1][1],cc[0][0]:cc[1][0]] #截取图片
    # reader = easyocr.Reader(['eng','la'])
    # result = reader.readtext(cropped_img,allowlist='0123456789RABCDEFGHIJKLMNOPQRSTUVWXYZ∅±.')
    # return result #


# rotate('res_test4_90.jpg',path)



# def special_char():
#     '''识别公差框、孔特征等'''