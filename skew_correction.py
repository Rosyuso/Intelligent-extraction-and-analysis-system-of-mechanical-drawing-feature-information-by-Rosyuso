import cv2
import numpy as np



'''
倾斜坐标定义： 四点无共享坐标
坐标形如：coor = [[50,50],[100,25],[150,75],[120,100]]
steps
1.因为已经获取到最小外接矩形（倾斜），直接获得倾斜角度；
2. 最小外接正矩形的img为[y1:y2,x1:x2] = 
3. 在最小正矩形上进行旋转，输出旋转后的图片
'''



def rotate_bound(image, angle):
    #获取宽高
    (h, w) = image.shape[:2]
    (cX, cY) = (w // 2, h // 2)
    # 提取旋转矩阵 sin cos
    M = cv2.getRotationMatrix2D((cX, cY), angle, 1.0)
    #cv2.getRotationMatrix2D()，这个函数需要三个参数，旋转中心，旋转角度(逆时针旋转），旋转后图像的缩放比例
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])
    print(cos,sin)
    # 计算图像的新边界尺寸
    nW = int((h * sin) + (w * cos))
    #nH = int((h * cos) + (w * sin))
    nH = h
    # 调整旋转矩阵
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY
    return cv2.warpAffine(image, M, (nW, nH),flags=cv2.INTER_CUBIC, borderValue=(255,255,255))
  

def angle_correction(rect):
    '''
    倾斜角度校正:https://blog.csdn.net/duiwangxiaomi/article/details/92565308
    旋转角度θ是水平轴（x轴）逆时针旋转，与碰到的矩形的第一条边的夹角。并且这个边的边长是width，
    另一条边边长是height。也就是说，在这里，width与height不是按照长短来定义的。
    四个顶点中y值最大的顶点为p[0]，p[0]围着center顺时针旋转，依次经过的顶点为p[1]，p[2]，p[3]
    先判断，如果width>height,则顺时针旋转angle；
    如果width<height，则逆时针旋转90-angle

    '''
    # if angle >= 45 and angle !=90:
    #     angle = angle - 90
    # elif angle == 90:
    #     angle = angle
    # else:
    #     angle = angle
    if rect[1][0] > rect[1][1]: #width>height
        angle = rect[-1]
    elif rect[1][0] < rect[1][1]:
        angle = -(90 - rect[-1])
    else:
        angle = rect[-1]
    return angle 


def get_rect_vert(img,test_coor):
    '''获得最小外接正矩形'''
    min_x = min(test_coor[0][0],test_coor[1][0],test_coor[2][0],test_coor[3][0])
    max_x = max(test_coor[0][0],test_coor[1][0],test_coor[2][0],test_coor[3][0])
    min_y = min(test_coor[0][1],test_coor[1][1],test_coor[2][1],test_coor[3][1])
    max_y = max(test_coor[0][1],test_coor[1][1],test_coor[2][1],test_coor[3][1])
    return img[min_y:max_y,min_x:max_x]


def skew_correction(img,test_coor):
    # test_coor = [[50,50],[100,25],[150,75],[120,100]]
    cnt = np.array(test_coor) # 必须是array数组的形式
    rect = cv2.minAreaRect(cnt) # 得到最小外接矩形的（中心(x,y), (宽,高), 旋转角度）
    img_vert = get_rect_vert(img,test_coor)
    if 90 - abs(rect[-1]) < 5 or abs(rect[-1]) < 5: #接近竖直的框不处理 或倾斜度较小的框不处理
        return False
    else:
        angle = angle_correction(rect)
        print(angle)
        print('width',rect[1][0])
        print('height',rect[1][1])
        result = rotate_bound(img_vert,angle)
        H,W = result.shape[:-1] 
        text_width = max(rect[1][0],rect[1][1])
        text_height = min(rect[1][0],rect[1][1])
        #把白边切割掉
        result = result[int(H/2 - text_height/2):int(H/2 + text_height/2),int(W/2 - text_width/2):int(W/2 + text_width/2)]
        return result

# print(rect,'-'*10,rect_nor)
# box = cv2.boxPoints(rect) # 获取最小外接矩形的4个顶点坐标(ps: cv2.boxPoints(rect) for OpenCV 3.x)
# box = np.int0(box)
# box_list = []
# for i in box:
#     box_list.append(list(i))
# print(box_list)
# 画出原图和最小外接矩形
# cv2.line(img,(50,50),(100,25),(0,255,0),5)
# cv2.line(img,(50,50),(120,100),(0,255,0),5)
# cv2.line(img,(100,25),(150,75),(0,255,0),5)
# cv2.line(img,(150,75),(120,100),(0,255,0),5)
# cv2.drawContours(img, [box], 0, (255, 0, 0),5)
# cv2.imwrite('1.png',img)
# rotated_img = rotate_bound(image, rect[-1])