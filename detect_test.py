import cv2
import os

def Visualization(result_list,img_name):
    img = cv2.imread(os.path.join(rotate_path,img_name))
    for i in result_list:
        cv2.rectangle(img,(int(i[0]),int(i[1])),(int(i[2]),int(i[3])),(0,0,255),1)
        # cv2.putText(img,i,(int(i[0])-5,int(i[1])-5),cv2.FONT_ITALIC,0.5,(255,0,0),1)   
    return img

rotate_path = './original_rotate'
re_list = ['528,30,564,30,564,58,528,58', '314,30,381,30,381,58,314,58', '306,72,512,72,512,102,306,102\n', '905,76,944,76,944,100,905,100\n', '1131,219,1159,219,1159,264,1131,264\n', '199,357,233,357,233,383,199,383\n', '968,357,1006,357,1006,383,968,383\n', '617,399,677,399,677,427,617,427\n']
img = Visualization(re_list,'17.png')
cv2.namedWindow('recg_result',cv2.WINDOW_NORMAL)
cv2.imshow('recg_result',img)
cv2.waitKey(0)
