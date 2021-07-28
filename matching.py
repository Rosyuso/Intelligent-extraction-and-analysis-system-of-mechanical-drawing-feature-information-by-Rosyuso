import cv2
import numpy as np
import random

ctr_thre = 2 # 用于判断实际尺寸和矩形转换后的尺寸是否一致
rele_thre = 400  # 如果一个尺寸离矩形框过于远，则判定为不是该框的尺寸
aseb_thre_far = 500  # 用于确定距离相近但不等的情况,尽量取大一些
aseb_thre_near = 10  # 用于判断几个矩形的总长

def get_corner(approx_list):
    Corner_list = []
    for i in range(len(approx_list)):
        Corner_list.append([approx[i][0][0], approx[i][0][1]])


def get_cleansed(img):
    '''对图片进行处理：二值化、多次开闭操作、去除小于阈值的轮廓，留下主轮廓，返回处理后的图像'''
    # kernel = np.ones((5, 5), np.uint8)
    # erosion = cv2.erode(img, kernel)  # 腐蚀
    # window = cv2.namedWindow('thresh',cv2.WINDOW_NORMAL)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    # img_name = 'shaft/25.png'
    # img1 = cv2.imread(img_name,0)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 7, 2)
    # cv2.imshow('1.thresh',thresh)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
    opening = cv2.morphologyEx(closing, cv2.MORPH_OPEN, kernel)
    binartimg = cv2.Canny(opening, 100, 500)
    h = cv2.findContours(binartimg, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contour = small_cont_filter(h[0])  # 滤除大轮廓，获取小轮廓
    cv2.drawContours(opening, contour, -1, (255, 255, 255), 15)  # 在图像去掉小轮廓
    return opening


def small_cont_filter(contour):
    '''输入轮廓点集，得到小轮廓，返回小轮廓列表'''
    del_ind = []
    small_area = []
    for i in range(len(contour)):
        area = cv2.contourArea(contour[i])
        if area <= 100:
            del_ind.append(i)
            small_area.append(contour[i])
    # print('太小的轮廓数量',len(del_ind))
    contour = [contour[i] for i in range(len(contour)) if (i in del_ind)]  # 只留小于一定值的轮廓
    return contour


def single_p_filter(approx_list):
    """去除单个点（不成对的点），返回滤除后的点集"""
    rm_idx = []
    for i in range(len(approx_list) - 1):
        if i > 1 and abs(approx_list[i][0] - approx_list[i + 1][0]) >= 10 and abs(
                approx_list[i][0] - approx_list[i - 1][0]) >= 10:
            rm_idx.append(i)
    new_approx_list = [approx_list[i] for i in range(len(approx_list)) if (i not in rm_idx)]
    return new_approx_list


def rect_det(approx_list):
    """从拟合后的轮廓点集中提取矩形坐标，返回矩形坐标列表（四点）"""
    rect = []
    for i in range(len(approx_list) - 3):
        if abs(approx_list[i][0] - approx_list[i + 1][0]) <= 5 and \
                abs(approx_list[i + 2][0] - approx_list[i + 3][0]) <= 5 and \
                abs(min(approx_list[i][1], approx_list[i + 1][1]) - min(approx_list[i + 2][1],
                                                                        approx_list[i + 3][1])) <= 5 and \
                abs(max(approx_list[i][1], approx_list[i + 1][1]) - max(approx_list[i + 2][1],
                                                                        approx_list[i + 3][1])) <= 5:
            rect.append([j for j in approx_list[i:i + 4]])
        # if 
    return rect


def show_block(img, rect):
    '''画出检测到的矩形块'''
    for i in range(len(rect)):
        pt1 = (rect[i][0][0], min(rect[i][0][1], rect[i][1][1]))
        pt2 = (rect[i][2][0], max(rect[i][0][1], rect[i][1][1]))
        cv2.rectangle(img, pt1, pt2, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), 2)


def max_contour(contours):
    '''在检测到的多个轮廓中找到主轮廓（但不一定是点最多的，有待改进'''
    len_contours = []
    for i in contours:
        # print(len(i))
        len_contours.append(len(i))
    idx = len_contours.index(max(len_contours))
    new_contours = contours[idx]
    return new_contours


def approax(contours, img):
    '''外轮廓拟合，返回外轮廓的角点列表和最大轴长'''
    epsilon = 2
    approx = cv2.approxPolyDP(contours, epsilon, True)  # approx返回的是以整个图最左上的角点开始的逆时针顺序的角点坐标:np数组形式
    approx_list = []
    for i in range(len(approx)):
        approx_list.append((approx[i][0][0], approx[i][0][1]))

    approx_list.sort(key=lambda x:x[0], reverse=False)
    # print(approx_list)
    shaft_length = approx_list[-1][0] - approx_list[0][0]
    # 自动识别轴长，如果图上没有标轴长，要求用户自己计算输入，因为比例尺是根据最左和最右的角点确定的
    cv2.polylines(img, [approx], True, (0, 0, 255), 4)
    return approx_list, shaft_length


def split_rect(cleansed_img):
    """输入处理后的图片，输出矩形坐标列表和最大轴长"""
    cleansed_img = cv2.bitwise_not(cleansed_img)
    # img_gray = cv2.cvtColor(cleansed_img,cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(cleansed_img, 127, 255, 0)
    h = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = max_contour(h[0])
    approx_list, shaft_length = approax(contours, cleansed_img)
    # get_corner(approx_list)
    # print(approx_list)
    # draw_corner(approx_list)
    # approx_list[23] = (465, 181)
    # approx_list[24] = (465, 352)
    approx_list = single_p_filter(approx_list)
    # print('new:',approx_list,len(approx_list))
    rect = rect_det(approx_list)
    show_block(cleansed_img, rect)
    print('检测到的矩形-->', rect)
    return rect, shaft_length



def get_rect_info(rect):
    """输入坐标列表，输出每个元素的高度，宽度，中心坐标"""
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


def get_digits(s):
    """对于输入含有非数字的文本，判断尺寸类别，返回尺寸数值， 尺寸公差配合（没有为空）， 特征代号"""
    L = list(s)
    dms, tor = [], []
    for i in range(1,len(L)):
        if L[0] == '∅':
            if L[i].isdigit():
                dms.append(L[i])
            else:
                tor = L[i:]
                break
                # print('tor',tor)
        if L[0] == 'M':
            if L[i].isdigit():
                dms.append(L[i])
            else:
                tor = L[i:]
                break
                # print('tor',tor)

    return ''.join(dms), ''.join(tor), L[0]


def get_ratio(text, shaft_length):
    '''去掉非数字尺寸，获取最大尺寸,返回比例尺'''
    max_num = 0
    for i in text:
        if i.isdigit():
            # print(type(i))
            max_num = max(max_num, int(i))
    # 获取比例尺
    ratio = shaft_length / max_num
    return ratio



def coor_convert(coor, rect, text, shaft_length):
    '''输入文本坐标，矩形坐标，文本，轴长，输出矩阵信息（宽，高，（中心横坐标，中心纵坐标）），文本中心坐标，中心轴线纵坐标'''
    height_r, width_r, center_r = get_rect_info(rect)
    height_t, width_t, center_t = get_rect_info(coor)
    axis_r = int(np.mean(center_r, axis=0)[1]) # 中心轴线的纵坐标（矩形中心纵坐标的平均数）
    ratio = get_ratio(text, shaft_length)
    rect_width = [float(format(i / ratio, '.1f')) for i in width_r]
    rect_height = [float(format(i / ratio, '.1f')) for i in height_r]
    rect_info = list(zip(rect_width, rect_height, center_r))
    # 按照矩形中心横坐标从左到右排列
    rect_info.sort(key=lambda x: x[2][0])
    # print('rect_info', rect_info)
    # rect_info 中元素形如(33.6, 28.1, (124.0, 274.5))，
    # 其中前两项为矩形的宽和高，，第三项为中心坐标
    #
    # print('rect-center->', center_r)
    # print('rect-width->', width_r)
    # print('rect-height->', height_r)
    # print('coor-center->', center_t)
    # print('text->', text)
    # print('axis_r->', axis_r)
    return rect_info, center_t, axis_r


## test----------------------------------------------------------------------------------------------------------------------
#
# coor = [[106, 171, 146, 199], [108, 370, 151, 401], [148, 124, 191, 153], [271, 370, 305, 399], [332, 370, 374, 399],
#         [530, 28, 593, 57], [718, 77, 774, 104], [759, 124, 817, 153], [955, 370, 1053, 401], [975, 171, 1016, 200],
#         [1078, 308, 1107, 364], [209, 223, 242, 330], [550, 225, 582, 326], [806, 245, 835, 308], [10, 245, 37, 306]]
# rect = [[(66, 226), (67, 323), (182, 325), (182, 224)], [(183, 337), (184, 212), (268, 337), (268, 212)],
#         [(270, 353), (270, 197), (437, 353), (438, 197)], [(440, 337), (440, 212), (523, 212), (524, 337)],
#         [(525, 325), (526, 224), (936, 224), (937, 325)], [(938, 298), (938, 252), (943, 299), (943, 251)],
#         [(944, 305), (944, 245), (1051, 305), (1056, 245)]]
# text = ['34', '22', '59', '10', '28', '287', '180', '155', '3X∅12', '35', 'M16', '∅35k6', '∅35k6', '∅28', '∅28']
# shaft_length = 991
# coor_center = [(126.0, 185.0), (129.5, 385.5), (169.5, 138.5), (288.0, 384.5), (353.0, 384.5), (561.5, 42.5),
#                (746.0, 90.5), (788.0, 138.5), (1004.0, 385.5), (995.5, 185.5), (1092.5, 336.0), (225.5, 276.5),
#                (566.0, 275.5), (820.5, 276.5), (23.5, 275.5)]
# rect_info 中元素形如(33.6, 28.1, (124.0, 274.5))，
# 其中前两项为矩形的宽和高，，第三项为中心坐标
# 水平轴线
# rect_width = [116, 85, 167, 83, 411, 5, 107]
# rect_height = [97, 125, 156, 125, 101, 46, 60]
# rect_center = [(124.0, 274.5), (225.5, 274.5), (353.5, 275.0), (481.5, 274.5), (730.5, 274.5), (940.5, 275.0),
#                (997.5, 275.0)]
# rect-width-> ['33.6', '24.6', '48.4', '24.0', '119.0', '1.4', '31.0']
# rect-height-> ['28.1', '36.2', '45.2', '36.2', '29.3', '13.3', '17.4']


# text_match_coor(coor=coor, rect=rect, text=text, shaft_length=991)




#
# for i in rect_info:
#     print(i)
# print('rect_info', rect_info)
# 将检测到的矩形阶梯等比转换成实际尺寸的结果：
# rect-width-> ['33.6', '24.6', '48.4', '24.0', '119.0', '1.4', '31.0']
# rect-height-> ['28.1', '36.2', '45.2', '36.2', '29.3', '13.3', '17.4']
# print('rect-width->', rect_width)
# print('rect-height->', rect_height)

# converted =

'''
匹配规则：
1、 尺寸与转换后的矩形框，若两者中心接近且尺寸相配，则将该尺寸与矩形框匹配；
2、 当一个横向尺寸大于与其最近的矩形块长度时，从该矩形块开始向右右进行搜索，直至接近改尺寸，
    尺寸在矩形中心右边，向右添加矩形块，并计算矩形块总长，如果已经超过了尺寸还是没有匹配，break
    则搜索到的几个矩形块总长为该尺寸；
3、 


'''


# rect_info = [(33.6, 28.1, (124.0, 274.5)), (24.6, 36.2, (225.5, 274.5)), (48.4, 45.2, (353.5, 275.0)),
# (24.0, 36.2, (481.5, 274.5)), (119.0, 29.3, (730.5, 274.5)),
# (1.4, 13.3, (940.5, 275.0)), (31.0, 17.4, (997.5, 275.0))]


# axis_r = 274


def matching(rect_info, coor_center, text, axis_r):
    """矩形与尺寸文本匹配：输入【矩形信息， 文本坐标，文本， 轴线纵坐标】，输出【多矩形信息， 单矩形信息】 """
    multi_blocks, single_block = [], []  # 用于收集每个矩形的尺寸信息
    for i in range(len(rect_info)):  # i是矩形索引
        for j in range(len(coor_center)):  # j是尺寸索引
            if coor_center[j] == 'taken': continue

            # 水平向：[单个矩形长度] 找到中心接近且尺寸相配的
            if abs(rect_info[i][2][0] - coor_center[j][0]) <= ctr_thre and \
                    text[j].isdigit() and \
                    abs(rect_info[i][0] - int(text[j])) <= ctr_thre:
                if [i, 'W', int(text[j])] in single_block:
                    continue
                single_block.append([i, 'W', int(text[j])])
                print('匹配到结果--->   第{}个矩形宽度为:{}， \t\t\t尺寸:{}'.format(i + 1, rect_info[i][0], int(text[j])))
                coor_center[j] = 'taken'
            if coor_center[j] == 'taken':
                continue

            # 竖直向：[单个矩形高度] 找到中心接近且尺寸相配的,竖直一般都是直径，碰到直径符号删除后再比较
            elif abs(rect_info[i][2][1] - coor_center[j][1]) <= ctr_thre:  # 中心在同一条水平线上
                if coor_center[j] == 'taken':  continue
                if not text[j].isdigit() and \
                        abs(rect_info[i][1] - int(get_digits(text[j])[0])) <= ctr_thre and \
                        abs(rect_info[i][2][0] - coor_center[j][0]) <= rele_thre:  # 不是数字,删除特殊符号后再比较
                    # print('bingo')
                    # 存在问题： 只标记了用过的尺寸，并未标记用过的矩形，当碰到一模一样的尺寸时，还是会分配给同一个矩形，导致重复匹配。
                    # 解决： 判断一下在不在single_block里，在就跳过
                    if [i, 'H(∅)', int(get_digits(text[j])[0])] in single_block:
                        continue
                    single_block.append([i, 'H(∅)', int(get_digits(text[j])[0])])
                    print('匹配到结果--->   第{}个矩形高度为:{}， \t\t\t尺寸:{}{}\t配合:{}'.format(i + 1, rect_info[i][1],get_digits(text[j])[2],  get_digits(text[j])[0], get_digits(text[j])[1]))

                    coor_center[j] = 'taken'

            # 水平向： [多个矩形长度] 针对一条尺寸包括好几个矩形块的情况
            elif abs(axis_r - coor_center[j][1]) > 0.5 * rect_info[i][1]:  # 远离中心轴线的尺寸（在家），可以看作横向长度尺寸或退刀槽尺寸
                if coor_center[j] == 'taken': continue

                # 尺寸在矩形中心右边，向右添加矩形块，并计算矩形块总长，如果已经超过了尺寸还是没有匹配，则表明该尺寸不包含该块，继续向右遍历
                if text[j].isdigit() and \
                        0 < coor_center[j][0] - rect_info[i][2][0] <= aseb_thre_far and \
                        int(text[j]) > rect_info[i][0]:  # 尺寸为数字且大于矩形宽
                    length = rect_info[i][0]
                    for k in range(i + 1, len(rect_info)):
                        length += rect_info[k][0]
                        # 默认length 不可以超过尺寸， 超过就break
                        if length - int(text[j]) > aseb_thre_near:
                            break
                        if int(text[j]) - length <= aseb_thre_near:  # 说明已经加到了尺寸范围附近
                            # 从i到k即为该尺寸覆盖的矩形块
                            multi_blocks.append([i, k, length, int(text[j])])  # 结果存到列表里
                            print('匹配到结果--->   第{}到{}个矩形的总长度为:{}，\t尺寸:{}'.format(i + 1, k + 1, length, int(text[j])))

                # 文本->  text
                # ['34', '22', '59', '10', '28', '287', '180', '155', '3X∅12', '35', 'M16', '∅35k6', '∅35kh', '∅28', '∅28']
                # 除了位置固定的长宽以外，其余的包括退刀槽，螺纹等位置随机的尺寸
                # 退刀槽尺寸特点： 槽宽X槽深 或 槽宽X直径 形如3X∅12，或者无∅：6X3, 或者只有一个数字：
                # 槽宽一般小于10？ （暂定10
                if not text[j].isdigit() and text[j][0].isdigit() and 'X' in text[j] and '°' not in text[j]:  # 刨除倒角，螺纹，表示退刀槽,
                    if abs(int(text[j].split('X')[0]) - rect_info[i][0]) <= ctr_thre:
                        # 先处理 槽宽X直径 的形式，槽宽X槽深需要判断以更接近的基准
                        single_block.append([i, 'W(recess)', int(text[j].split('X')[0]), 'D(recess)', text[j].split('X')[1]])
                        print('匹配到结果--->   第{}个矩形的长度为:{}，\t\t\t尺寸:{}\t\t槽深/直径:{}'.format(i + 1, rect_info[i][0], int(text[j].split('X')[0]), text[j].split('X')[1]))

                # 螺纹同理
                # 螺纹特征代号 开头
                elif text[j][0] in ['M', 'G', 'Rc', 'Tr', 'B'] and abs(rect_info[i][1] - int(get_digits(text[j])[0])) <= ctr_thre:
                    single_block.append([i, 'H(M)', int(get_digits(text[j])[0]), 'M_info', get_digits(text[j])[1]])
                    print('匹配到结果--->   第{}个矩形的高度为:{}，\t\t尺寸:{}{}\t\t螺纹信息:{}'.format(i + 1, rect_info[i][1], get_digits(text[j])[2], int(get_digits(text[j])[0]), get_digits(text[j])[1]))

    return  multi_blocks, single_block


# rect_info, coor_center, axis_r = coor_convert(coor, rect, text, shaft_length)
# print(matching(rect_info, coor_center, text, axis_r))



