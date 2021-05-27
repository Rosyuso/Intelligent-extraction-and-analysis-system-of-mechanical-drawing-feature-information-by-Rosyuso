# -*- coding: utf-8 -*-
import shutil
import cv2 as cv
import os
import numpy as np
import random


'''
    opencv数据增强
    对图片进行色彩增强、高斯噪声、水平镜像、放大、旋转、剪切
    并对每张图片保存每一种数据增强的图片
'''
 
 
def contrast_brightness_image(src1, a, g, path_out):
    '''
        色彩增强（通过调节对比度和亮度）
    '''
    h, w, ch = src1.shape  # 获取shape的数值，height和width、通道
    # 新建全零图片数组src2,将height和width，类型设置为原图片的通道类型(色素全为零，输出为全黑图片)
    src2 = np.ones([h, w, ch], src1.dtype)
    # addWeighted函数说明:计算两个图像阵列的加权和
    dst = cv.addWeighted(src1, a, src2, 1 - a, g)
    cv.imwrite(path_out, dst)
 
 
def gasuss_noise(image, path_out_gasuss, mean=0, var=0.001):
    '''
        添加高斯噪声
        mean : 均值
        var : 方差
    '''
    image = np.array(image / 255, dtype=float)
    noise = np.random.normal(mean, var ** 0.5, image.shape)
    out = image + noise
    if out.min() < 0:
        low_clip = -1.
    else:
        low_clip = 0.
    out = np.clip(out, low_clip, 1.0)
    out = np.uint8(out * 255)
    cv.imwrite(path_out_gasuss, out)
 
 
def mirror(image, path_out_mirror):
    '''
        水平镜像
    '''
    h_flip = cv.flip(image, 1)
    cv.imwrite(path_out_mirror, h_flip)
 
 
def resize(image, path_out_large):
    '''
        放大两倍
    '''
    height, width = image.shape[:2]
    amp_num = 2*random.random()
    large = cv.resize(image, (int (amp_num* width),  int (amp_num* height)))
    cv.imwrite(path_out_large, large)
 
def SaltAndPepper(src,percetage,path_out_SaltAndPepper):
    '''
    椒盐噪声
    '''
    SP_NoiseImg=src.copy()
    SP_NoiseNum=int(percetage*src.shape[0]*src.shape[1]) 
    for i in range(SP_NoiseNum): 
        randR=np.random.randint(0,src.shape[0]-1) 
        randG=np.random.randint(0,src.shape[1]-1) 
        randB=np.random.randint(0,3)
        if np.random.randint(0,1)==0: 
            SP_NoiseImg[randR,randG,randB]=0 
        else: 
            SP_NoiseImg[randR,randG,randB]=255 
    cv.imwrite(path_out_SaltAndPepper, SP_NoiseImg)


def rotate(image, path_out_rotate):
    '''
        旋转
    '''
    rows, cols = image.shape[:2]
    M = cv.getRotationMatrix2D((cols / 2, rows / 2), random.randint(-8,8), 1)
    dst = cv.warpAffine(image, M, (cols, rows),borderValue=(255,255,255))
    cv.imwrite(path_out_rotate, dst)
 
 
def shear(image, path_out_shear):
    '''
        剪切
    '''
    height, width = image.shape[:2]
    i = random.randint(0,4)
    shear_percent = 10
    if i == 0: #剪切左上
        cropped = image[int(height /shear_percent):height, int(width /shear_percent):width]
    elif i == 1: #剪切右上
        cropped = image[int(height /shear_percent):height, 0:width - int(width /shear_percent)]
    elif i == 2: #剪切左下
        cropped = image[0:height - int(height /shear_percent), int(width /shear_percent):width]
    else: #剪切右下
        cropped = image[0:height - int(height /shear_percent), 0:width - int(width /shear_percent)]  
    cv.imwrite(path_out_shear, cropped)



image_path = 'D:/vs_python_opencv_tesseract/pics/validation0527'
image_out_path = 'D:/vs_python_opencv_tesseract/pics/data_augmentation'
if not os.path.exists(image_out_path):
    os.mkdir(image_out_path)
list = os.listdir(image_path) #读取文件夹下的所有文件存成列表
# print(list)
imageNameList = [
    '_color.png',
    '_gasuss.png',
    '_mirror.png',
    '_resize.png',
    '_rotate.png',
    '_shear.png',
    '_saltandpepper.png']
    
for i in range(0, len(list)):
    path = os.path.join(image_path, list[i])
    out_image_name = os.path.splitext(list[i])[0]
    print(out_image_name)
    for j in range(0, len(imageNameList)):
        path_out = os.path.join(image_out_path, out_image_name + imageNameList[j])
        image = cv.imread(path)
        if j == 0:
            contrast_brightness_image(image, 1.2,10, path_out)
        elif j == 1:
            gasuss_noise(image, path_out)
        # elif j == 2:
        #     mirror(image, path_out)
        # elif j == 3:
        #     resize(image, path_out)
        elif j == 4:
            rotate(image, path_out)
        elif j == 5:
            shear(image, path_out)
        elif j == 6:
            SaltAndPepper(image,random.random(),path_out)
        # else:
            # shutil.copy(path, path_out)
