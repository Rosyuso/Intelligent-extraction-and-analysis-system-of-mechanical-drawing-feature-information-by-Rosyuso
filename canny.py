import cv2
import numpy as np

'''img = cv2.imread('crop_from_web/54.png',0)
img1 = cv2.GaussianBlur(img,(3,3),0)
canny = cv2.Canny(img1, 50, 150)

_,Thr_img = cv2.threshold(img1,210,255,cv2.THRESH_BINARY)#设定红色通道阈值210（阈值影响梯度运算效果）
kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(5,5))         #定义矩形结构元素
gradient = cv2.morphologyEx(Thr_img, cv2.MORPH_GRADIENT, kernel) #梯度

# window = cv2.namedWindow('test',cv2.WINDOW_NORMAL)
# cv2.imshow('test', canny)
# cv2.imshow("gradient", gradient) 
# cv2.waitKey(0)

 
def CannyThreshold(lowThreshold):
    detected_edges = cv2.GaussianBlur(gray,(3,3),0)
    detected_edges = cv2.Canny(detected_edges,
                               lowThreshold,
                               lowThreshold*ratio,
                               apertureSize = kernel_size)
    dst = cv2.bitwise_and(img,img,mask = detected_edges)  # just add some colours to edges from original image.
    cv2.imshow('canny demo',dst)

lowThreshold = 0
max_lowThreshold = 500
ratio = 3
kernel_size = 5
 
img = cv2.imread('crop_from_web/51.png')
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
 
cv2.namedWindow('canny demo',cv2.WINDOW_NORMAL)
 
cv2.createTrackbar('Min threshold','canny demo',lowThreshold, max_lowThreshold, CannyThreshold)
 
CannyThreshold(0)  # initialization
if cv2.waitKey(0) == 27:
    cv2.destroyAllWindows()
'''

# 形态学操作
# img = cv2.imread('shaft/52.png',0)
# kernel = np.ones((5, 5), np.uint8)
# erosion = cv2.erode(img, kernel)  # 腐蚀
# # window = cv2.namedWindow('thresh',cv2.WINDOW_NORMAL)
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
img_name = 'shaft/24.png'
img1 = cv2.imread(img_name, 0)

thresh = cv2.adaptiveThreshold(img1, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 7, 2)
cv2.imshow('1.thresh', thresh)
opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
opening = cv2.morphologyEx(closing, cv2.MORPH_OPEN, kernel)
# closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
# opening = cv2.morphologyEx(closing, cv2.MORPH_OPEN, kernel)
# closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
# opening = cv2.morphologyEx(closing, cv2.MORPH_OPEN, kernel)
# cv2.imshow('thresh',opening)
# cv2.waitKey(0)
cv2.imshow('2.opening', opening)

binartimg = cv2.Canny(opening, 1, 1000)
cv2.imshow('3.canny', binartimg)

h = cv2.findContours(binartimg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
print(len(h[0]))
contour = h[0]

small_area, middle_area = [], []
for i in range(len(contour)):
    area = cv2.contourArea(contour[i])
    print(area)
    if area <= 50:
        small_area.append(contour[i])
    elif 50 < area < 200:
        middle_area.append(contour[i])


# contour = [contour[i] for i in range(len(contour)) if (i in del_ind)]
# approx = cv2.approxPolyDP(contour[0],50,True)
# cv2.polylines(opening, [approx], True, (0, 0, 255), 2)

# print('middle_area', middle_area)
# 创建白色幕布
# temp = np.ones(binartimg.shape, np.uint8) * 255
# 画出轮廓：temp是白色幕布，contours是轮廓，-1表示全画，然后是颜色，厚度
# 分阶段画： 大轮廓用大厚度画，小轮廓用小厚度画
cv2.drawContours(opening, small_area, -1, (255, 255, 255), 5)
cv2.drawContours(opening, middle_area, -1, (255, 255, 255), 3)

# opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
opening = cv2.morphologyEx(closing, cv2.MORPH_OPEN, kernel)

cv2.imshow("4.contours", opening)
cv2.imwrite(img_name.split('.')[0] + 'cleansed.png', opening)
cv2.waitKey(0)
cv2.destroyAllWindows()

# for i in range(len())
