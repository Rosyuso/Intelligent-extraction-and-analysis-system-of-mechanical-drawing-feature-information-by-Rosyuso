import cv2
import numpy as np
import random

def keystd(elem):
    return elem[0]


def get_corner(approx_list):
    Corner_list = [] 
    for i in range(len(approx_list)):
        # cv2.circle( x1 ,(new_contours[i][0][0],new_contours[i][0][1]) , 5 , (0, 255, 195), 5 )
        # cv2.circle( x1 ,(approx_list[i][0],approx_list[i][1]) , 3 , (0, 255, 195), 3 )
        Corner_list.append([approx[i][0][0],approx[i][0][1]])
#     if i % 8 == 0: #稀释坐标显示
#         cord=str( new_contours[i][0][0]) # + ',' + new_contours[i][0][1])
#         cv2.putText(x1, cord , (new_contours[i][0][0],new_contours[i][0][1]+32), cv2.FONT_HERSHEY_COMPLEX, 0.7, (85, 132, 159), 2 )
# test = approx[0][0]
# cv2.circle( x1 ,(test[0],test[1]) , 5 , (0, 255, 195), 5 )
# print(test)


def get_cleansed(img):
    kernel = np.ones((5, 5), np.uint8)
    erosion = cv2.erode(img, kernel)  # 腐蚀
    # window = cv2.namedWindow('thresh',cv2.WINDOW_NORMAL)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    # img_name = 'shaft/25.png'
    # img1 = cv2.imread(img_name,0)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,7,2)
    # cv2.imshow('1.thresh',thresh)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
    opening = cv2.morphologyEx(closing, cv2.MORPH_OPEN, kernel)
    binartimg = cv2.Canny(opening,100,500)
    h = cv2.findContours(binartimg,cv2.RETR_LIST ,cv2.CHAIN_APPROX_SIMPLE)
    contour = small_cont_filter(h[0]) # 滤除大轮廓，获取小轮廓
    cv2.drawContours(opening,contour,-1,(255,255,255),15) # 在图像去掉小轮廓
    return opening


def small_cont_filter(contour):
    del_ind = []
    small_area = []
    for i in range(len(contour)):
        area = cv2.contourArea(contour[i])
        if area <= 100:
            del_ind.append(i)
            small_area.append(contour[i])
    # print('太小的轮廓数量',len(del_ind))
    contour = [contour[i] for i in range(len(contour)) if (i in del_ind)] #只留小于一定值的轮廓
    return contour


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


def show_block(img, rect):
    '''画出检测到的矩形块'''
    for i in range(len(rect)):
        pt1 = (rect[i][0][0],min(rect[i][0][1],rect[i][1][1]))
        pt2 = (rect[i][2][0],max(rect[i][0][1],rect[i][1][1]))
        cv2.rectangle(img,pt1,pt2,(random.randint(0,255),random.randint(0,255),random.randint(0,255)),2)


def max_contour(contours):
    len_contours = [] 
    for i in contours:
        # print(len(i))
        len_contours.append(len(i))
    idx = len_contours.index(max(len_contours))  
    new_contours = contours[idx]
    return new_contours

def approax(contours, img):
    epsilon = 2
    approx = cv2.approxPolyDP(contours,epsilon,True) #approx返回的是以整个图最左上的角点开始的逆时针顺序的角点坐标:np数组形式
    approx_list = []
    for i in range(len(approx)):
        approx_list.append((approx[i][0][0],approx[i][0][1]))

    approx_list.sort(key=keystd,reverse=False)
    # print(approx_list)
    shaft_length = approx_list[-1][0] - approx_list[0][0] 
    # 自动识别轴长，如果图上没有标轴长，要求用户自己计算输入，因为比例尺是根据最左和最右的角点确定的
    cv2.polylines(img, [approx], True, (0, 0, 255), 4)
    return approx_list, shaft_length

# imgp = cv2.imread('shaft/32cleansed.png')

def split_rect(cleansed_img):
    cleansed_img = cv2.bitwise_not(cleansed_img)
    # img_gray = cv2.cvtColor(cleansed_img,cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(cleansed_img, 127, 255,0)
    h = cv2.findContours(thresh,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = max_contour(h[0]) 
    approx_list, shaft_length = approax(contours, cleansed_img)
    get_corner(approx_list)
    print(approx_list)
    # draw_corner(approx_list)
    # approx_list[23] = (465, 181)
    # approx_list[24] = (465, 352)
    approx_list = single_p_filter(approx_list)
    # print('new:',approx_list,len(approx_list))
    rect = rect_det(approx_list)
    show_block(cleansed_img,rect)
    print('检测到的矩形-->',rect)
    return rect, shaft_length



 
# 文本->  text
# ['34', '22', '59', '10', '28', '287', '180', '155', '3X∅12', '35', 'M16', '∅35k6', '∅35kh', '∅28', '∅28']

# 坐标->  coor
# [[106, 171, 146, 199], 
# [108, 370, 151, 401], 
# [148, 124, 191, 153], 
# [271, 370, 305, 399], 
# [332, 370, 374, 399], 
# [530, 28, 593, 57], 
# [718, 77, 774, 104], 
# [759, 124, 817, 153], 
# [955, 370, 1053, 401], 
# [975, 171, 1016, 200], 
# [1078, 308, 1107, 364], 
# [209, 223, 242, 330], 
# [550, 225, 582, 326], 
# [806, 245, 835, 308], 
# [10, 245, 37, 306]]

# 矩形阶梯截面-> rect
# [[(66, 226), (67, 323), (182, 325), (182, 224)], 
# [(183, 337), (184, 212), (268, 337), (268, 212)],
# [(270, 353), (270, 197), (437, 353), (438, 197)], 
# [(440, 337), (440, 212), (523, 212), (524, 337)], 
# [(525, 325), (526, 224), (936, 224), (937, 325)], 
# [(938, 298), (938, 252), (943, 299), (943, 251)], 
# [(944, 305), (944, 245), (1051, 305), (1056, 245)]]


def get_rect_info(rect):
    height, width, center = [], [], []
    for i in rect:
        if isinstance(rect[0][0], tuple):
            width.append(abs(i[0][0] - i[2][0]))
            height.append(abs(i[0][1] - i[1][1]))
            center.append((abs(i[0][0] + i[2][0]) / 2, abs(i[0][1] + i[1][1]) / 2))
        elif isinstance(rect[0][0], int):
            width.append(abs(i[2] - i[0]))
            height.append(abs(i[3] - i[1]))
            center.append((abs(i[0] + i[2]) / 2, abs(i[1] + i[3]) / 2))
    return height, width, center




def text_match_coor(coor, rect, text, shaft_length):
    height_r, width_r, center_r = get_rect_info(rect)
    height_t, width_t, center_t = get_rect_info(coor)
    print('rect-center->', center_r)
    print('rect-width->', width_r)
    print('rect-height->', height_r)
    print('coor-center->', center_t)
    print('text->', text)



## test----------------------------------------------------------------------------------------------------------------------

coor = [[106, 171, 146, 199], [108, 370, 151, 401], [148, 124, 191, 153], [271, 370, 305, 399], [332, 370, 374, 399], [530, 28, 593, 57], [718, 77, 774, 104], [759, 124, 817, 153], [955, 370, 1053, 401], [975, 171, 1016, 200], [1078, 308, 1107, 364], [209, 223, 242, 330], [550, 225, 582, 326], [806, 245, 835, 308], [10, 245, 37, 306]]
rect = [[(66, 226), (67, 323), (182, 325), (182, 224)], [(183, 337), (184, 212), (268, 337), (268, 212)], [(270, 353), (270, 197), (437, 353), (438, 197)], [(440, 337), (440, 212), (523, 212), (524, 337)], [(525, 325), (526, 224), (936, 224), (937, 325)], [(938, 298), (938, 252), (943, 299), (943, 251)], [(944, 305), (944, 245), (1051, 305), (1056, 245)]]
text = ['34', '22', '59', '10', '28', '287', '180', '155', '3X∅12', '35', 'M16', '∅35k6', '∅35kh', '∅28', '∅28']
shaft_length = 991
rect_width = [116, 85, 167, 83, 411, 5, 107]
rect_height = [97, 125, 156, 125, 101, 46, 60]
# text_match_coor(coor=coor, rect=rect, text=text, shaft_length=991)

# 去掉非数字尺寸，获取最大尺寸
max_num = 0
for i in text:
    if i.isdigit():
        # print(type(i))
        max_num = max(max_num, int(i))

print(max_num)

# 获取比例尺
ratio = shaft_length / max_num
rect_width = [format(i / ratio, '.1f') for i in rect_width]
rect_height = [format(i / ratio, '.1f') for i in rect_height]

# 将检测到的矩形阶梯等比转换成实际尺寸的结果：
# rect-width-> ['33.6', '24.6', '48.4', '24.0', '119.0', '1.4', '31.0']
# rect-height-> ['28.1', '36.2', '45.2', '36.2', '29.3', '13.3', '17.4']
print('rect-width->', rect_width)
print('rect-height->', rect_height)

# converted = 