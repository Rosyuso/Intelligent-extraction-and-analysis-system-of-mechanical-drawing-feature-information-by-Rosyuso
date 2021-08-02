import cv2
import numpy as np
import random

def keystd(elem):
    return elem[0]

def draw_corner(approx_list):
    for i in range(len(approx_list)):
        # cv2.circle( x1 ,(new_contours[i][0][0],new_contours[i][0][1]) , 5 , (0, 255, 195), 5 )
        cv2.circle( x1 ,(approx_list[i][0],approx_list[i][1]) , 3 , (0, 255, 195), 3 )
        Corner_list.append([approx[i][0][0],approx[i][0][1]])
#     if i % 8 == 0: #稀释坐标显示
#         cord=str( new_contours[i][0][0]) # + ',' + new_contours[i][0][1])
#         cv2.putText(x1, cord , (new_contours[i][0][0],new_contours[i][0][1]+32), cv2.FONT_HERSHEY_COMPLEX, 0.7, (85, 132, 159), 2 )
# test = approx[0][0]
# cv2.circle( x1 ,(test[0],test[1]) , 5 , (0, 255, 195), 5 )
# print(test)

def single_p_filter(approx_list):
    '''去除单个点（不成对的点）'''
    rm_idx = []
    for i in range(len(approx_list)-1):
        if i > 1 and abs(approx_list[i][0] - approx_list[i+1][0]) >= 10 and abs(approx_list[i][0] - approx_list[i-1][0]) >= 10:
            rm_idx.append(i)
    new_approx_list = [approx_list[i] for i in range(len(approx_list)) if (i not in rm_idx)]
    return new_approx_list


def rect_det(approx_list):
    rect = []
    for i in range(len(approx_list)-3):
        if abs(approx_list[i][0] - approx_list[i+1][0]) <= 5 and \
            abs(approx_list[i+2][0] - approx_list[i+3][0]) <= 5 and \
            abs(min(approx_list[i][1],approx_list[i+1][1]) - min(approx_list[i+2][1],approx_list[i+3][1])) <= 5 and  \
                abs(max(approx_list[i][1],approx_list[i+1][1]) - max(approx_list[i+2][1],approx_list[i+3][1])) <= 5:
                rect.append([j for j in approx_list[i:i+4]])
        # if 
    return rect 

def show_block(rect):
    '''画出检测到的矩形块'''
    for i in range(len(rect)):
        pt1 = (rect[i][0][0],min(rect[i][0][1],rect[i][1][1]))
        pt2 = (rect[i][2][0],max(rect[i][0][1],rect[i][1][1]))
        cv2.rectangle(imgp,pt1,pt2,(random.randint(0,255),random.randint(0,255),random.randint(0,255)),2)


img_name = 'shaft/46cleansed.png'
imgp = cv2.imread(img_name)
# img1 = cv2.imread()
img = cv2.bitwise_not(imgp)
img_gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
ret, thresh = cv2.threshold(img_gray, 127, 255,0)
h = cv2.findContours(thresh,cv2.RETR_EXTERNAL , cv2.CHAIN_APPROX_SIMPLE )
# print('lenh:',len(h))

# print('h:',h)

contours = h[0]
len_contours,contour_list = [], []
contour_info = []
for i in contours:
    x = sorted(i, key=lambda x:x[0][0], reverse=True)
    length = abs(x[0][0][0] - x[-1][-1][0]) # 每个contour的最大水平距离，最大的为主轮廓，小于10的可以删除了
    contour_info.append([length, len(i)])

# contour_info.sort(key=lambda x:x[0], reverse=True)
print(max(contour_info))

idx = contour_info.index(max(contour_info))
# idx = len_contours.index(53)  
# print('idx', idx)
new_contours = contours[idx]

x1 = img.copy()
epsilon = 2
approx = cv2.approxPolyDP(new_contours,epsilon,True)
#approx返回的是以整个图最左上的角点开始的逆时针顺序的角点坐标:np数组形式
approx_list = []
for i in range(len(approx)):
    approx_list.append((approx[i][0][0],approx[i][0][1]))

approx_list.sort(key=lambda x:(x[0], -x[1]),reverse=False)
print('approx_list - >',approx_list)
cv2.polylines(x1, [approx], True, (0, 0, 255), 4)
Corner_list = [] 

draw_corner(approx_list)
# approx_list[23] = (465, 181)
# approx_list[24] = (465, 352)
approx_list = single_p_filter(approx_list)
print('new:',approx_list,len(approx_list))
rect = rect_det(approx_list)
show_block(rect)
print('检测到的矩形-->',rect)


cv2.imshow('asdf',imgp)
cv2.imshow('sadf',x1)
cv2.imwrite('shaft/' + img_name.split('/')[1].split('.')[0] + '_block.png',imgp)

cv2.waitKey(0)
# print(Corner_list,len(Corner_list))
cv2.putText(x1, "epsilon: %d" % epsilon , (160,180), cv2.FONT_HERSHEY_COMPLEX, 1.0, (0, 0, 255), 2 )
cv2.imwrite( 'approxcurve2.jpg' , x1 ) 

