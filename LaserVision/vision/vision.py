import numpy as np
import math
import cv2
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from picamera import PiCamera
from time import sleep



        
       
            
def take_picture(nb_image):
    camera = PiCamera(resolution='1080p')
    camera.start_preview()
    for i in range(nb_image):
        camera.capture('picture/{n}.png'.format(n=i))
        sleep(0.25)
    
    camera.stop_preview()
    
def detect_circles():
    
    img = cv2.imread('picture/0.png')
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.medianBlur(gray, 25)
    minDist = 100
    param1 = 30 #500
    param2 = 50 #200 #smaller value-> more false circles
    minRadius = 5
    maxRadius = 100 #10

    # docstring of HoughCircles: HoughCircles(image, method, dp, minDist[, circles[, param1[, param2[, minRadius[, maxRadius]]]]]) -> circles
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, 1, minDist, param1=param1, param2=param2, minRadius=minRadius, maxRadius=maxRadius)
    if circles is not None:
        circles = np.uint16(np.around(circles))
        
        for i in circles[0,:]:
            circle_params= [i[0], i[1],i[2]]
            cv2.circle(img, (i[0], i[1]), i[2], (0, 255, 0), 2)
    # Show result for testing:
    cv2.imwrite("picture/circle.png", img)
    return circle_params

def get_vector(circle_params):
    circle_R = 18.3 #change the true circle radius here
    K = circle_R/circle_params[2]
    Ix = 540
    Iy = 960
    Dx = (circle_params[0]-Ix)*K
    Dy = (circle_params[1]-Iy)*K
    return Dx,Dy
    
def change_contrast(img):
    #g_kernel = cv2.getGaborKernel((21, 21), 8.0, np.pi/4, 10.0, 0.5, 0, ktype=cv2.CV_32F)
    #img = cv2.filter2D(img, cv2.CV_8UC3, g_kernel)
    image_enhanced = cv2.equalizeHist(img)
    return image_enhanced

def rotate_image(image, angle):
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result

def find_angle(image,n,gap,verbose=False,enhanced=True):
    angles_f =[]
    img_before = cv2.imread(image)
#     scale_percent = 100 # percent of original size
#     width = int(img_before.shape[1] * scale_percent / 100)
#     height = int(img_before.shape[0] * scale_percent / 100)
#     dim = (width, height)
#     img_before = cv2.resize(img_before, dim, interpolation = cv2.INTER_AREA)
    img_gray = cv2.cvtColor(img_before, cv2.COLOR_BGR2GRAY)
    if enhanced ==True:
        img_gray = change_contrast(img_gray)
    img_gray = cv2.GaussianBlur(img_gray, (5,5), 0)
    cv2.imwrite('edge/blur.png'.format(n=n),img_gray)
    
    tresh = np.linspace(50,150,30,dtype = int)
    tresholds = []
    for i in tresh:
        if i//3 < 30:
            tresholds.append((30,i))
        else:
            tresholds.append((i//3,i))
        
        
    for treshold in tresholds:
        
        img_edges = cv2.Canny(img_gray, treshold[0], treshold[1])
        if verbose:
            cv2.imwrite('edge/edge_{t1}_{t2}.png'.format(n=n,t1 = treshold[0],t2 =treshold[1] ), img_edges)  
        lines = cv2.HoughLinesP(img_edges, 1, np.pi/180.0, 100, minLineLength=50, maxLineGap=gap)
        angles = []
        
        try:
            for [[x1, y1, x2, y2]] in lines:
                cv2.line(img_before, (x1, y1), (x2, y2), (255, 0, 0), 3)
                angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
                angles.append(angle)
        except Exception as e:
            continue
        
        if verbose:
            cv2.imwrite('line/line_{t1}_{t2}.png'.format(n=n,t1 = treshold[0],t2 =treshold[1] ), img_before)

        median_angle = np.median(angles)
        angles_f.append(median_angle)
    return angles_f

def final_angles(angles):
    angles_neg=[]
    angles_pos=[]
    neg = 0
    pos = 0
    if len(angles)==0:
        return -1000
    for angle in angles:
        
        if angle < 0:
            neg+= 1
            angles_neg.append(angle)
        else:
            pos += 1
            angles_pos.append(angle)
    if neg> pos:
        median =np.median(angles_neg)
        for i in angles_neg:
            if np.abs(i-median)>3:
                angles_neg.remove(i)      
        median = np.median(angles_neg)
        if abs(median) > 45:
            median = (90+median)
    else:
        median = np.median(angles_pos)
        for i in angles_pos:
            if np.abs(i-median)>3:
                angles_pos.remove(i)
        median = np.mean(angles_pos)
        if abs(median) > 45:
            median = -(90-median)
    return median
def compute_angle(nb_image,gap=5,verbose=False):
    angles= []
    n = 0
    take_picture(nb_image)
    for i in range(nb_image):
        image = 'picture/{i}.png'.format(i=i)
        angles_find=find_angle(image,n,gap,verbose)
            
        final_angle_tmp = final_angles(angles_find)
        while final_angle_tmp  ==-1000:
            angles_find=find_angle(image,n,gap,verbose,True)
            final_angle_tmp = final_angles(angles_find)
        angles.append(final_angle_tmp)
        
    
    final_angle = np.median(angles)
    if final_angle != -1000:
        img_rotated = rotate_image(cv2.imread(image), final_angle)
        cv2.imwrite('picture/rotated.png'.format(n=n), img_rotated) 
    else:
        img_rotated = cv2.imread(image)
        cv2.imwrite('picture/rotated.png'.format(n=n), img_rotated)
    if verbose:
        img_base = mpimg.imread('picture/{n}.png'.format(n=n))
        img = mpimg.imread('picture/rotated.png')
        fig, axs = plt.subplots(1, 2, figsize=(18, 6), sharey=True)
        fig.suptitle('Rotate the image')
        axs[0].imshow(img_base)
        axs[1].imshow(img)
        axs[0].axis('off')
        axs[1].axis('off')
    return final_angle
    
    
                   
    return final_angle
import time
#stime = time.time()
circle_params = detect_circles()
Dx,Dy = get_vector(circle_params)
Dx = "{:.2f}".format(Dx)
Dy = "{:.2f}".format(Dy)
rot = compute_angle(1,5)
rot = "{:.2f}".format(rot)
print(Dx,Dy,rot)

#print(circle_params)
#print(time.time()-stime)